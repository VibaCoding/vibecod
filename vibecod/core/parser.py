from .ast import *
from .lexer import TT


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def cur(self):
        return self.tokens[self.i]

    def eat(self, t):
        tok = self.cur()
        if tok.type != t:
            raise Exception(f"Expected {t}, got {tok.type}")
        self.i += 1
        return tok

    # ---------------- ROOT ----------------

    def parse(self):
        stmts = []
        while self.cur().type != TT.EOF:
            stmts.append(self.statement())
        return Program(stmts)

    # ---------------- STATEMENTS ----------------

    def statement(self):
        tok = self.cur()

        # spit
        if tok.type == TT.SPIT:
            self.eat(TT.SPIT)
            return SpitStmt(self.expr())

        # hold (var decl)
        if tok.type == TT.HOLD:
            self.eat(TT.HOLD)
            name = self.eat(TT.IDENT).value
            self.eat(TT.EQ)
            value = self.expr()
            return VarDecl(name, value)

        # set (assign)
        if tok.type == TT.SET:
            self.eat(TT.SET)
            name = self.eat(TT.IDENT).value
            self.eat(TT.EQ)
            value = self.expr()
            return AssignStmt(name, value)

        # when (if)
        if tok.type == TT.WHEN:
            self.eat(TT.WHEN)
            cond = self.expr()
            body = self.block()

            else_body = None
            if self.cur().type == TT.ELSE:
                self.eat(TT.ELSE)
                else_body = self.block()

            return IfStmt(cond, body, else_body)

        return ExprStmt(self.expr())

    # ---------------- BLOCK ----------------

    def block(self):
        self.eat(TT.LBRACE)
        stmts = []

        while self.cur().type != TT.RBRACE:
            stmts.append(self.statement())

        self.eat(TT.RBRACE)
        return stmts

    # ---------------- EXPRESSIONS ----------------

    def expr(self):
        return self.term()

    def term(self):
        left = self.factor()

        while self.cur().type in (TT.PLUS, TT.MINUS):
            op = self.cur().type.value
            self.eat(self.cur().type)
            right = self.factor()
            left = BinOp(left, op, right)

        return left

    def factor(self):
        left = self.primary()

        while self.cur().type in (TT.MUL, TT.DIV):
            op = self.cur().type.value
            self.eat(self.cur().type)
            right = self.primary()
            left = BinOp(left, op, right)

        return left

    def primary(self):
        tok = self.cur()

        if tok.type == TT.NUMBER:
            self.eat(TT.NUMBER)
            return NumLit(tok.value)

        if tok.type == TT.STRING:
            self.eat(TT.STRING)
            return StrLit(tok.value)

        if tok.type == TT.IDENT:
            self.eat(TT.IDENT)
            return VarExpr(tok.value)

        if tok.type == TT.LPAREN:
            self.eat(TT.LPAREN)
            expr = self.expr()
            self.eat(TT.RPAREN)
            return expr

        raise Exception(f"Unexpected {tok.type}")
