"""一致性黄金集的语料本体：一部「带毒」的 20 章书（PRD §12.1）。

标注与正文共用同一份字面量：每条违规用 ``at=parts 下标`` 指认自己的逐字片段，
所以「标注说正文里写了什么」与「正文实际写了什么」不可能分家——改一句话即同时
改掉判据，不会出现语料漂移后闸门「召回率突然暴涨」那种自欺。

五处刻意的设计：

- **判定面只有规则引擎**：语料同时标注 ``detector="judge"`` 的语义违规（C4 时间线、
  C5 世界规则、C2 知情越界、C6 动机矛盾），但 CI 里裁判不调用——它们用来钉住
  「规则查不到」这条事实，一旦哪天补了规则，覆盖台账测试就会红，逼着重算基线；
- **禁用词故意荒诞**（手机 / 地铁 / 咖啡混进玄幻稿）：`check_forbidden_words` 判的是
  子串命中，语料要的可不是「像真小说」而是「命中位置唯一」，写得更像反而难标注；
- **每章的字数带是算出来的**：``RULES.target_words=160`` → 软带 96–256、硬带 56–352。
  只有四章故意越带（由 ``length_out_of_band`` 标注点名），其余章必须落在软带内，
  否则长度规则会污染误报率——填充句由 :func:`_pad` 补齐，不靠手数格子；
- **抽取候选里掺幻觉**：证据句不在本章正文里的候选即「误采」样本，逐字证据闸门
  必须整条丢弃（:mod:`.score` 按「证据是否在正文里」现场判定，不另立清单——
  另立清单就会和正文改版脱钩）；
- **死亡时间点决定谁是违规**：老周开篇即死（圣经），沐青死于第 5 章，沈槐死于第 6 章
  （第 6 章他那句遗言因此是**合法**写法，第 13 章同一句才是违规）。as-of 边界一旦改动，
  这两章的标注就会立刻对不上，这是本语料里最值钱的一处反例。
"""

from __future__ import annotations

from dataclasses import dataclass

from po_agent_novel.context import StyleContract
from po_agent_novel.gates import GateRules, visible_chars
from po_agent_novel.schemas import (
    AliasCandidate,
    AssertionCandidate,
    BookIdea,
    ChapterExtraction,
    ChapterOutline,
    ForeshadowPlantCandidate,
    PlannedScene,
    SceneCard,
    StateChangeCandidate,
    WorldBible,
    WorldCharacterEntry,
    WorldRelationEntry,
    WorldRuleEntry,
)

# ---------- 冲突类别（PRD §1.1 的 C1–C6） ----------

CONFLICT_CLASSES = ("C1", "C2", "C3", "C4", "C5", "C6")

# 只有语义裁判能判的编码：规则侧对它们**应当**零命中（覆盖台账测试钉这条）。
JUDGE_ONLY_CODES = frozenset(
    {
        "timeline_break",  # C4：区间越界没有写路径（PRD §15.6 #7）
        "world_rule_break",  # C5：规则需形式化，边界靠语义
        "knowledge_leak",  # C2：不在场者知道了只有在场者可能知道的信息
        "motivation_break",  # C6：情节与动机矛盾
    }
)


@dataclass(frozen=True)
class Mark:
    """一处已知违规。

    :param cls: C1–C6
    :param code: 期望的 ``FindingCode``
    :param at: 该违规所在的 ``parts`` 下标（正文语料＝逐字片段来源；计划语料＝
        ``needles`` 下标，见 :class:`PlanCase`）；``-1`` 表示整章级
        （没有片段可指：空章、字数越带、状态快照造成的复活、正文里没写过的称谓）
    :param detector: ``rule`` 应被规则引擎查出 / ``judge`` 只有语义裁判能查
    :param severity: 期望严重度，空串表示不限（同一规则按命中数分档时不锁死）
    """

    cls: str
    code: str
    at: int
    detector: str = "rule"
    severity: str = ""


@dataclass(frozen=True)
class ChapterCase:
    """一章：正文 + 本章的抽取候选 + 标注。"""

    no: int
    title: str
    summary: str
    parts: tuple[str, ...]
    marks: tuple[Mark, ...] = ()
    #: 刻意「看着像违规但不该报」的片段下标。打分时任何一条 Finding 的证据都不许
    #: 等于这些片段——比聚合误报率更严：一处反例恰好撞上别的标注时，聚合值照样好看。
    decoys: tuple[int, ...] = ()
    extraction: ChapterExtraction | None = None

    @property
    def text(self) -> str:
        return "".join(self.parts)

    def locate(self, mark: Mark) -> str:
        """标注 → 逐字片段（整章级标注返回空串）。"""
        return self.parts[mark.at] if mark.at >= 0 else ""

    @property
    def rule_marks(self) -> tuple[Mark, ...]:
        return tuple(mark for mark in self.marks if mark.detector == "rule")

    @property
    def judge_marks(self) -> tuple[Mark, ...]:
        return tuple(mark for mark in self.marks if mark.detector == "judge")


@dataclass(frozen=True)
class PlanCase:
    """计划侧一章的场景卡与标注（坐标系是 ``scene_card_text`` 的渲染）。

    计划文本的每一行都由模板生成，指认一条违规最稳的办法是给出**必须出现在该行里
    的片段**（实体键、``[fsh#N]``、字数带 ``400-600``），所以 ``needles`` 存的是子串
    而不是整行原文：模板改字时不必重抄标注，模板改**语义**时 needle 会找不到而报错。
    """

    no: int
    card: SceneCard
    needles: tuple[str, ...] = ()
    marks: tuple[Mark, ...] = ()
    #: True = 打分时把该章真实存在的未收伏笔编号注入 ``payoffs``，期望**零命中**
    payoff_decoy: bool = False

    def locate(self, mark: Mark) -> str:
        return self.needles[mark.at]


# ---------- 书级设定（等价于一次 worldbuild 的产出） ----------

IDEA = BookIdea(
    title="霜刃行",
    genre="玄幻",
    summary="守祠人死后，盲眼剑师的徒弟带着会灼伤活人的月火下山，在白渡口找回师父失踪那一夜的真相。",
)

BIBLE = WorldBible(
    logline="徒弟替死去的守祠人走完未竟的送信路，却发现月火才是杀师的那只手。",
    rules=[
        WorldRuleEntry(
            kind="world_rule",
            subjectKey="rule:moonlight_burns",
            predicate="harms",
            objectText="活人的皮肤",
            restatement="月火之下，活人裸露的皮肤会被灼伤",
            status="confirmed",
        ),
        WorldRuleEntry(
            kind="location",
            subjectKey="loc:tingxue",
            predicate="exists_at",
            objectText="北岭雪线之上",
            restatement="听雪楼坐落在北岭雪线之上",
            status="confirmed",
        ),
        WorldRuleEntry(
            kind="location",
            subjectKey="loc:baidukou",
            predicate="exists_at",
            objectText="听雪楼以南三百里",
            restatement="白渡口在听雪楼以南三百里",
            status="confirmed",
        ),
        WorldRuleEntry(
            kind="item",
            subjectKey="item:shuangren",
            predicate="blade_name",
            objectText="霜刃",
            restatement="那把剑的名字叫霜刃",
            status="confirmed",
        ),
        # 缺口（机制③）：作者还没定的设定，读侧不注入，也不许被闸门当成违规。
        WorldRuleEntry(
            kind="world_rule",
            subjectKey="rule:spirit_cost",
            predicate="cannot_use",
            objectText="灵力代价",
            restatement="动用灵力要付出什么代价尚未确定",
            status="todo",
        ),
    ],
    characters=[
        WorldCharacterEntry(
            key="char:linwan",
            name="林晚",
            role="主角",
            anchor="听雪楼唯一的徒弟，灰瞳黑发，左手持剑",
            alive=True,
        ),
        WorldCharacterEntry(
            key="char:shenhuai",
            name="沈槐",
            role="师父",
            anchor="听雪楼主，失踪于一夜风雪",
            alive=True,
        ),
        WorldCharacterEntry(
            key="char:agui",
            name="阿桂",
            role="同门",
            anchor="山下渡口人家的女儿，替楼里送柴",
            alive=True,
        ),
        WorldCharacterEntry(
            key="char:muqing",
            name="沐青",
            role="反派",
            anchor="三十年前离开听雪楼的大师兄",
            alive=True,
        ),
        WorldCharacterEntry(
            key="char:laozhou",
            name="老周",
            role="守祠人",
            anchor="山脚守祠四十年的哑巴老人",
            alive=False,
        ),
    ],
    relations=[
        WorldRelationEntry(
            fromKey="char:linwan",
            toKey="char:shenhuai",
            relation="师徒",
            restatement="林晚是沈槐唯一的徒弟",
        ),
        WorldRelationEntry(
            fromKey="char:muqing",
            toKey="char:shenhuai",
            relation="宿敌",
            restatement="沐青与沈槐三十年前决裂",
        ),
    ],
    pov="第三人称限知",
    tense="过去时",
    forbidden=["手机", "地铁", "咖啡"],
    openQuestions=["月火灼伤活人的原理未定", "灵力代价未定"],
)

STYLE = StyleContract(genre="玄幻", pov="第三人称限知", tense="过去时")

# 字数带按比值走：语料要的是「同一套判据」而不是「像真书」。
TARGET_WORDS = 160
RULES = GateRules(
    target_words=TARGET_WORDS,
    min_ratio=0.6,
    max_ratio=1.6,
    hard_min_ratio=0.35,
    hard_max_ratio=2.2,
    pov_major_hits=3,
    forbidden_words=tuple(BIBLE.forbidden),
    speech_window=12,
    per_code_limit=3,
)
SOFT_LOW = int(TARGET_WORDS * RULES.min_ratio)
SOFT_HIGH = int(TARGET_WORDS * RULES.max_ratio)
HARD_LOW = int(TARGET_WORDS * RULES.hard_min_ratio)
HARD_HIGH = int(TARGET_WORDS * RULES.hard_max_ratio)


# ---------- 逐字片段库 ----------
#
# 填充句的共同要求：不含人名、不含发言动词（_SPEECH_VERBS）、不含第一人称代词、
# 不含禁用词——否则「 padding 撑字数」会顺手造出一条 Finding。

PAD_A = "风从檐角卷下来，打着雪粒子敲窗纸，又顺着门槛退回去，屋里只剩灯芯烧动的细响。"
PAD_B = "她把手按在门框上站了一会儿，指腹摸见去年冬天留下的裂口。"
PAD_C = "雪光从瓦缝里漏进来，在地上拖出窄窄一片白。"
PAD_D = "柴堆旁的雪化了又冻，冻硬成一层薄冰，踩上去有细碎的响。"
PAD_E = "檐下冰棱滴了一夜水，石阶上洇开一小片深色。"
PAD_F = "她把剑横放在膝上，烛芯爆了一下，屋里更静。"
PAD_G = "门外雪压着枯枝，隔一阵就崩落一串细碎的响。"
PAD_H = "她数着火堆里的柴，数到第三十根时天就亮了。"

_PAD_BANK = (PAD_E, PAD_F, PAD_G, PAD_H, PAD_B, PAD_C, PAD_D, PAD_A)


def _pad(parts: tuple[str, ...], minimum: int) -> tuple[str, ...]:
    """追加填充句直到本章可见字数 ≥ ``minimum``。

    只往末尾加：标注用的是 ``parts`` 下标，前面那些片段的坐标因此不受影响。
    字数带是这套语料唯一「靠数格子维护」的判据，让代码来数就不存在数错的可能。
    """
    out = list(parts)
    index = 0
    while visible_chars("".join(out)) < minimum:
        out.append(_PAD_BANK[index % len(_PAD_BANK)])
        index += 1
        if index > 40:  # 预算兜底：填充无限循环说明 minimum 写错了
            raise ValueError(f"填充超过 40 句仍未达到 {minimum} 字")
    return tuple(out)


# C1 属性漂移：先立的规矩（证据即正文原句）。
S_EYE_GRAY = "她拂去肩上残雪，灰瞳映着灯芯那点红。"
S_HAIR_BLACK = "黑发垂到颊边，她没有去拢。"
S_HAND_LEFT = "她把左手按在剑柄上，指节一根一根收紧。"
S_SECT_TINGXUE = "她报上门派时只提两个字：听雪楼。"
S_ORIGIN_BAIDU = "她生在白渡口，会游泳的年纪比会走路还早。"
S_OWNER_LINWAN = "这把剑跟了林晚十年，鞘口的麻绳是她自己缠的。"

# C1 违规（与上面逐条相抵）
S_EYE_GOLD = "她拂去肩上残雪，金瞳映着灯芯那点红。"
S_EYE_GREEN = "她拂去肩上残雪，碧瞳映着灯芯那点红。"
S_EYE_RED = "她拂去肩上残雪，赤瞳映着灯芯那点红。"
S_HAIR_SILVER = "银发垂到颊边，她没有去拢。"
S_HAIR_BROWN = "棕发垂到颊边，她没有去拢。"
S_HAND_RIGHT = "她把右手按在剑柄上，指节一根一根收紧。"
S_OWNER_MUQING = "这把剑跟了沐青十年，鞘口的麻绳是她自己缠的。"
S_SECT_CHIYAN = "她报上门派时只提三个字：赤炎门。"
S_ORIGIN_HEYIN = "她生在河阴，会游泳的年纪比会走路还早。"
S_BLADE_NAME_XUEZHUI = "那把剑的名字是雪锥，剑脊上铸着两个旧字。"

# C2 生死：死者开口＝姓名与发言动词在窗口内同现。
S_DEAD_LAOZHOU = "老周说道，祠里的灯不许吹。"
S_DEAD_MUQING = "沐青笑道，三十年了你还记得那道疤。"
S_DEAD_MUQING_2 = "沐青问道，雪线上的风还是那么硬吗。"
S_DEAD_SHENHUAI = "沈槐叹了口气，说廊下的灯该换了。"
S_DEAD_SHENHUAI_2 = "沈槐答道，剑不用管，人先回去。"
S_ALIVE_NORMAL_DEATH = "沐青跪在雪里，天亮时人已经没了气息。"
S_ALIVE_ASSERT = "她把沐青的尸身背下山，一路上那人再没有喘过气。"
# 反例：只提死者、死者名下没有发言动词、发言留在引号里（旁人转述），都不算死者开口。
S_DEAD_MENTION = "她想起老周生前守的那盏灯，灯早灭了。"
S_DEAD_QUIET = "老周不应，只是把灯往她手里推了推。"
S_DEAD_IN_QUOTE = "「这话是老周说的，」阿桂学着他的腔调。"

# C3 称谓
S_ALIAS_SHENGGUNIANG = "沈姑娘接过柴捆，脸冻得通红。"
S_ALIAS_SHOUCIREN = "守祠人的牌位就立在第二进院子里。"

# C6 视角漂移（叙述层的「我」；引号内的不算）
S_EGO_1 = "我究竟该不该下山，她在雪里想了很久。"
S_EGO_2 = "俺这辈子没走过这么深的雪，她忽然想起这句话是谁讲的。"
S_EGO_3 = "咱听雪楼不欠人东西，她这样告诉自己。"
S_EGO_IN_QUOTE = "「我究竟该不该下山？」她低声问自己。"

# C6 引用编号（本会话未归档 → 库里没有未收伏笔，任何编号都是凭空认领）
S_FSH_999 = "她终于收回了那条伏笔，正如 [fsh#999] 所许。"
S_FSH_998 = "至于 [fsh#998]，早在这一剑里有了结局。"
S_CANON_77 = "她想起那条设定 [canon#77]，握紧了剑。"

# C6 禁用词
S_FORBID_PHONE = "她袖口里滑出一部手机，屏幕还亮着。"
S_FORBID_METRO = "白渡口没有船，她只好去坐地铁。"
S_FORBID_COFFEE = "她在雪线顶端煮了一壶咖啡，香气飘出很远。"
# 引号内的禁用词**仍然**算命中（平台红线不看谁说出口），所以它是标注而不是反例。
S_FORBID_IN_QUOTE = "「把你的手机收起来，」她沉声讲。"

# 语义裁判专属标注（规则侧应当零命中）
S_JUDGE_TIMELINE_1 = "她想起三天后发生的那场雪崩，心里一紧。"
S_JUDGE_TIMELINE_2 = "那件事要等到第八天，她却在此刻先哭了出来。"
S_JUDGE_TIMELINE_3 = "她记得师父死那年的春天，可师父此刻还活着。"
S_JUDGE_TIMELINE_4 = "渡船单程要十日，她讲三天后就能回来。"
S_JUDGE_TIMELINE_5 = "她按着去年腊月的雪，脚下却是六月。"
S_JUDGE_TIMELINE_6 = "那场比试结束后，她又想起了比试开始前的一句独白。"
S_JUDGE_TIMELINE_7 = "信在天亮前送到，而写信的人天亮后才动笔。"
S_JUDGE_TIMELINE_8 = "她认出了那个尚未出生的孩子。"
S_JUDGE_RULE_1 = "她在月下裸露着双臂，皮肤一点事也没有。"
S_JUDGE_RULE_2 = "月火照在阿桂脸上，她只觉有点凉。"
S_JUDGE_RULE_3 = "两人在月火下握手，谁也没有被灼伤。"
S_JUDGE_RULE_4 = "她把袖子挽到肘上，月火穿过袖口却未留下痕。"
S_JUDGE_RULE_5 = "守祠的夜里她裸臂取水，皮肉完好如初。"
S_JUDGE_RULE_6 = "月火之下，众人的手背都白净得反常。"
S_JUDGE_RULE_7 = "她在月光里睡了一整夜，醒来连红印都没有。"
S_JUDGE_RULE_8 = "月火落在柴堆上，柴没有烫，人也没有。"
S_JUDGE_KNOWS_1 = "阿桂说穿了那封只有林晚读过的信的内容。"
S_JUDGE_KNOWS_2 = "沐青清楚林晚昨夜独自去了地窖，可无人知晓。"
S_JUDGE_KNOWS_3 = "阿桂清楚那桩渡口旧案的每一处细节。"
S_JUDGE_KNOWS_4 = "一个已死之人向旁人复述了密谈的全部内容。"
S_JUDGE_KNOWS_5 = "林晚复述了只有掌门一人知晓的那句口诀。"
S_JUDGE_KNOWS_6 = "柴行的人清楚地了解楼内密室的布置。"
S_JUDGE_KNOWS_7 = "阿桂背出了那卷只在她手中展开过的账。"
S_JUDGE_KNOWS_8 = "路人精准地叫出了她隐匿多年的本名。"
S_JUDGE_MOTIVATION_1 = "她一路上都想杀那个人，此刻却毫无缘由地替他挡了一剑。"
S_JUDGE_MOTIVATION_2 = "她最爱那只猫，转手就把它扔进了井里。"
S_JUDGE_MOTIVATION_3 = "她从不说谎，这一段里她连撒了三个谎，却没有理由。"
S_JUDGE_MOTIVATION_4 = "她为救师父下山，走到门口却把门重新锁上。"
S_JUDGE_MOTIVATION_5 = "她怕火，却主动把袖子伸进炉膛，且不提为什么。"
S_JUDGE_MOTIVATION_6 = "她答应送柴到渡口，半路折回，此后再不提这件事。"
S_JUDGE_MOTIVATION_7 = "她恨了三十年的那个人，忽然被她说成此生最敬的人。"
S_JUDGE_MOTIVATION_8 = "她一心要隐瞒的事，进院后第一句就自己招了。"

# 可变谓词的正常改写（剧情推进，不是冲突）
S_MUTABLE_MOVE = "她此刻人在白渡口，靴子上还沾着北岭的雪。"
# 取值互为包含（「黑发」vs「她伸手摸了摸自己的黑发」不报）
S_HAIR_CONTAIN = "她伸手摸了摸自己的黑发，短发齐耳。"


def _cand(
    subject: str,
    predicate: str,
    value: str,
    evidence: str,
    *,
    kind: str = "character",
    status: str = "confirmed",
) -> AssertionCandidate:
    return AssertionCandidate(
        kind=kind,
        subjectKey=subject,
        predicate=predicate,
        objectText=value,
        restatement=f"{subject} · {predicate} = {value}",
        evidenceQuote=evidence,
        status=status,
    )


def _alias(key: str, text: str, *, primary: bool = False) -> AliasCandidate:
    return AliasCandidate(entityKey=key, aliasText=text, isPrimary=primary)


def _state(key: str, *, alive: bool | None = None) -> StateChangeCandidate:
    return StateChangeCandidate(charKey=key, isAlive=alive)


def _plant(content: str, *, due: int = 1) -> ForeshadowPlantCandidate:
    return ForeshadowPlantCandidate(content=content, dueByArc=due)


def _ex(
    assertions: tuple[AssertionCandidate, ...] = (),
    states: tuple[StateChangeCandidate, ...] = (),
    aliases: tuple[AliasCandidate, ...] = (),
    foreshadows: tuple[ForeshadowPlantCandidate, ...] = (),
) -> ChapterExtraction:
    return ChapterExtraction(
        assertions=list(assertions),
        stateChanges=list(states),
        aliases=list(aliases),
        foreshadows=list(foreshadows),
    )


def _card(
    entities: tuple[str, ...],
    scenes: tuple[tuple[str, str, tuple[str, ...]], ...],
    *,
    low: int = 120,
    high: int = 240,
    new: tuple[str, ...] = (),
    payoffs: tuple[int, ...] = (),
    hook: str = "章末留一句未答的话。",
) -> SceneCard:
    return SceneCard(
        entities=list(entities),
        newEntities=list(new),
        scenes=[
            PlannedScene(goal=goal, locationKey=location, present=list(present))
            for goal, location, present in scenes
        ],
        payoffs=list(payoffs),
        wordsLow=low,
        wordsHigh=high,
        hook=hook,
    )


# ---------- 二十章 ----------

CH1 = ChapterCase(
    no=1,
    title="守祠",
    summary="林晚在山脚祠里接过老周未点完的那盏灯。",
    parts=(
        S_EYE_GRAY,
        S_HAIR_BLACK,
        S_HAND_LEFT,
        S_SECT_TINGXUE,
        S_ORIGIN_BAIDU,
        S_DEAD_MENTION,
        S_JUDGE_MOTIVATION_2,
    ),
    # 死者被「提到」不是违规；本章同时把全书的不可变属性立起来（后面每一处 C1 都撞它）
    decoys=(5,),
    marks=(Mark("C6", "motivation_break", 6, detector="judge"),),
    extraction=_ex(
        assertions=(
            _cand("char:linwan", "eye_color", "灰瞳", S_EYE_GRAY),
            _cand("char:linwan", "hair_color", "黑发", S_HAIR_BLACK),
            _cand("char:linwan", "dominant_hand", "左手", S_HAND_LEFT),
            _cand("char:linwan", "sect", "听雪楼", S_SECT_TINGXUE),
            _cand("char:linwan", "origin", "白渡口", S_ORIGIN_BAIDU),
        ),
        aliases=(_alias("char:linwan", "林晚", primary=True),),
        foreshadows=(_plant("祠里那盏灯为什么不许吹灭"),),
    ),
)

CH2 = ChapterCase(
    no=2,
    title="借剑",
    summary="她下山去渡口借那把名为霜刃的旧剑。",
    parts=(
        PAD_C,
        S_OWNER_LINWAN,
        S_DEAD_LAOZHOU,
        S_FORBID_PHONE,
        S_JUDGE_KNOWS_5,
        PAD_B,
    ),
    marks=(
        Mark("C2", "death_speaks", 2, severity="blocker"),
        Mark("C6", "forbidden_word", 3, severity="blocker"),
        Mark("C2", "knowledge_leak", 4, detector="judge"),
    ),
    decoys=(1,),
    extraction=_ex(
        assertions=(
            _cand("item:shuangren", "owner", "林晚", S_OWNER_LINWAN, kind="item"),
            _cand("char:shenhuai", "mentor_of", "林晚", PAD_C),
        ),
        aliases=(_alias("char:shenhuai", "师父"),),
    ),
)

CH3 = ChapterCase(
    no=3,
    title="听雪",
    summary="她在楼里等到雪停，也等到一个不愿意听的消息。",
    parts=(
        S_EGO_1,
        PAD_A,
        S_EGO_IN_QUOTE,
        S_ALIVE_ASSERT,
        S_JUDGE_MOTIVATION_3,
        PAD_C,
    ),
    marks=(
        Mark("C6", "style_drift", 0, severity="minor"),
        Mark("C6", "motivation_break", 4, detector="judge"),
    ),
    decoys=(2, 3),
    extraction=_ex(
        assertions=(_cand("char:muqing", "threatens", "听雪楼", S_ALIVE_ASSERT),),
        foreshadows=(_plant("霜刃鞘内刻着一个不属于林晚的名字"),),
    ),
)

CH4 = ChapterCase(
    no=4,
    title="金瞳",
    summary="灯下有人看见她的眼睛换了颜色。",
    parts=(
        S_EYE_GOLD,
        PAD_B,
        S_SECT_TINGXUE,
        S_FORBID_METRO,
        S_JUDGE_KNOWS_6,
        PAD_C,
    ),
    marks=(
        Mark("C1", "attribute_conflict", 0, severity="blocker"),
        Mark("C6", "forbidden_word", 3, severity="blocker"),
        Mark("C2", "knowledge_leak", 4, detector="judge"),
    ),
    # 与既有值相同的重复叙述不是冲突（谓词比对只看候选，不看正文提了几次）
    decoys=(2,),
    extraction=_ex(
        assertions=(
            _cand("char:linwan", "eye_color", "金瞳", S_EYE_GOLD),
            # 幻觉候选：正文里没有这句证据，逐字闸门必须整条丢弃
            _cand("char:linwan", "scar_face", "左颊有刀疤", "她左颊有一道旧刀疤。"),
        ),
    ),
)

CH5 = ChapterCase(
    no=5,
    title="白发",
    summary="沐青死在山门外，雪盖住他半边衣角。",
    parts=_pad(
        (
            S_HAIR_SILVER,
            S_ALIVE_NORMAL_DEATH,
            S_JUDGE_RULE_1,
            S_JUDGE_MOTIVATION_4,
            PAD_A,
            PAD_B,
            PAD_C,
            PAD_D,
            S_DEAD_IN_QUOTE,
        ),
        SOFT_HIGH + 4,
    ),
    marks=(
        Mark("C1", "attribute_conflict", 0, severity="blocker"),
        Mark("C6", "length_out_of_band", -1, severity="minor"),
        Mark("C5", "world_rule_break", 2, detector="judge"),
        Mark("C6", "motivation_break", 3, detector="judge"),
    ),
    # 本章同时把沐青写死：死者被旁人转述（末句）不是违规
    decoys=(1, 8),
    extraction=_ex(
        assertions=(
            _cand("char:linwan", "hair_color", "银发", S_HAIR_SILVER),
            _cand("char:muqing", "is_alive", "false", S_ALIVE_NORMAL_DEATH),
        ),
        aliases=(
            _alias("char:agui", "阿桂", primary=True),
            _alias("char:muqing", "沐青", primary=True),
        ),
    ),
)

CH6 = ChapterCase(
    no=6,
    title="灯该换了",
    summary="师父留下最后一句话，那一夜他死在廊下。",
    parts=(
        S_DEAD_SHENHUAI,
        S_HAIR_SILVER,
        S_ORIGIN_BAIDU,
        S_JUDGE_TIMELINE_3,
        PAD_C,
        PAD_D,
    ),
    marks=(
        Mark("C1", "attribute_conflict", 1, severity="blocker"),
        Mark("C4", "timeline_break", 3, detector="judge"),
    ),
    # 本章末尾他才被登记为死亡：as-of 之前他活着，这句话因此是合法遗言。
    # 把 bible/前一章的死亡时间挪一格，这条反例立刻变成漏报——as-of 支点的活体检测。
    decoys=(0, 2),
    extraction=_ex(
        assertions=(
            _cand("char:linwan", "origin", "白渡口", S_ORIGIN_BAIDU),
            _cand("char:linwan", "hair_color", "银发", S_HAIR_SILVER),
            _cand("char:shenhuai", "is_alive", "false", S_DEAD_SHENHUAI),
        ),
    ),
)

CH7 = ChapterCase(
    no=7,
    title="右手",
    summary="她在渡口拔剑，剑却换了一只手。",
    parts=(
        S_HAND_RIGHT,
        S_DEAD_MUQING,
        S_JUDGE_RULE_2,
        S_MUTABLE_MOVE,
        S_JUDGE_KNOWS_7,
        PAD_A,
    ),
    marks=(
        Mark("C1", "attribute_conflict", 0, severity="blocker"),
        Mark("C2", "death_speaks", 1, severity="blocker"),
        Mark("C5", "world_rule_break", 2, detector="judge"),
        Mark("C2", "knowledge_leak", 4, detector="judge"),
    ),
    # location 是可变谓词：换了地方不叫属性漂移
    decoys=(3,),
    extraction=_ex(
        assertions=(
            _cand("char:linwan", "dominant_hand", "右手", S_HAND_RIGHT),
            _cand("char:linwan", "location", "白渡口", S_MUTABLE_MOVE),
            _cand("char:linwan", "scar_hand", "虎口有旧茧", "她握刀的虎口有一层旧茧。"),
        ),
    ),
)

CH8 = ChapterCase(
    no=8,
    title="送柴",
    summary="阿桂把柴送到第二进院子，顺手接过了她的剑。",
    parts=(
        S_DEAD_SHENHUAI_2,
        S_ALIAS_SHENGGUNIANG,
        S_FORBID_COFFEE,
        S_JUDGE_RULE_3,
        S_JUDGE_MOTIVATION_1,
        PAD_D,
    ),
    marks=(
        Mark("C2", "death_speaks", 0, severity="blocker"),
        Mark("C6", "forbidden_word", 2, severity="blocker"),
        Mark("C5", "world_rule_break", 3, detector="judge"),
        Mark("C6", "motivation_break", 4, detector="judge"),
    ),
    # 「沈姑娘」第一次登记：一个称谓一个实体，此刻没有漂移可比
    decoys=(1,),
    extraction=_ex(
        aliases=(_alias("char:agui", "沈姑娘"),),
        assertions=(_cand("char:agui", "delivers", "柴", S_ALIAS_SHENGGUNIANG),),
    ),
)

CH9 = ChapterCase(
    no=9,
    title="回光",
    summary="有人声称又在前坡看见了那个该死的人。",
    parts=_pad(
        (
            S_EYE_GRAY,
            S_JUDGE_TIMELINE_1,
            S_JUDGE_KNOWS_3,
            S_ALIVE_NORMAL_DEATH,
            PAD_A,
            PAD_B,
            PAD_C,
            PAD_D,
        ),
        HARD_HIGH + 8,
    ),
    marks=(
        # 沐青自第 5 章起是死人，本章候选又把他记回「在世」
        Mark("C2", "resurrection", 3, severity="blocker"),
        Mark("C6", "length_out_of_band", -1, severity="major"),
        Mark("C4", "timeline_break", 1, detector="judge"),
        Mark("C2", "knowledge_leak", 2, detector="judge"),
    ),
    # 与既有值相同的重复登记不是冲突
    decoys=(0,),
    extraction=_ex(
        assertions=(
            _cand("char:muqing", "is_alive", "在世", S_ALIVE_NORMAL_DEATH),
            _cand("char:linwan", "eye_color", "灰瞳", S_EYE_GRAY),
        ),
    ),
)

CH10 = ChapterCase(
    no=10,
    title="两个沈姑娘",
    summary="同一个称谓被叫到了两个人身上。",
    parts=(
        S_ALIAS_SHENGGUNIANG,
        S_OWNER_MUQING,
        S_JUDGE_RULE_4,
        S_JUDGE_MOTIVATION_5,
        PAD_D,
        PAD_C,
        PAD_A,
    ),
    marks=(
        Mark("C3", "alias_drift", 0, severity="major"),
        Mark("C1", "attribute_conflict", 1, severity="blocker"),
        Mark("C2", "resurrection", 0, severity="blocker"),
        Mark("C5", "world_rule_break", 2, detector="judge"),
        Mark("C6", "motivation_break", 3, detector="judge"),
    ),
    extraction=_ex(
        assertions=(
            _cand("item:shuangren", "owner", "沐青", S_OWNER_MUQING, kind="item"),
            _cand("char:laozhou", "is_alive", "活着", S_ALIAS_SHENGGUNIANG),
        ),
        aliases=(_alias("char:linwan", "沈姑娘"), _alias("char:laozhou", "守祠人")),
        # 状态快照里活人标活：不是复活
        states=(_state("char:agui", alive=True),),
    ),
)

CH11 = ChapterCase(
    no=11,
    title="碧瞳",
    summary="雪光里她的眼睛第三次变了颜色，而叙述开始换人。",
    parts=(
        S_EYE_GREEN,
        S_EGO_1,
        S_EGO_2,
        S_EGO_3,
        S_JUDGE_RULE_5,
        S_JUDGE_KNOWS_8,
        PAD_D,
    ),
    marks=(
        Mark("C1", "attribute_conflict", 0, severity="blocker"),
        Mark("C6", "style_drift", 1, severity="major"),
        Mark("C6", "style_drift", 2, severity="major"),
        Mark("C6", "style_drift", 3, severity="major"),
        Mark("C5", "world_rule_break", 4, detector="judge"),
        Mark("C2", "knowledge_leak", 5, detector="judge"),
    ),
    extraction=_ex(
        assertions=(
            _cand("char:linwan", "eye_color", "碧瞳", S_EYE_GREEN),
            # todo＝缺口登记，不许拿它去撞既有断言（机制③）
            _cand("char:agui", "age", "十六", PAD_D, status="todo"),
            _cand("char:agui", "saw_avalanche", "见过雪崩", "阿桂说自己十六岁那年见过雪崩。"),
        ),
    ),
)

CH12 = ChapterCase(
    no=12,
    title="赤炎门",
    summary="她报出一个从未存在过的门派。",
    parts=(
        S_ALIAS_SHOUCIREN,
        S_SECT_CHIYAN,
        S_DEAD_MUQING_2,
        S_FORBID_IN_QUOTE,
        S_JUDGE_TIMELINE_5,
        S_JUDGE_KNOWS_4,
        PAD_B,
        PAD_D,
    ),
    marks=(
        Mark("C1", "attribute_conflict", 1, severity="blocker"),
        Mark("C2", "death_speaks", 2, severity="blocker"),
        # 整章级：本章结束时的状态快照把死人又标成活人，没有片段可指
        Mark("C2", "resurrection", -1, severity="blocker"),
        Mark("C6", "forbidden_word", 3, severity="blocker"),
        Mark("C4", "timeline_break", 4, detector="judge"),
        Mark("C2", "knowledge_leak", 5, detector="judge"),
    ),
    # 死者别名「守祠人」出现在没有发言动词的一句里
    decoys=(0,),
    extraction=_ex(
        assertions=(_cand("char:linwan", "sect", "赤炎门", S_SECT_CHIYAN),),
        states=(_state("char:muqing", alive=True),),
    ),
)

CH13 = ChapterCase(
    no=13,
    title="短句",
    summary="这一章只有三句话，字数越出软带下沿。",
    parts=(PAD_A, S_EYE_GRAY, S_DEAD_SHENHUAI),
    marks=(
        Mark("C2", "death_speaks", 2, severity="blocker"),
        # 整章级：本章把「沈姑娘」指给了第三个人，可正文里根本没出现过这个称谓
        Mark("C3", "alias_drift", -1, severity="major"),
        Mark("C6", "length_out_of_band", -1, severity="minor"),
    ),
    decoys=(1,),
    extraction=_ex(
        assertions=(_cand("char:linwan", "eye_color", "灰瞳", S_EYE_GRAY),),
        aliases=(_alias("char:shenhuai", "沈姑娘"),),
    ),
)

CH14 = ChapterCase(
    no=14,
    title="河阴",
    summary="她的出身被换到了一条不存在的河。",
    parts=(
        S_ORIGIN_HEYIN,
        S_CANON_77,
        S_JUDGE_TIMELINE_2,
        S_JUDGE_MOTIVATION_8,
        S_JUDGE_RULE_6,
        S_JUDGE_TIMELINE_4,
        PAD_C,
        PAD_D,
    ),
    marks=(
        Mark("C1", "attribute_conflict", 0, severity="blocker"),
        Mark("C6", "unknown_ref", 1, severity="major"),
        Mark("C4", "timeline_break", 2, detector="judge"),
        Mark("C6", "motivation_break", 3, detector="judge"),
        Mark("C5", "world_rule_break", 4, detector="judge"),
        Mark("C4", "timeline_break", 5, detector="judge"),
    ),
    extraction=_ex(
        assertions=(
            _cand("char:linwan", "origin", "河阴", S_ORIGIN_HEYIN),
            _cand("item:shuangren", "forged_at", "河阴", "这把剑是在河阴铸成的。", kind="item"),
        ),
    ),
)

CH15 = ChapterCase(
    no=15,
    title="抽不出的一章",
    summary="这一章的抽取整体失败，正文侧的规则照常要跑。",
    parts=(
        S_DEAD_LAOZHOU,
        S_DEAD_QUIET,
        S_JUDGE_KNOWS_1,
        PAD_D,
        PAD_A,
        PAD_E,
    ),
    marks=(
        Mark("C2", "death_speaks", 0, severity="blocker"),
        Mark("C2", "knowledge_leak", 2, detector="judge"),
    ),
    # 死者名下没有发言动词
    decoys=(1,),
    extraction=None,
)

CH16 = ChapterCase(
    no=16,
    title="雪锥",
    summary="剑名被改写，师父也被写活。",
    parts=_pad(
        (
            S_BLADE_NAME_XUEZHUI,
            S_JUDGE_RULE_1,
            S_JUDGE_TIMELINE_6,
            S_HAIR_CONTAIN,
            S_JUDGE_MOTIVATION_6,
        ),
        SOFT_LOW + 4,
    ),
    marks=(
        # 同一片段两条标注：attribute_conflict 撞圣经的 blade_name，resurrection 撞第 6 章的死
        Mark("C1", "attribute_conflict", 0, severity="blocker"),
        Mark("C2", "resurrection", 0, severity="blocker"),
        Mark("C5", "world_rule_break", 1, detector="judge"),
        Mark("C4", "timeline_break", 2, detector="judge"),
        Mark("C6", "motivation_break", 4, detector="judge"),
    ),
    # 「黑发」与「她摸了摸自己的黑发」互为包含，不报
    decoys=(3,),
    extraction=_ex(
        assertions=(
            _cand(
                "item:shuangren",
                "blade_name",
                "雪锥",
                S_BLADE_NAME_XUEZHUI,
                kind="item",
            ),
            _cand("char:shenhuai", "is_alive", "活着", S_BLADE_NAME_XUEZHUI),
            _cand("char:linwan", "hair_color", "黑发", S_HAIR_CONTAIN),
        ),
    ),
)

CH17 = ChapterCase(
    no=17,
    title="空章",
    summary="这一章一个字都没有，是唯一的空章 blocker。",
    parts=(),
    marks=(
        Mark("C6", "length_out_of_band", -1, severity="blocker"),
        Mark("C3", "alias_drift", -1, severity="major"),
    ),
    extraction=_ex(aliases=(_alias("char:shenhuai", "守祠人"),)),
)

CH18 = ChapterCase(
    no=18,
    title="棕发",
    summary="第三次换发色，动机也第一次无缘由地掉头。",
    parts=_pad(
        (
            S_HAIR_BROWN,
            S_JUDGE_MOTIVATION_7,
            S_JUDGE_TIMELINE_7,
            S_JUDGE_RULE_7,
        ),
        SOFT_LOW + 6,
    ),
    marks=(
        Mark("C1", "attribute_conflict", 0, severity="blocker"),
        Mark("C6", "motivation_break", 1, detector="judge"),
        Mark("C4", "timeline_break", 2, detector="judge"),
        Mark("C5", "world_rule_break", 3, detector="judge"),
    ),
    extraction=_ex(
        assertions=(
            _cand("char:linwan", "hair_color", "棕发", S_HAIR_BROWN),
            # mood 是可变谓词：情绪换了不是属性漂移
            _cand("char:agui", "mood", "惶恐", PAD_F),
        ),
    ),
)

CH19 = ChapterCase(
    no=19,
    title="赤瞳",
    summary="第四次换瞳色，死人也第五次开口。",
    parts=(
        S_EYE_RED,
        S_DEAD_MUQING_2,
        S_EGO_1,
        S_EGO_2,
        S_EGO_3,
        S_FSH_999,
        S_JUDGE_RULE_8,
        S_JUDGE_KNOWS_2,
        PAD_D,
    ),
    marks=(
        Mark("C1", "attribute_conflict", 0, severity="blocker"),
        Mark("C2", "death_speaks", 1, severity="blocker"),
        Mark("C6", "style_drift", 2, severity="major"),
        Mark("C6", "style_drift", 3, severity="major"),
        Mark("C6", "style_drift", 4, severity="major"),
        # 本会话的伏笔从没入库 → 任何 [fsh#N] 都是凭空认领
        Mark("C6", "foreshadow_missing", 5, severity="blocker"),
        Mark("C5", "world_rule_break", 6, detector="judge"),
        Mark("C2", "knowledge_leak", 7, detector="judge"),
    ),
    extraction=_ex(
        assertions=(
            _cand("char:linwan", "eye_color", "赤瞳", S_EYE_RED),
            _cand("char:linwan", "eye_rule", "灰瞳是月火的印记", "灰瞳是月火留下的印记。"),
        ),
    ),
)

CH20 = ChapterCase(
    no=20,
    title="收线",
    summary="她收了一条没有埋过的线，也把出身换了一次。",
    parts=(
        S_FSH_998,
        S_ORIGIN_HEYIN,
        S_JUDGE_TIMELINE_8,
        PAD_A,
        PAD_B,
        PAD_G,
        PAD_H,
    ),
    marks=(
        Mark("C6", "foreshadow_missing", 0, severity="blocker"),
        Mark("C1", "attribute_conflict", 1, severity="blocker"),
        Mark("C4", "timeline_break", 2, detector="judge"),
    ),
    decoys=(3, 4, 5, 6),
    extraction=_ex(
        assertions=(_cand("char:linwan", "origin", "河阴", S_ORIGIN_HEYIN),),
    ),
)

CHAPTERS: tuple[ChapterCase, ...] = (
    CH1,
    CH2,
    CH3,
    CH4,
    CH5,
    CH6,
    CH7,
    CH8,
    CH9,
    CH10,
    CH11,
    CH12,
    CH13,
    CH14,
    CH15,
    CH16,
    CH17,
    CH18,
    CH19,
    CH20,
)

OUTLINE: tuple[ChapterOutline, ...] = tuple(
    ChapterOutline(title=case.title, summary=case.summary) for case in CHAPTERS
)

# 抽取失败的那一章：正文侧规则要照常跑，候选侧规则（属性冲突 / 复活）整体跳过。
EXTRACTION_FAILED_CHAPTERS = frozenset({case.no for case in CHAPTERS if case.extraction is None})


def _needle(*needles: str) -> tuple[str, ...]:
    return needles


# ---------- 计划侧语料（坐标系 = prompts.scene_card_text 的渲染） ----------

PLAN_CASES: tuple[PlanCase, ...] = (
    # ---- C3 计划侧：场景用到了一条已登记事实都指不出的实体（major） ----
    PlanCase(
        2,
        _card(
            ("char:linwan", "char:ghost"),
            (("渡口问路", "loc:baidukou", ("char:linwan",)),),
        ),
        needles=_needle("char:ghost"),
        marks=(Mark("C3", "unregistered_entity", 0, severity="major"),),
    ),
    PlanCase(
        8,
        _card(
            ("char:linwan", "char:agui"),
            (("送柴", "loc:ferry", ("char:agui",)),),
        ),
        needles=_needle("loc:ferry"),
        marks=(Mark("C3", "unregistered_entity", 0, severity="major"),),
    ),
    PlanCase(
        11,
        _card(
            ("char:linwan", "char:ninegong"),
            (("雪夜", "loc:tingxue", ("char:linwan",)),),
        ),
        needles=_needle("char:ninegong"),
        marks=(Mark("C3", "unregistered_entity", 0, severity="major"),),
    ),
    PlanCase(
        17,
        _card(
            ("char:linwan", "char:xueyuan"),
            (("雪院", "loc:heying", ("char:xueyuan",)),),
        ),
        needles=_needle("char:xueyuan", "loc:heying"),
        marks=(
            Mark("C3", "unregistered_entity", 0, severity="major"),
            Mark("C3", "unregistered_entity", 1, severity="major"),
        ),
    ),
    PlanCase(
        19,
        _card(
            ("char:linwan", "char:huizhu"),
            (("会主", "loc:tingxue", ("char:huizhu",)),),
        ),
        needles=_needle("char:huizhu"),
        marks=(Mark("C3", "unregistered_entity", 0, severity="major"),),
    ),
    # ---- C2 计划侧：把已死人物排进在场名单（blocker，计划闸门存在的理由） ----
    PlanCase(
        9,
        _card(
            ("char:linwan", "char:muqing"),
            (("前坡重逢", "loc:tingxue", ("char:linwan", "char:muqing")),),
        ),
        needles=_needle("char:muqing"),
        marks=(Mark("C2", "death_speaks", 0, severity="blocker"),),
    ),
    PlanCase(
        13,
        _card(
            ("char:linwan", "char:shenhuai"),
            (("廊下换灯", "loc:tingxue", ("char:shenhuai",)),),
        ),
        needles=_needle("char:shenhuai"),
        marks=(Mark("C2", "death_speaks", 0, severity="blocker"),),
    ),
    PlanCase(
        15,
        _card(
            ("char:linwan", "char:laozhou"),
            (("祠内问信", "loc:tingxue", ("char:laozhou",)),),
        ),
        needles=_needle("char:laozhou"),
        marks=(Mark("C2", "death_speaks", 0, severity="blocker"),),
    ),
    # ---- C6 计划侧：回收一条没埋过的线（blocker） / 字数带容不下目标（minor） ----
    PlanCase(
        12,
        _card(
            ("char:linwan", "char:agui"),
            (("门派盘问", "loc:tingxue", ("char:linwan",)),),
            payoffs=(997,),
        ),
        needles=_needle("[fsh#997]"),
        marks=(Mark("C6", "foreshadow_missing", 0, severity="blocker"),),
    ),
    PlanCase(
        18,
        _card(
            ("char:linwan", "char:agui"),
            (("棕发之疑", "loc:baidukou", ("char:linwan",)),),
            payoffs=(996, 995),
        ),
        needles=_needle("[fsh#996]", "[fsh#995]"),
        marks=(
            Mark("C6", "foreshadow_missing", 0, severity="blocker"),
            Mark("C6", "foreshadow_missing", 1, severity="blocker"),
        ),
    ),
    PlanCase(
        6,
        _card(
            ("char:linwan", "char:shenhuai"),
            (("师徒对话", "loc:tingxue", ("char:linwan",)),),
            low=400,
            high=600,
        ),
        needles=_needle("400-600"),
        marks=(Mark("C6", "length_out_of_band", 0, severity="minor"),),
    ),
    # ---- 干净卡：不该有任何命中 ----
    # 第 1 章 as_of=0 → Tier-1 整段不跑 → 没有未收伏笔可收，payoffs 必须留空
    PlanCase(
        1,
        _card(
            ("char:linwan", "char:laozhou"),
            (("接灯", "loc:tingxue", ("char:linwan",)),),
        ),
    ),
    PlanCase(
        3,
        _card(
            ("char:linwan", "char:muqing"),
            (("听雪", "loc:tingxue", ("char:linwan",)),),
        ),
    ),
    # payoff_decoy：打分时注入该章真实存在的未收编号，期望零命中
    PlanCase(
        4,
        _card(
            ("char:linwan", "char:shenhuai", "item:shuangren"),
            (("借剑", "loc:tingxue", ("char:linwan",)),),
        ),
        payoff_decoy=True,
    ),
    PlanCase(
        5,
        _card(
            ("char:linwan", "char:muqing"),
            (("山门外对峙", "loc:tingxue", ("char:linwan", "char:muqing")),),
            new=("char:stranger",),
        ),
    ),
    PlanCase(
        7,
        _card(
            ("char:linwan", "char:agui"),
            (("渡口拔剑", "loc:baidukou", ("char:linwan", "char:agui")),),
        ),
        payoff_decoy=True,
    ),
    PlanCase(
        10,
        _card(
            ("char:agui", "char:linwan"),
            (("称谓之争", "loc:baidukou", ("char:agui", "char:linwan")),),
        ),
    ),
    PlanCase(
        14,
        _card(
            ("char:linwan", "loc:baidukou"),
            (("渡船", "loc:baidukou", ("char:linwan",)),),
        ),
    ),
    PlanCase(
        16,
        _card(
            ("char:linwan", "item:shuangren"),
            (("剑名", "loc:tingxue", ("char:linwan",)),),
        ),
    ),
    PlanCase(
        20,
        _card(
            ("char:linwan", "char:agui"),
            (("收线", "loc:baidukou", ("char:linwan",)),),
        ),
        payoff_decoy=True,
    ),
)

__all__ = [
    "BIBLE",
    "CHAPTERS",
    "CONFLICT_CLASSES",
    "EXTRACTION_FAILED_CHAPTERS",
    "HARD_HIGH",
    "HARD_LOW",
    "IDEA",
    "JUDGE_ONLY_CODES",
    "OUTLINE",
    "PLAN_CASES",
    "RULES",
    "SOFT_HIGH",
    "SOFT_LOW",
    "STYLE",
    "TARGET_WORDS",
    "ChapterCase",
    "Mark",
    "PlanCase",
]
