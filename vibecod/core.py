#!/usr/bin/env python3
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Any, Optional, Dict, Callable

# ============================================================
# ERRORS
# ============================================================
class VIBEError(Exception):
    def __init__(self, msg: str, line: int = 0, col: int = 0):
        self.msg = msg
        self.line = line
        self.col = col
        super().__init__(f"[{line}:{col}] {msg}" if line else msg)

class VIBESyntaxError(VIBEError): pass
class VIBERuntimeError(VIBEError): pass
class VIBEReturnSignal(Exception):
    def __init__(self, value): self.value = value

# ============================================================
# TOKENS
# ============================================================
class TT(Enum):
    VIBE = "vibe"; YEET = "yeet"; FLORP = "florp"
    SPIT = "spit"; SPIT_COLOR = "spit_color"
    LOOPIT = "loopit"; GONE = "gone"
    MAYBE = "maybe"; NOPE = "nope"
    FN = "fn"; YOINK = "yoink"
    USE = "use"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    ASSIGN = "="; PLUS = "+"; MINUS = "-"
    MULTIPLY = "*"; DIVIDE = "/"; CONCAT = "+-"
    LT = "<"; GT = ">"; LTE = "<="; GTE = ">="
    EQ = "=="; NEQ = "!="
    AND = "&&"; OR = "||"; NOT = "!"
    INC = "++"; DEC = "--"
    DOT = "."
    LPAREN = "("; RPAREN = ")"
    LBRACE = "{"; RBRACE = "}"
    LBRACKET = "["; RBRACKET = "]"
    SEMICOLON = ";"; COMMA = ","
    ARROW = "->"
    EOF = "EOF"

@dataclass
class Token:
    type: TT
    value: Any
    line: int
    col: int

# ============================================================
# LEXER
# ============================================================
KEYWORDS = {
    'vibe': TT.VIBE, 'yeet': TT.YEET, 'florp': TT.FLORP,
    'spit': TT.SPIT, 'spit_color': TT.SPIT_COLOR,
    'loopit': TT.LOOPIT, 'gone': TT.GONE,
    'maybe': TT.MAYBE, 'nope': TT.NOPE,
    'fn': TT.FN, 'yoink': TT.YOINK,
    'use': TT.USE,
    'true': TT.BOOLEAN, 'false': TT.BOOLEAN,
    'null': TT.NULL,
}

class Lexer:
    def __init__(self, source: str, filename: str = "<input>"):
        self.src = source
        self.pos = 0
        self.line = 1
        self.col = 1

    def error(self, msg):
        raise VIBESyntaxError(msg, self.line, self.col)

    def peek(self, offset=0):
        i = self.pos + offset
        return self.src[i] if i < len(self.src) else None

    def advance(self):
        ch = self.src[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def skip_whitespace(self):
        while self.pos < len(self.src) and self.src[self.pos].isspace():
            self.advance()

    def skip_comment(self):
        while self.pos < len(self.src) and self.src[self.pos] != '\n':
            self.advance()

    def read_string(self):
        line, col = self.line, self.col
        self.advance()
        buf = []
        while self.pos < len(self.src):
            ch = self.src[self.pos]
            if ch == '"':
                self.advance()
                return Token(TT.STRING, ''.join(buf), line, col)
            if ch == '\\':
                self.advance()
                esc = self.advance()
                buf.append({'n':'\n','t':'\t','\\':'\\','"':'"'}.get(esc, esc))
            else:
                buf.append(self.advance())
        self.error("Unterminated string")

    def read_number(self):
        line, col = self.line, self.col
        buf = []
        is_float = False
        while self.pos < len(self.src) and (self.src[self.pos].isdigit() or self.src[self.pos] == '.'):
            if self.src[self.pos] == '.':
                if is_float: self.error("Invalid number")
                is_float = True
            buf.append(self.advance())
        s = ''.join(buf)
        return Token(TT.NUMBER, float(s) if is_float else int(s), line, col)

    def read_identifier(self):
        line, col = self.line, self.col
        buf = []
        while self.pos < len(self.src) and (self.src[self.pos].isalnum() or self.src[self.pos] == '_'):
            buf.append(self.advance())
        word = ''.join(buf)
        tt = KEYWORDS.get(word)
        if tt == TT.BOOLEAN:
            return Token(TT.BOOLEAN, word == 'true', line, col)
        if tt == TT.NULL:
            return Token(TT.NULL, None, line, col)
        if tt:
            return Token(tt, word, line, col)
        return Token(TT.IDENTIFIER, word, line, col)

    def tokenize(self):
        tokens = []
        while self.pos < len(self.src):
            self.skip_whitespace()
            if self.pos >= len(self.src):
                break
            line, col = self.line, self.col
            ch = self.src[self.pos]
            if ch == '/' and self.peek(1) == '/':
                self.skip_comment()
                continue
            if ch == '"':
                tokens.append(self.read_string())
                continue
            if ch.isdigit():
                tokens.append(self.read_number())
                continue
            if ch.isalpha() or ch == '_':
                tokens.append(self.read_identifier())
                continue
            two = self.src[self.pos:self.pos+2] if self.pos+1 < len(self.src) else ''
            if two == '+-':
                self.advance(); self.advance()
                tokens.append(Token(TT.CONCAT, '+-', line, col)); continue
            if two == '++':
                self.advance(); self.advance()
                tokens.append(Token(TT.INC, '++', line, col)); continue
            if two == '--':
                self.advance(); self.advance()
                tokens.append(Token(TT.DEC, '--', line, col)); continue
            if two == '==':
                self.advance(); self.advance()
                tokens.append(Token(TT.EQ, '==', line, col)); continue
            if two == '!=':
                self.advance(); self.advance()
                tokens.append(Token(TT.NEQ, '!=', line, col)); continue
            if two == '&&':
                self.advance(); self.advance()
                tokens.append(Token(TT.AND, '&&', line, col)); continue
            if two == '||':
                self.advance(); self.advance()
                tokens.append(Token(TT.OR, '||', line, col)); continue
            if two == '<=':
                self.advance(); self.advance()
                tokens.append(Token(TT.LTE, '<=', line, col)); continue
            if two == '>=':
                self.advance(); self.advance()
                tokens.append(Token(TT.GTE, '>=', line, col)); continue
            if two == '->':
                self.advance(); self.advance()
                tokens.append(Token(TT.ARROW, '->', line, col)); continue
            single = {
                '+': TT.PLUS, '-': TT.MINUS, '*': TT.MULTIPLY, '/': TT.DIVIDE,
                '<': TT.LT, '>': TT.GT, '=': TT.ASSIGN, '!': TT.NOT,
                '(': TT.LPAREN, ')': TT.RPAREN,
                '{': TT.LBRACE, '}': TT.RBRACE,
                '[': TT.LBRACKET, ']': TT.RBRACKET,
                ';': TT.SEMICOLON, ',': TT.COMMA, '.': TT.DOT,
            }
            if ch in single:
                self.advance()
                tokens.append(Token(single[ch], ch, line, col))
                continue
            self.error(f"Unknown character '{ch}'")
        tokens.append(Token(TT.EOF, None, self.line, self.col))
        return tokens

# ============================================================
# AST NODES
# ============================================================
@dataclass
class Node: line: int = 0; col: int = 0
@dataclass
class NumLit(Node): value: Any = None
@dataclass
class StrLit(Node): value: str = ""
@dataclass
class BoolLit(Node): value: bool = False
@dataclass
class VarExpr(Node): name: str = ""
@dataclass
class BinOp(Node): left: Node = None; op: str = ""; right: Node = None
@dataclass
class CallExpr(Node): callee: Node = None; args: List[Node] = field(default_factory=list)
@dataclass
class AssignExpr(Node): name: str = ""; value: Node = None
@dataclass
class VarDecl(Node): var_type: str = ""; name: str = ""; value: Node = None
@dataclass
class SpitStmt(Node): value: Node = None
@dataclass
class SpitColorStmt(Node): color: Node = None; text: Node = None
@dataclass
class LoopItStmt(Node): init: Node = None; condition: Node = None; increment: Node = None; body: List[Node] = field(default_factory=list)
@dataclass
class MaybeStmt(Node): condition: Node = None; body: List[Node] = field(default_factory=list); elifs: List[tuple] = field(default_factory=list); else_body: Optional[List[Node]] = None
@dataclass
class FnDecl(Node): name: str = ""; params: List[str] = field(default_factory=list); body: List[Node] = field(default_factory=list)
@dataclass
class UseStmt(Node): module: str = ""
@dataclass
class ExprStmt(Node): expr: Node = None
@dataclass
class Program(Node): statements: List[Node] = field(default_factory=list)

# ============================================================
# PARSER
# ============================================================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    def cur(self):
        return self.tokens[self.pos]
    def eat(self, *types):
        tok = self.cur()
        if tok.type not in types:
            raise VIBESyntaxError(f"Expected {types}, got {tok.type}", tok.line, tok.col)
        self.pos += 1
        return tok
    def parse(self):
        stmts = []
        while not self.cur().type == TT.EOF:
            stmts.append(self.parse_stmt())
        return Program(stmts)
    def parse_stmt(self):
        tok = self.cur()
        if tok.type in (TT.VIBE, TT.YEET, TT.FLORP):
            self.eat(tok.type)
            name = self.eat(TT.IDENTIFIER).value
            self.eat(TT.ASSIGN)
            val = self.parse_expr()
            return VarDecl(tok.type.value, name, val, tok.line, tok.col)
        if tok.type == TT.SPIT:
            self.eat(TT.SPIT)
            self.eat(TT.LPAREN)
            val = self.parse_expr()
            self.eat(TT.RPAREN)
            return SpitStmt(val, tok.line, tok.col)
        if tok.type == TT.SPIT_COLOR:
            self.eat(TT.SPIT_COLOR)
            self.eat(TT.LPAREN)
            color = self.parse_expr()
            self.eat(TT.COMMA)
            text = self.parse_expr()
            self.eat(TT.RPAREN)
            return SpitColorStmt(color, text, tok.line, tok.col)
        if tok.type == TT.LOOPIT:
            self.eat(TT.LOOPIT)
            self.eat(TT.LPAREN)
            if self.cur().type in (TT.VIBE, TT.YEET, TT.FLORP):
                init = self.parse_stmt()
            else:
                name = self.eat(TT.IDENTIFIER).value
                self.eat(TT.ASSIGN)
                val = self.parse_expr()
                init = VarDecl('vibe', name, val)
            self.eat(TT.SEMICOLON)
            cond = self.parse_expr()
            self.eat(TT.SEMICOLON)
            inc_name = self.eat(TT.IDENTIFIER).value
            if self.cur().type == TT.INC:
                self.eat(TT.INC)
                inc = AssignExpr(inc_name, BinOp(VarExpr(inc_name), '+', NumLit(1)))
            else:
                self.eat(TT.ASSIGN)
                inc_val = self.parse_expr()
                inc = AssignExpr(inc_name, inc_val)
            self.eat(TT.RPAREN)
            self.eat(TT.LBRACE)
            body = []
            while not self.cur().type == TT.RBRACE:
                body.append(self.parse_stmt())
            self.eat(TT.RBRACE)
            return LoopItStmt(init, cond, inc, body, tok.line, tok.col)
        if tok.type == TT.MAYBE:
            self.eat(TT.MAYBE)
            self.eat(TT.LPAREN)
            cond = self.parse_expr()
            self.eat(TT.RPAREN)
            self.eat(TT.LBRACE)
            body = []
            while not self.cur().type == TT.RBRACE:
                body.append(self.parse_stmt())
            self.eat(TT.RBRACE)
            elifs = []
            else_body = None
            while self.cur().type == TT.MAYBE and self.tokens[self.pos+1].type == TT.MAYBE:
                self.eat(TT.MAYBE)
                self.eat(TT.LPAREN)
                econd = self.parse_expr()
                self.eat(TT.RPAREN)
                self.eat(TT.LBRACE)
                ebody = []
                while not self.cur().type == TT.RBRACE:
                    ebody.append(self.parse_stmt())
                self.eat(TT.RBRACE)
                elifs.append((econd, ebody))
            if self.cur().type == TT.NOPE:
                self.eat(TT.NOPE)
                self.eat(TT.LBRACE)
                else_body = []
                while not self.cur().type == TT.RBRACE:
                    else_body.append(self.parse_stmt())
                self.eat(TT.RBRACE)
            return MaybeStmt(cond, body, elifs, else_body, tok.line, tok.col)
        if tok.type == TT.FN:
            self.eat(TT.FN)
            name = self.eat(TT.IDENTIFIER).value
            self.eat(TT.LPAREN)
            params = []
            if not self.cur().type == TT.RPAREN:
                params.append(self.eat(TT.IDENTIFIER).value)
                while self.cur().type == TT.COMMA:
                    self.eat(TT.COMMA)
                    params.append(self.eat(TT.IDENTIFIER).value)
            self.eat(TT.RPAREN)
            self.eat(TT.LBRACE)
            body = []
            while not self.cur().type == TT.RBRACE:
                body.append(self.parse_stmt())
            self.eat(TT.RBRACE)
            return FnDecl(name, params, body, tok.line, tok.col)
        if tok.type == TT.YOINK:
            self.eat(TT.YOINK)
            val = self.parse_expr() if not self.cur().type in (TT.RBRACE, TT.EOF) else None
            return ExprStmt(CallExpr(VarExpr("__return__"), [val] if val else []))
        if tok.type == TT.IDENTIFIER:
            name = self.eat(TT.IDENTIFIER).value
            if self.cur().type == TT.ASSIGN:
                self.eat(TT.ASSIGN)
                val = self.parse_expr()
                return ExprStmt(AssignExpr(name, val))
            self.pos -= 1
            expr = self.parse_expr()
            return ExprStmt(expr)
        return self.parse_expr()
    def parse_expr(self):
        return self.parse_or()
    def parse_or(self):
        left = self.parse_and()
        while self.cur().type == TT.OR:
            op = self.eat(TT.OR).value
            right = self.parse_and()
            left = BinOp(left, op, right)
        return left
    def parse_and(self):
        left = self.parse_eq()
        while self.cur().type == TT.AND:
            op = self.eat(TT.AND).value
            right = self.parse_eq()
            left = BinOp(left, op, right)
        return left
    def parse_eq(self):
        left = self.parse_compare()
        while self.cur().type in (TT.EQ, TT.NEQ):
            op = self.eat(self.cur().type).value
            right = self.parse_compare()
            left = BinOp(left, op, right)
        return left
    def parse_compare(self):
        left = self.parse_concat()
        if self.cur().type in (TT.LT, TT.GT, TT.LTE, TT.GTE, TT.GONE):
            op = self.eat(self.cur().type)
            op_val = '<' if op.type == TT.GONE else op.value
            right = self.parse_concat()
            left = BinOp(left, op_val, right)
        return left
    def parse_concat(self):
        left = self.parse_add()
        while self.cur().type == TT.CONCAT:
            self.eat(TT.CONCAT)
            right = self.parse_add()
            left = BinOp(left, '+-', right)
        return left
    def parse_add(self):
        left = self.parse_mul()
        while self.cur().type in (TT.PLUS, TT.MINUS):
            op = self.eat(self.cur().type).value
            right = self.parse_mul()
            left = BinOp(left, op, right)
        return left
    def parse_mul(self):
        left = self.parse_unary()
        while self.cur().type in (TT.MULTIPLY, TT.DIVIDE):
            op = self.eat(self.cur().type).value
            right = self.parse_unary()
            left = BinOp(left, op, right)
        return left
    def parse_unary(self):
        if self.cur().type == TT.NOT:
            op = self.eat(TT.NOT).value
            return BinOp(None, op, self.parse_unary())
        if self.cur().type == TT.MINUS:
            op = self.eat(TT.MINUS).value
            return BinOp(NumLit(0), op, self.parse_unary())
        return self.parse_primary()
    def parse_primary(self):
        tok = self.cur()
        if tok.type == TT.NUMBER:
            self.eat(TT.NUMBER)
            return NumLit(tok.value, tok.line, tok.col)
        if tok.type == TT.STRING:
            self.eat(TT.STRING)
            return StrLit(tok.value, tok.line, tok.col)
        if tok.type == TT.BOOLEAN:
            self.eat(TT.BOOLEAN)
            return BoolLit(tok.value, tok.line, tok.col)
        if tok.type == TT.IDENTIFIER:
            name = self.eat(TT.IDENTIFIER).value
            if self.cur().type == TT.LPAREN:
                self.eat(TT.LPAREN)
                args = []
                if not self.cur().type == TT.RPAREN:
                    args.append(self.parse_expr())
                    while self.cur().type == TT.COMMA:
                        self.eat(TT.COMMA)
                        args.append(self.parse_expr())
                self.eat(TT.RPAREN)
                return CallExpr(VarExpr(name), args)
            return VarExpr(name, tok.line, tok.col)
        if tok.type == TT.LPAREN:
            self.eat(TT.LPAREN)
            expr = self.parse_expr()
            self.eat(TT.RPAREN)
            return expr
        raise VIBESyntaxError(f"Unexpected token {tok.type}", tok.line, tok.col)

# ============================================================
# ENVIRONMENT
# ============================================================
class Env:
    def __init__(self, parent=None):
        self.vars = {}
        self.consts = set()
        self.parent = parent
    def get(self, name, line=0, col=0):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name, line, col)
        raise VIBERuntimeError(f"Undefined '{name}'", line, col)
    def set(self, name, val, line=0, col=0):
        if name in self.consts:
            raise VIBERuntimeError(f"Cannot reassign yeet '{name}'", line, col)
        if name in self.vars or not self.parent:
            self.vars[name] = val
        else:
            self.parent.set(name, val, line, col)
    def define(self, name, val, is_const=False):
        self.vars[name] = val
        if is_const:
            self.consts.add(name)

@dataclass
class VIBEFunction:
    name: str
    params: List[str]
    body: List[Node]
    closure: Env

@dataclass
class NativeFunction:
    name: str
    fn: Callable

# ============================================================
# INTERPRETER
# ============================================================
COLORS = {'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m', 'blue': '\033[94m', 'magenta': '\033[95m', 'cyan': '\033[96m', 'white': '\033[97m', 'black': '\033[30m'}

class Interpreter:
    def __init__(self):
        self.globals = Env()
        self.globals.define('spit', NativeFunction('spit', lambda args: print(self._str(args[0]), flush=True)))
        self.globals.define('spit_color', NativeFunction('spit_color', lambda args: print(f"{COLORS.get(str(args[0]), '')}{self._str(args[1])}\033[0m", flush=True)))
        self.globals.define('len', NativeFunction('len', lambda args: len(args[0])))
        self.globals.define('str', NativeFunction('str', lambda args: str(args[0])))
        self.globals.define('num', NativeFunction('num', lambda args: float(args[0])))
        self.globals.define('push', NativeFunction('push', lambda args: args[0].append(args[1]) or args[0]))
        self.globals.define('pop', NativeFunction('pop', lambda args: args[0].pop()))
        self.globals.define('exit', NativeFunction('exit', lambda args: sys.exit(0)))

    def _str(self, val):
        if isinstance(val, list): return "[" + ", ".join(self._str(v) for v in val) + "]"
        if isinstance(val, bool): return "true" if val else "false"
        if val is None: return "null"
        return str(val)

    def eval(self, node, env):
        if isinstance(node, NumLit): return node.value
        if isinstance(node, StrLit): return node.value
        if isinstance(node, BoolLit): return node.value
        if isinstance(node, VarExpr): return env.get(node.name, node.line, node.col)
        if isinstance(node, BinOp):
            if node.op == '+-':
                return self._str(self.eval(node.left, env)) + self._str(self.eval(node.right, env))
            l = self.eval(node.left, env)
            r = self.eval(node.right, env)
            if node.op == '+': return l + r
            if node.op == '-': return l - r
            if node.op == '*': return l * r
            if node.op == '/': return l / r
            if node.op == '<': return l < r
            if node.op == '>': return l > r
            if node.op == '==': return l == r
            if node.op == '!=': return l != r
            if node.op == '&&': return l and r
            if node.op == '||': return l or r
            return None
        if isinstance(node, AssignExpr):
            val = self.eval(node.value, env)
            env.set(node.name, val, node.line, node.col)
            return val
        if isinstance(node, CallExpr):
            callee = self.eval(node.callee, env)
            args = [self.eval(a, env) for a in node.args]
            if isinstance(callee, NativeFunction):
                return callee.fn(args)
            if isinstance(callee, VIBEFunction):
                if len(args) != len(callee.params):
                    raise VIBERuntimeError(f"Expected {len(callee.params)} args, got {len(args)}", node.line, node.col)
                fn_env = Env(callee.closure)
                for p, a in zip(callee.params, args):
                    fn_env.define(p, a)
                try:
                    self.exec_block(callee.body, fn_env)
                except VIBEReturnSignal as ret:
                    return ret.value
                return None
            raise VIBERuntimeError(f"Not callable: {callee}", node.line, node.col)
        raise VIBERuntimeError(f"Unknown node {type(node)}", node.line, node.col)

    def exec(self, node, env):
        if isinstance(node, Program):
            for s in node.statements:
                self.exec(s, env)
        elif isinstance(node, VarDecl):
            val = self.eval(node.value, env)
            env.define(node.name, val, node.var_type == 'yeet')
        elif isinstance(node, SpitStmt):
            print(self._str(self.eval(node.value, env)), flush=True)
        elif isinstance(node, SpitColorStmt):
            col = self._str(self.eval(node.color, env))
            txt = self._str(self.eval(node.text, env))
            print(f"{COLORS.get(col, '')}{txt}\033[0m", flush=True)
        elif isinstance(node, LoopItStmt):
            loop_env = Env(env)
            self.exec(node.init, loop_env)
            while self.eval(node.condition, loop_env):
                body_env = Env(loop_env)
                try:
                    self.exec_block(node.body, body_env)
                except VIBEReturnSignal:
                    raise
                self.exec(node.increment, loop_env)
        elif isinstance(node, MaybeStmt):
            if self.eval(node.condition, env):
                self.exec_block(node.body, Env(env))
            else:
                for cond, body in node.elifs:
                    if self.eval(cond, env):
                        self.exec_block(body, Env(env))
                        return
                if node.else_body:
                    self.exec_block(node.else_body, Env(env))
        elif isinstance(node, FnDecl):
            env.define(node.name, VIBEFunction(node.name, node.params, node.body, env))
        elif isinstance(node, ExprStmt):
            self.eval(node.expr, env)
        elif isinstance(node, UseStmt):
            pass
        else:
            self.eval(node, env)

    def exec_block(self, stmts, env):
        for s in stmts:
            self.exec(s, env)

    def run(self, prog):
        self.exec(prog, self.globals)

# ============================================================
# PUBLIC API
# ============================================================
def run_code(code: str):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.run(ast)

def run_file(path: str):
    with open(path, 'r') as f:
        run_code(f.read())
