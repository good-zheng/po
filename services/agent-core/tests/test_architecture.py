"""架构铁律测试：agent-core 必须保持框架无关、无 import 副作用。

参考实现（novel_server）的死因之一：编排模块 import 即连 Redis、
顶层实例化模型客户端、循环依赖靠延迟导入打补丁。本测试防复发。
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "po_agent_core"

# 禁止依赖的 Web 框架 / 宿主应用 / 持久层 ORM（协议客户端如 httpx 不受限）
FORBIDDEN_MODULES = frozenset(
    {"fastapi", "flask", "uvicorn", "starlette", "socketio", "django", "sqlalchemy", "po_chat"}
)

# 模块顶层禁止出现的资源类调用（连接/编译/执行都属于工厂函数内部的事）
SUSPICIOUS_CALLS = frozenset({"connect", "from_conn_string", "compile", "setup", "invoke", "stream"})


def iter_source_files() -> list[Path]:
    return sorted(SRC.rglob("*.py"))


def module_level_imports(tree: ast.Module) -> set[str]:
    """收集模块顶层 import 的顶层包名（函数体内的延迟 import 不算违规）。"""
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def call_name(call: ast.Call) -> str | None:
    func = call.func
    return getattr(func, "attr", None) or getattr(func, "id", None)


def test_source_tree_exists() -> None:
    files = iter_source_files()
    assert files, f"未找到源码：{SRC}"
    assert any(f.name == "__init__.py" and f.parent == SRC for f in files)


def test_no_forbidden_toplevel_imports() -> None:
    violations: list[str] = []
    for file in iter_source_files():
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        bad = module_level_imports(tree) & FORBIDDEN_MODULES
        if bad:
            violations.append(f"{file}: {sorted(bad)}")
    assert not violations, "agent-core 禁止依赖 Web 框架/宿主应用：\n" + "\n".join(violations)


def test_no_toplevel_resource_calls() -> None:
    """模块/类体顶层（非函数体内）禁止出现连接、编译、执行类调用。"""
    violations: list[str] = []
    for file in iter_source_files():
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    name = call_name(sub)
                    if name in SUSPICIOUS_CALLS:
                        violations.append(f"{file}: 模块顶层调用 {name}()")
    assert not violations, (
        "模块顶层禁止资源类调用（应延迟到工厂/初始化函数内）：\n" + "\n".join(violations)
    )
