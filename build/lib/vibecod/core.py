#!/usr/bin/env python3
import sys
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Any, Optional, Dict, Callable


# =========================
# ERRORS
# =========================

class VIBEError(Exception): pass
class VIBESyntaxError(VIBEError): pass
class VIBERuntimeError(VIBEError): pass
class VIBEReturnSignal(Exception):
    def __init__(self, value): self.value = value


# =========================
# TOKENS
# =========================

class TT(Enum):
    VIBE = "vibe"
YEET = "yeet"
FLORP = "florp"
    SPIT = "spit"
SPIT_COLOR = "spit_color"
    LOOPIT = "loopit"
GONE = "gone"
    MAYBE = "maybe"
NOPE = "nope"
    FN = "fn"
YOINK = "yoink"
    USE = "use"

    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"

    ASSIGN = "="
PLUS = "+"
MINUS = "-"
    MULTIPLY = "*"
DIVIDE = "/"
CONCAT = "+-"

    LT = "<"
GT = ">"
LTE = "<="
GTE = ">="
    EQ = "=="
NEQ = "!="
    AND = "&&"
OR = "||"
NOT = "!"

    INC = "++"
DEC = "--"

    LPAREN = "("
RPAREN = ")"
    LBRACE = "{"
RBRACE = "}"
    SEMICOLON = ";"
COMMA = ","
    DOT = "."
    EOF = "EOF"


@dataclass
class Token:
    type: TT
    value: Any
    line: int
    col: int


# =========================
# LEXER
# =========================

class Lexer:
    def __init__(self, source: str):
        self.src = source
        self.pos = 0
        self.line = 1
        self.col = 1

    def error(self, msg): raise VIBESyntaxError(msg, self.line, self.col)

    def peek(self, o=0):
        i = self.pos + o
        return self.src[i] if i < len(self.src) else None

    def advance(self):
        ch = self.src[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def skip_ws(self):
        while self.pos < len(self.src) and self.src[self.pos].isspace():
            self.advance()

    def skip_comment(self):
        while self.pos < len(self.src) and self.src[self.pos] != "\n":
            self.advance()

    def read_string(self):
        line, col = self.line, self.col
        self.advance()
        buf = []
        while self.pos < len(self.src):
            ch = self.src[self.pos]
            if ch == '"':
                self.advance()
                return Token(TT.STRING, "".join(buf), line, col)
            if ch == "\\":
                self.advance()
                esc = self.advance()
                buf.append({"n":"\n","t":"\t","\\":"\\","\"":"\""}.get(esc, esc))
            else:
                buf.append(self.advance())
        self.error("Unterminated string")

    def read_number(self):
        line, col = self.line, self.col
        buf = []
        dot = False
        while self.pos < len(self.src) and (self.src[self.pos].isdigit() or self.src[self.pos] == "."):
            if self.src[self.pos] == ".":
                if dot: self.error("bad number")
                dot = True
            buf.append(self.advance())
        s = "".join(buf)
        return Token(TT.NUMBER, float(s) if dot else int(s), line, col)

    def read_ident(self):
        line, col = self.line, self.col
        buf = []
        while self.pos < len(self.src) and (self.src[self.pos].isalnum() or self.src[self.pos] == "_"):
            buf.append(self.advance())
        w = "".join(buf)

        kw = {
            "vibe": TT.VIBE, "yeet": TT.YEET, "florp": TT.FLORP,
            "spit": TT.SPIT, "spit_color": TT.SPIT_COLOR,
            "loopit": TT.LOOPIT, "gone": TT.GONE,
            "maybe": TT.MAYBE, "nope": TT.NOPE,
            "fn": TT.FN, "yoink": TT.YOINK,
            "use": TT.USE,
            "true": TT.BOOLEAN, "false": TT.BOOLEAN,
            "null": TT.NULL,
        }

        tt = kw.get(w)
        if tt == TT.BOOLEAN: return Token(TT.BOOLEAN, w == "true", line, col)
        if tt == TT.NULL: return Token(TT.NULL, None, line, col)
        if tt: return Token(tt, w, line, col)
        return Token(TT.IDENTIFIER, w, line, col)

    def tokenize(self):
        out = []
        while self.pos < len(self.src):
            self.skip_ws()
            if self.pos >= len(self.src): break

            line, col = self.line, self.col
            ch = self.src[self.pos]

            if ch == "/" and self.peek(1) == "/":
                self.skip_comment()
                continue

            if ch == '"':
                out.append(self.read_string())
continue
            if ch.isdigit():
                out.append(self.read_number())
continue
            if ch.isalpha() or ch == "_":
                out.append(self.read_ident())
continue

            two = self.src[self.pos:self.pos+2]
            if two in ("++","--","==","!=","&&","||","<=",">=","+-"):
                self.advance()
self.advance()
                mapping = {
                    "++": TT.INC, "--": TT.DEC,
                    "==": TT.EQ, "!=": TT.NEQ,
                    "&&": TT.AND, "||": TT.OR,
                    "<=": TT.LTE, ">=": TT.GTE,
                    "+-": TT.CONCAT
                }
                out.append(Token(mapping[two], two, line, col))
                continue

            single = {
                "+":TT.PLUS,"-":TT.MINUS,"*":TT.MULTIPLY,"/":TT.DIVIDE,
                "<":TT.LT,">":TT.GT,"=":TT.ASSIGN,"!":TT.NOT,
                "(":TT.LPAREN,")":TT.RPAREN,
                "{":TT.LBRACE,"}":TT.RBRACE,
                ";":TT.SEMICOLON,",":TT.COMMA,
                ".":TT.DOT
            }

            if ch in single:
                self.advance()
                out.append(Token(single[ch], ch, line, col))
                continue

            self.error(f"bad char {ch}")

        out.append(Token(TT.EOF, None, self.line, self.col))
        return out


# =========================
# AST
# =========================

@dataclass
class Node: line: int = 0
col: int = 0
@dataclass
class NumLit(Node): value: Any = None
@dataclass
class StrLit(Node): value: str = ""
@dataclass
class BoolLit(Node): value: bool = False
@dataclass
class VarExpr(Node): name: str = ""
@dataclass
class BinOp(Node): left: Node = None
op: str = ""
right: Node = None
@dataclass
class CallExpr(Node): callee: Node = None
args: List[Node] = field(default_factory=list)
@dataclass
class AssignExpr(Node): name: str = ""
value: Node = None
@dataclass
class VarDecl(Node): var_type: str = ""
name: str = ""
value: Node = None
@dataclass
class SpitStmt(Node): value: Node = None
@dataclass
class ExprStmt(Node): expr: Node = None
@dataclass
class Program(Node): statements: List[Node] = field(default_factory=list)
@dataclass
class UseStmt(Node): module: str = ""


# =========================
# PARSER
# =========================

class Parser:
    def __init__(self, t): self.t=t
self.i=0
    def cur(self): return self.t[self.i]
    def eat(self, *x):
        tok=self.cur()
        if tok.type not in x:
            raise VIBESyntaxError("expected", tok.line, tok.col)
        self.i+=1
return tok

    def parse(self):
        s=[]
        while self.cur().type!=TT.EOF:
            s.append(self.stmt())
        return Program(s)

    def stmt(self):
        tok=self.cur()

        if tok.type == TT.USE:
            self.eat(TT.USE)
            m = self.eat(TT.STRING).value
            return UseStmt(m, tok.line, tok.col)

        if tok.type == TT.SPIT:
            self.eat(TT.SPIT)
            self.eat(TT.LPAREN)
            v=self.expr()
            self.eat(TT.RPAREN)
            return SpitStmt(v,tok.line,tok.col)

        if tok.type in (TT.VIBE,TT.YEET,TT.FLORP):
            tt=self.eat(tok.type)
            name=self.eat(TT.IDENTIFIER).value
            self.eat(TT.ASSIGN)
            v=self.expr()
            return VarDecl(tt.value,name,v,tok.line,tok.col)

        if tok.type==TT.IDENTIFIER:
            name=self.eat(TT.IDENTIFIER).value
            if self.cur().type==TT.ASSIGN:
                self.eat(TT.ASSIGN)
                v=self.expr()
                return ExprStmt(AssignExpr(name,v))
            self.i-=1
            return ExprStmt(self.expr())

        return ExprStmt(self.expr())

    def expr(self):
        return self.primary()

    def primary(self):
        t=self.cur()
        if t.type==TT.NUMBER: self.eat(TT.NUMBER)
return NumLit(t.value)
        if t.type==TT.STRING: self.eat(TT.STRING)
return StrLit(t.value)
        if t.type==TT.BOOLEAN: self.eat(TT.BOOLEAN)
return BoolLit(t.value)
        if t.type==TT.IDENTIFIER:
            n=self.eat(TT.IDENTIFIER).value
            return VarExpr(n)
        raise VIBESyntaxError("bad expr",t.line,t.col)


# =========================
# ENV
# =========================

class Env:
    def __init__(self,parent=None):
        self.vars={}
        self.parent=parent

    def get(self,n):
        if n in self.vars: return self.vars[n]
        if self.parent: return self.parent.get(n)
        raise VIBERuntimeError(f"undef {n}")

    def set(self,n,v):
        if n in self.vars: self.vars[n]=v
        elif self.parent: self.parent.set(n,v)
        else: self.vars[n]=v

    def define(self,n,v): self.vars[n]=v


# =========================
# INTERPRETER + MODULE SYSTEM
# =========================

class Interpreter:
    def __init__(self):
        self.globals = Env()
        self.modules = {}  # cache

        self.globals.define("spit", lambda a: print(a[0]))

    def run_file(self, path, env):
        with open(path,"r",encoding="utf-8") as f:
            code=f.read()
        return self.run_code(code, env)

    def run_code(self, code, env):
        ast = Parser(Lexer(code).tokenize()).parse()
        return self.exec(ast, env)

    def exec(self, node, env):
        if isinstance(node, Program):
            for s in node.statements:
                self.exec(s, env)

        elif isinstance(node, VarDecl):
            env.define(node.name, self.eval(node.value, env))

        elif isinstance(node, SpitStmt):
            print(self.eval(node.value, env))

        elif isinstance(node, ExprStmt):
            return self.eval(node.expr, env)

        elif isinstance(node, UseStmt):
            name = node.module

            if name in self.modules:
                mod_env = self.modules[name]
            else:
                mod_env = Env(self.globals)

                # simple resolve
                if not name.endswith(".vibe"):
                    name += ".vibe"

                if not os.path.exists(name):
                    raise VIBERuntimeError(f"module not found {name}")

                self.run_file(name, mod_env)
                self.modules[name] = mod_env

            # import into current scope
            for k,v in mod_env.vars.items():
                env.define(k,v)

        else:
            return self.eval(node, env)

    def eval(self,node,env):
        if isinstance(node,NumLit): return node.value
        if isinstance(node,StrLit): return node.value
        if isinstance(node,BoolLit): return node.value
        if isinstance(node,VarExpr): return env.get(node.name)
        return None


# =========================
# ENTRY
# =========================

def run_code(code):
    i=Interpreter()
    i.exec(Parser(Lexer(code).tokenize()).parse(), i.globals)
