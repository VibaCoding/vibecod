class Node:
    pass


class Program(Node):
    def __init__(self, statements):
        self.statements = statements


# -------- expressions --------

class NumLit(Node):
    def __init__(self, value):
        self.value = value


class StrLit(Node):
    def __init__(self, value):
        self.value = value


class VarExpr(Node):
    def __init__(self, name):
        self.name = name


class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


# -------- statements --------

class ExprStmt(Node):
    def __init__(self, expr):
        self.expr = expr


class SpitStmt(Node):
    def __init__(self, value):
        self.value = value


class VarDecl(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class AssignStmt(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class IfStmt(Node):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body


class WhileStmt(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class FuncDecl(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class ReturnStmt(Node):
    def __init__(self, value):
        self.value = value
