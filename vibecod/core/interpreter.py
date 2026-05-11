from .env import Env


class Interpreter:
    def __init__(self):
        self.globals = Env()

    def exec(self, node):
        method = getattr(self, f"eval_{type(node).__name__}", None)
        if method:
            return method(node)
        raise Exception(f"No eval for {type(node).__name__}")

    # ---------------- PROGRAM ----------------

    def eval_Program(self, node):
        result = None
        for stmt in node.statements:
            result = self.exec(stmt)
        return result

    # ---------------- EXPRESSIONS ----------------

    def eval_NumLit(self, node):
        return node.value

    def eval_StrLit(self, node):
        return node.value

    def eval_VarExpr(self, node):
        return self.globals.get(node.name)

    def eval_BinOp(self, node):
        l = self.exec(node.left)
        r = self.exec(node.right)

        if node.op == "+":
            return l + r
        if node.op == "-":
            return l - r
        if node.op == "*":
            return l * r
        if node.op == "/":
            return l / r

    # ---------------- STATEMENTS ----------------

    def eval_SpitStmt(self, node):
        print(self.exec(node.value))

    def eval_ExprStmt(self, node):
        return self.exec(node.expr)

    def eval_VarDecl(self, node):
        self.globals.define(node.name, self.exec(node.value))

    def eval_AssignStmt(self, node):
        self.globals.assign(node.name, self.exec(node.value))

    def eval_IfStmt(self, node):
        cond = self.exec(node.cond)

        if cond:
            for s in node.body:
                self.exec(s)
        elif node.else_body:
            for s in node.else_body:
                self.exec(s)

# ---------------- SAFE ENTRY POINTS ----------------

def run_code(code: str, interp=None, filename="<memory>"):
    interp = interp or Interpreter()
    return interp


def run_file(path: str):
    import os

    if not os.path.exists(path):
        print(f"[VIBE ERROR] file not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    return run_code(code)
