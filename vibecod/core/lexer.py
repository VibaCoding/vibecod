from dataclasses import dataclass
from enum import Enum

class TT(Enum):
    NUMBER="NUMBER"
    STRING="STRING"
    IDENT="IDENT"

    PLUS="+"
    MINUS="-"
    MUL="*"
    DIV="/"
    ASSIGN="="

    LPAREN="("
    RPAREN=")"
    EOF="EOF"

    SPIT="spit"

@dataclass
class Token:
    type: TT
    value: any
    line: int
    col: int


class Lexer:
    def __init__(self, src):
        self.src = src
        self.i = 0
        self.line = 1
        self.col = 1

    def peek(self):
        return self.src[self.i] if self.i < len(self.src) else None

    def advance(self):
        ch = self.src[self.i]
        self.i += 1
        self.col += 1
        return ch

    def tokenize(self):
        tokens = []

        while self.i < len(self.src):
            ch = self.peek()

            if ch.isspace():
                self.advance()
                continue

            # number
            if ch.isdigit():
                num = ""
                while self.peek() and self.peek().isdigit():
                    num += self.advance()
                tokens.append(Token(TT.NUMBER, int(num), self.line, self.col))
                continue

            # string
            if ch == '"':
                self.advance()
                s = ""
                while self.peek() != '"':
                    s += self.advance()
                self.advance()
                tokens.append(Token(TT.STRING, s, self.line, self.col))
                continue

            # identifier / keyword
            if ch.isalpha():
                ident = ""
                while self.peek() and self.peek().isalnum():
                    ident += self.advance()

                if ident == "spit":
                    tokens.append(Token(TT.SPIT, ident, self.line, self.col))
                else:
                    tokens.append(Token(TT.IDENT, ident, self.line, self.col))
                continue

            # symbols
            if ch == "+":
                self.advance()
                tokens.append(Token(TT.PLUS, "+", self.line, self.col))
                continue

            if ch == "-":
                self.advance()
                tokens.append(Token(TT.MINUS, "-", self.line, self.col))
                continue

            if ch == "*":
                self.advance()
                tokens.append(Token(TT.MUL, "*", self.line, self.col))
                continue

            if ch == "/":
                self.advance()
                tokens.append(Token(TT.DIV, "/", self.line, self.col))
                continue

            if ch == "=":
                self.advance()
                tokens.append(Token(TT.ASSIGN, "=", self.line, self.col))
                continue

            if ch == "(":
                self.advance()
                tokens.append(Token(TT.LPAREN, "(", self.line, self.col))
                continue

            if ch == ")":
                self.advance()
                tokens.append(Token(TT.RPAREN, ")", self.line, self.col))
                continue

            raise Exception(f"Unknown char: {ch}")

        tokens.append(Token(TT.EOF, None, self.line, self.col))
        return tokens
