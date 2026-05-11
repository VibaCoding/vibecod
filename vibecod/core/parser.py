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

    def parse(self):
        stmts = []
        while self.cur().type != TT.EOF:
            stmts.append(self.statement())
        return Program(statements=stmts)

    def statement(self):
        tok = self.cur()

        if tok.type == TT.SPIT:
            self.eat(TT.SPIT)
            val = self.expr()
            return SpitStmt(value=val)

        return ExprStmt(expr=self.expr())

    def expr(self):
        return self.term()

    def term(self):
        left = self.factor()

        while self.cur().type in (TT.PLUS, TT.MINUS):
            op = self.cur().type.value
            self.eat(self.cur().type)
            right = self.factor()
            left = BinOp(left=left, op=op, right=right)

        return left

    def factor(self):
        left = self.primary()

        while self.cur().type in (TT.MUL, TT.DIV):
            op = self.cur().type.value
            self.eat(self.cur().type)
            right = self.primary()
            left = BinOp(left=left, op=op, right=right)

        return left

    def primary(self):
        tok = self.cur()

        if tok.type == TT.NUMBER:
            self.eat(TT.NUMBER)
            return NumLit(value=tok.value)

        if tok.type == TT.STRING:
            self.eat(TT.STRING)
            return StrLit(value=tok.value)

        if tok.type == TT.IDENT:
            self.eat(TT.IDENT)
            return VarExpr(name=tok.value)

        if tok.type == TT.LPAREN:
            self.eat(TT.LPAREN)
            expr = self.expr()
            self.eat(TT.RPAREN)
            return expr

        raise Exception(f"Unexpected {tok.type}")
