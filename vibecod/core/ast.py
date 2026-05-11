from dataclasses import dataclass, field
from typing import Any, List, Optional

@dataclass
class Node:
    line: int = 0
    col: int = 0

@dataclass
class NumLit(Node):
    value: Any = None

@dataclass
class StrLit(Node):
    value: str = ""

@dataclass
class BoolLit(Node):
    value: bool = False

@dataclass
class VarExpr(Node):
    name: str = ""

@dataclass
class BinOp(Node):
    left: Node = None
    op: str = ""
    right: Node = None

@dataclass
class CallExpr(Node):
    callee: Node = None
    args: List[Node] = field(default_factory=list)

@dataclass
class AssignExpr(Node):
    name: str = ""
    value: Node = None

@dataclass
class VarDecl(Node):
    var_type: str = ""
    name: str = ""
    value: Node = None

@dataclass
class SpitStmt(Node):
    value: Node = None

@dataclass
class ExprStmt(Node):
    expr: Node = None

@dataclass
class Program(Node):
    statements: List[Node] = field(default_factory=list)
