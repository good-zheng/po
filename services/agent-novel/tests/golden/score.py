"""黄金集打分器：把确定性判据跑在 :mod:`.book` 的标注语料上（PRD §12.1）。

只打三面**可确定**的判据，这条边界是整个模块的前提：

1. **规则闸门**（正文侧 :func:`gates.run_rules` / 计划侧 :func:`gates.run_plan_rules`）
   ——语料里 ``detector="rule"`` 的标注应当被逐条查出，查不出即漏报；查出来的标注外
   记录即误报。语义裁判要调 LLM，CI 里不调，``detector="judge"`` 的标注因此只进
   覆盖台账（见 :data:`book.JUDGE_ONLY_CODES`）。
2. **逐字证据闸门**（:func:`graph.filter_extraction`）——证据不在正文里的候选必须整条
   丢弃，这是「误采 ≤ 10%」的唯一确定性测法。
3. **别名唯一约束**（``InMemoryCanonStore.append_assertions`` 复刻的
   ``(book, aliasText)`` 唯一索引）——重复登记与冲突登记都不许覆盖首次认定。

闸门输入一律由 :func:`context.compile_context` 现装配，不在语料里手写：注入视图与
闸门视图必须同源（同一份 snapshot / refs 编号），否则测的是「打分器自己拼的上下文」
而不是链路真正会看到的那一份。
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from po_agent_novel.context import compile_context
from po_agent_novel.gates import (
    Finding,
    GateInput,
    GateRules,
    PlanInput,
    run_plan_rules,
    run_rules,
)
from po_agent_novel.graph import bible_extraction, filter_extraction
from po_agent_novel.prompts import scene_card_text
from po_agent_novel.schemas import ChapterDraft, ChapterExtraction
from po_agent_novel.store import (
    CanonAssertion,
    ExtractionSource,
    InMemoryCanonStore,
    content_hash,
    pending_assertions,
)

from .book import (
    BIBLE,
    CHAPTERS,
    CONFLICT_CLASSES,
    IDEA,
    JUDGE_ONLY_CODES,
    OUTLINE,
    PLAN_CASES,
    RULES,
    SOFT_HIGH,
    SOFT_LOW,
    STYLE,
    ChapterCase,
    Mark,
    PlanCase,
)

# 计划侧走「已落库」的那条装配路径：回收编号必须来自真实的未收伏笔，
# 否则 payoff_decoy 那几张卡测的是库里根本不存在的坐标系。
BOOK_ID = "golden-1"


# ---------- 明细记录 ----------


@dataclass(frozen=True, slots=True)
class Miss:
    """一条该报而没报的标注（漏报）。"""

    side: str
    chapter: int
    cls: str
    code: str
    fragment: str
    severity: str


@dataclass(frozen=True, slots=True)
class FalsePositive:
    """一条标注之外的命中（误报）。"""

    side: str
    chapter: int
    code: str
    severity: str
    evidence: str
    explanation: str


@dataclass(frozen=True, slots=True)
class SeverityError:
    """报对了但严重度不对：同一处冲突走了另一条处置分支，也必须算账。"""

    side: str
    chapter: int
    code: str
    expected: str
    actual: str


@dataclass(slots=True)
class SideScore:
    """一面判据（正文闸门 / 计划闸门）的召回与误报。"""

    side: str
    expected: int = 0
    recalled: int = 0
    findings: int = 0
    blocker_expected: int = 0
    blocker_recalled: int = 0
    misses: list[Miss] = field(default_factory=list)
    false_positives: list[FalsePositive] = field(default_factory=list)
    decoy_hits: list[FalsePositive] = field(default_factory=list)
    severity_errors: list[SeverityError] = field(default_factory=list)
    #: 规则侧命中在「只有语义裁判能判」的标注片段上——覆盖台账，见模块 docstring
    judge_blind_spots: list[FalsePositive] = field(default_factory=list)
    by_class: dict[str, list[int]] = field(default_factory=dict)

    @property
    def recall(self) -> float:
        return self.recalled / self.expected if self.expected else 1.0

    @property
    def blocker_recall(self) -> float:
        return self.blocker_recalled / self.blocker_expected if self.blocker_expected else 1.0

    @property
    def fp_rate(self) -> float:
        return len(self.false_positives) / self.findings if self.findings else 0.0


@dataclass(slots=True)
class ExtractionScore:
    """抽取侧：逐字证据闸门的拦截率与新事实的入库率。"""

    candidates: int = 0
    verbatim: int = 0
    hallucinated: int = 0
    kept: int = 0
    blocked: int = 0
    registered: int = 0

    @property
    def recall(self) -> float:
        """逐字候选里真正落到正典库的比例（PRD 的「新事实召回」）。"""
        return self.registered / self.verbatim if self.verbatim else 1.0

    @property
    def false_capture_rate(self) -> float:
        """放行的候选里证据不在正文中的占比（PRD 的「误采」）。"""
        leaked = self.kept - self.verbatim
        return leaked / self.kept if self.kept else 0.0

    @property
    def block_rate(self) -> float:
        return self.blocked / self.hallucinated if self.hallucinated else 1.0


@dataclass(slots=True)
class AliasScore:
    """别名侧：唯一索引的处置是否与「首次认定优先」逐章一致。"""

    total: int = 0
    first_seen: int = 0
    repeat: int = 0
    conflicting: int = 0
    correct: int = 0
    mismatched_chapters: list[int] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 1.0


@dataclass(slots=True)
class GoldenReport:
    prose: SideScore
    plan: SideScore
    extraction: ExtractionScore
    aliases: AliasScore
    #: 每个 judge 编码在语料里的标注条数（覆盖台账）
    judge_labels: dict[str, int] = field(default_factory=dict)
    #: 实际注入过真实未收编号的 payoff_decoy 卡数（0 表示那几张反例是空跑）
    payoff_decoys_injected: int = 0
    words: dict[int, int] = field(default_factory=dict)

    @property
    def marks(self) -> int:
        return self.prose.expected + self.plan.expected

    @property
    def recall(self) -> float:
        total = self.prose.expected + self.plan.expected
        return (self.prose.recalled + self.plan.recalled) / total if total else 1.0

    @property
    def blocker_recall(self) -> float:
        total = self.prose.blocker_expected + self.plan.blocker_expected
        return (
            self.prose.blocker_recalled + self.plan.blocker_recalled
        ) / total if total else 1.0

    @property
    def fp_rate(self) -> float:
        findings = self.prose.findings + self.plan.findings
        fps = len(self.prose.false_positives) + len(self.plan.false_positives)
        return fps / findings if findings else 0.0

    def class_counts(self) -> dict[str, int]:
        """每类冲突的标注数（PRD §12.1 要求每类 8–15 处，用来证明覆盖不是空话）。"""
        counts: Counter[str] = Counter()
        for case in CHAPTERS:
            for mark in case.marks:
                counts[mark.cls] += 1
        for case in PLAN_CASES:
            for mark in case.marks:
                counts[mark.cls] += 1
        return {cls: counts[cls] for cls in CONFLICT_CLASSES}

    def diagnostics(self) -> str:
        """失败时打全量明细：定位一条漏报要把「标注说有什么」与「闸门报了什么」并排看。"""
        lines: list[str] = [
            f"正文闸门：召回 {self.prose.recalled}/{self.prose.expected}"
            f"（blocker {self.prose.blocker_recalled}/{self.prose.blocker_expected}）"
            f"，命中 {self.prose.findings} 条，误报 {len(self.prose.false_positives)} 条",
            f"计划闸门：召回 {self.plan.recalled}/{self.plan.expected}"
            f"（blocker {self.plan.blocker_recalled}/{self.plan.blocker_expected}）"
            f"，命中 {self.plan.findings} 条，误报 {len(self.plan.false_positives)} 条",
            f"抽取：候选 {self.extraction.candidates} 条（逐字 {self.extraction.verbatim} /"
            f" 幻觉 {self.extraction.hallucinated}，拦下 {self.extraction.blocked}）"
            f"，入库 {self.extraction.registered} 条",
            f"别名：共 {self.aliases.total} 条登记（首次 {self.aliases.first_seen} /"
            f" 重复 {self.aliases.repeat} / 冲突 {self.aliases.conflicting}）"
            f"，处置正确 {self.aliases.correct} 条，异常章 {self.aliases.mismatched_chapters}",
            f"分类标注数：{self.class_counts()}",
            f"分类召回：{ {side: dict(score.by_class) for side, score in (('prose', self.prose), ('plan', self.plan))} }",
        ]
        for miss in self.prose.misses + self.plan.misses:
            lines.append(
                f"漏报 [{miss.side}] 第 {miss.chapter} 章 {miss.cls} {miss.code}"
                f"（期望 {miss.severity}）← {miss.fragment!r}"
            )
        for fp in self.prose.false_positives + self.plan.false_positives:
            lines.append(
                f"误报 [{fp.side}] 第 {fp.chapter} 章 {fp.code}（{fp.severity}）"
                f"← {fp.evidence!r} / {fp.explanation}"
            )
        for error in self.prose.severity_errors + self.plan.severity_errors:
            lines.append(
                f"严重度不符 [{error.side}] 第 {error.chapter} 章 {error.code}："
                f"期望 {error.expected}，实得 {error.actual}"
            )
        for spot in self.prose.judge_blind_spots + self.plan.judge_blind_spots:
            lines.append(
                f"规则越界命中 judge 标注 [{spot.side}] 第 {spot.chapter} 章"
                f" {spot.code}←{spot.evidence!r}"
            )
        banded = [(no, words) for no, words in sorted(self.words.items()) if not _in_soft_band(words)]
        if banded:
            lines.append(f"越出软带 {SOFT_LOW}-{SOFT_HIGH} 的章：{banded}")
        return "\n".join(lines)


def _in_soft_band(words: int) -> bool:
    return SOFT_LOW <= words <= SOFT_HIGH


# ---------- 标注 ↔ Finding 的比对 ----------


def prose_matcher(fragment: str, finding: Finding) -> bool:
    """正文侧：标注片段与 Finding 证据同指一处。

    双向包含是有意的：规则 span 取「整句」，语料的一个 part 通常就是那一句，两边相等；
    但句末标点与相邻片段会让 span 比 part 略长或略短，严格要求相等只会把正确的召回
    数成漏报。空片段（整章级标注）只与「无 span 无证据」的 Finding 相配。
    """
    if fragment:
        return bool(finding.evidenceQuote) and (
            fragment in finding.evidenceQuote or finding.evidenceQuote in fragment
        )
    return finding.textStart is None and not finding.evidenceQuote


def plan_matcher(needle: str, finding: Finding) -> bool:
    """计划侧：needle 指在卡文本的整行证据里，或指在解释文案里（编号类两条都写）。"""
    if needle:
        return needle in finding.evidenceQuote or needle in finding.explanation
    return finding.textStart is None and not finding.evidenceQuote


def _consume(
    score: SideScore,
    chapter_no: int,
    marks: tuple[Mark, ...],
    findings: list[Finding],
    locate,
    matcher,
    decoys: tuple[str, ...],
) -> None:
    """把一章的标注与实得 Finding 对账（正文侧与计划侧共用同一份口径）。

    贪心配对按标注顺序取第一条合规 Finding：同一编码在同一章里命中多条时（视角漂移
    就是三条），配对结果与命中顺序无关，因为剩下的每条都要各自对上另一条标注，
    配错的那条会同时以「漏报 + 误报」两行出现在诊断里。
    """
    remaining = list(findings)
    score.findings += len(remaining)
    for mark in marks:
        if mark.detector != "rule":
            continue
        fragment = locate(mark)
        hit = next(
            (
                finding
                for finding in remaining
                if finding.code == mark.code and matcher(fragment, finding)
            ),
            None,
        )
        score.expected += 1
        row = score.by_class.setdefault(mark.cls, [0, 0])
        row[1] += 1
        if hit is None:
            score.misses.append(
                Miss(score.side, chapter_no, mark.cls, mark.code, fragment, mark.severity)
            )
            continue
        remaining.remove(hit)
        row[0] += 1
        score.recalled += 1
        if mark.severity == "blocker":
            score.blocker_expected += 1
            score.blocker_recalled += 1
        if mark.severity and hit.severity != mark.severity:
            score.severity_errors.append(
                SeverityError(score.side, chapter_no, mark.code, mark.severity, hit.severity)
            )
    for finding in remaining:
        record = FalsePositive(
            score.side,
            chapter_no,
            finding.code,
            finding.severity,
            finding.evidenceQuote,
            finding.explanation,
        )
        score.false_positives.append(record)
        if finding.evidenceQuote and any(
            finding.evidenceQuote in part or part in finding.evidenceQuote for part in decoys
        ):
            score.decoy_hits.append(record)
    for mark in marks:
        if mark.detector != "judge":
            continue
        fragment = locate(mark)
        for finding in findings:
            covered = finding.code in JUDGE_ONLY_CODES or (
                bool(fragment) and matcher(fragment, finding)
            )
            if covered:
                score.judge_blind_spots.append(
                    FalsePositive(
                        score.side,
                        chapter_no,
                        finding.code,
                        finding.severity,
                        finding.evidenceQuote,
                        finding.explanation,
                    )
                )


def _filtered(case: ChapterCase) -> ChapterExtraction | None:
    if case.extraction is None:
        return None
    filtered, _dropped = filter_extraction(case.extraction, case.text)
    return filtered


async def score_prose(
    rules: GateRules = RULES,
) -> tuple[SideScore, ExtractionScore, dict[int, int]]:
    """正文闸门 + 抽取侧：按链路真实顺序逐章装配、逐章对账。

    ``book_id=None`` 是有意的：黄金集测的是**一轮连续写作会话**（overlay 视图），不是
    已归档的书。这条路径同时把 §9.1 的「正文引用了未注入的 [fsh#N]」逼到最严的一端——
    会话内伏笔从未入库，任何伏笔编号都是凭空认领，必须报。
    """
    store = InMemoryCanonStore()
    world = pending_assertions("", 1, bible_extraction(BIBLE))
    overlay: list[CanonAssertion] = []
    aliases: dict[str, str] = {character.name: character.key for character in BIBLE.characters}
    drafts: list[ChapterDraft] = []
    score = SideScore(side="prose")
    extraction = ExtractionScore()
    words: dict[int, int] = {}
    for case in CHAPTERS:
        filtered = _filtered(case)
        compiled = await compile_context(
            store,
            book_id=None,
            idea=IDEA,
            outline=OUTLINE,
            index=case.no - 1,
            chapters=drafts,
            entities=None,
            world=world,
            overlay=tuple(overlay),
            style=STYLE,
        )
        gate_in = GateInput(
            text=case.text,
            chapter_no=case.no,
            extraction=filtered,
            snapshot=compiled.snapshot,
            refs=compiled.refs,
            known_aliases=aliases,
            style=compiled.style,
        )
        report = run_rules(gate_in, rules)
        words[case.no] = report.words
        _consume(
            score,
            case.no,
            case.marks,
            report.findings,
            case.locate,
            prose_matcher,
            tuple(case.parts[index] for index in case.decoys),
        )
        if filtered is None or case.extraction is None:
            continue
        kept = {(a.subjectKey, a.predicate, a.objectText) for a in filtered.assertions}
        for candidate in case.extraction.assertions:
            key = (candidate.subjectKey, candidate.predicate, candidate.objectText)
            verbatim = bool(candidate.evidenceQuote) and candidate.evidenceQuote in case.text
            extraction.candidates += 1
            extraction.verbatim += int(verbatim)
            extraction.hallucinated += int(not verbatim)
            extraction.kept += int(key in kept)
            extraction.blocked += int(not verbatim and key not in kept)
        overlay.extend(pending_assertions("", case.no, filtered))
        for alias in filtered.aliases:
            aliases.setdefault(alias.aliasText, alias.entityKey)
    return score, extraction, words


async def score_plan(
    rules: GateRules = RULES,
    extraction: ExtractionScore | None = None,
) -> tuple[SideScore, AliasScore, int]:
    """计划闸门 + 别名侧 + 入库核对：按「计划先于正文」的真实时序喂库。

    第 N 章的场景卡在第 N 章写作之前提交，所以库里只有 1..N-1 章的事实——与
    :func:`score_prose` 同一个 as-of 支点，两道闸门的召回才可以横向比。
    """
    store = InMemoryCanonStore()
    world = pending_assertions("", 1, bible_extraction(BIBLE))
    by_chapter: dict[int, PlanCase] = {case.no: case for case in PLAN_CASES}
    drafts: list[ChapterDraft] = []
    score = SideScore(side="plan")
    alias_score = AliasScore()
    injected = 0
    seen_alias: dict[str, str] = {}
    for chapter_no in range(1, len(CHAPTERS) + 1):
        prose = CHAPTERS[chapter_no - 1]
        plan_case = by_chapter.get(chapter_no)
        if plan_case is not None:
            compiled = await compile_context(
                store,
                book_id=BOOK_ID,
                idea=IDEA,
                outline=OUTLINE,
                index=chapter_no - 1,
                chapters=drafts,
                entities=None,
                world=world,
                style=STYLE,
            )
            card = plan_case.card
            if plan_case.payoff_decoy:
                open_numbers = [ref.number for ref in compiled.refs if ref.kind == "foreshadow"]
                if open_numbers:
                    card = card.model_copy(update={"payoffs": open_numbers[:1]})
                    injected += 1
            plan_in = PlanInput(
                card_text=scene_card_text(card, OUTLINE[chapter_no - 1]),
                card=card,
                chapter_no=chapter_no,
                snapshot=compiled.snapshot,
                refs=compiled.refs,
            )
            _consume(
                score,
                chapter_no,
                plan_case.marks,
                run_plan_rules(plan_in, rules).findings,
                plan_case.locate,
                plan_matcher,
                (),
            )
        drafts.append(ChapterDraft(index=prose.no, title=prose.title, content=prose.text))
        filtered = _filtered(prose)
        if filtered is None or prose.extraction is None:
            continue
        expected_skipped = 0
        for alias in filtered.aliases:
            alias_score.total += 1
            owner = seen_alias.get(alias.aliasText)
            if owner is None:
                seen_alias[alias.aliasText] = alias.entityKey
                alias_score.first_seen += 1
            elif owner == alias.entityKey:
                alias_score.repeat += 1
                expected_skipped += 1
            else:
                alias_score.conflicting += 1
                expected_skipped += 1
        outcome = await store.append_assertions(
            BOOK_ID,
            chapter_no,
            filtered,
            ExtractionSource(
                chapter_id=f"c{chapter_no}",
                content_hash=content_hash(prose.text),
                prompt_version="golden",
                model="golden",
            ),
        )
        # 唯一的 skipped 来源就是别名（重复或冲突），所以「本章别名条数 − 计数偏差」
        # 就是被正确处置的条数：偏差非零即库把该记的没记、或不该记的记了。
        delta = abs(outcome.skipped - expected_skipped)
        alias_score.correct += max(0, len(filtered.aliases) - delta)
        if delta:
            alias_score.mismatched_chapters.append(chapter_no)
        if extraction is not None:
            rows = await store.load_snapshot(BOOK_ID, as_of_chapter=chapter_no)
            landed = {(row.subject_key, row.predicate, row.object_text) for row in rows}
            for candidate in filtered.assertions:
                if candidate.evidenceQuote in prose.text:
                    extraction.registered += int(
                        (candidate.subjectKey, candidate.predicate, candidate.objectText) in landed
                    )
    return score, alias_score, injected


async def run_golden_set(rules: GateRules = RULES) -> GoldenReport:
    """跑完整套黄金集：三面判据一次算完，供阈值测试与覆盖台账测试共用。"""
    prose, extraction, words = await score_prose(rules)
    plan, aliases, injected = await score_plan(rules, extraction)
    judge_labels: Counter[str] = Counter()
    for case in CHAPTERS:
        for mark in case.judge_marks:
            judge_labels[mark.code] += 1
    return GoldenReport(
        prose=prose,
        plan=plan,
        extraction=extraction,
        aliases=aliases,
        judge_labels=dict(judge_labels),
        payoff_decoys_injected=injected,
        words=words,
    )


__all__ = [
    "AliasScore",
    "BOOK_ID",
    "ExtractionScore",
    "FalsePositive",
    "GoldenReport",
    "Miss",
    "SeverityError",
    "SideScore",
    "plan_matcher",
    "prose_matcher",
    "run_golden_set",
    "score_plan",
    "score_prose",
]
