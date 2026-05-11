#!/usr/bin/env python3
import sys
import argparse
from .core import run_code, run_file, Interpreter, Lexer, Parser

def main():
    parser = argparse.ArgumentParser(description="VIBEcod Language")
    parser.add_argument("-c", "--command", help="Execute one line of VIBE code")
    parser.add_argument("file", nargs="?", help="VIBE source file")
    parser.add_argument("-v", "--version", action="store_true", help="Show version")
    
    args = parser.parse_args()
    
    if args.version:
        print("VIBEcod 2.0.0")
        return
    
    if args.command:
        # Режим "как у clang": vibecod -c 'spit("hello")'
        run_code(args.command)
    elif args.file:
        run_file(args.file)
    else:
        # REPL режим
        print("\033[96mVIBEcod REPL v2.0\033[0m")
        interp = Interpreter()
        while True:
            try:
                line = input("\033[93mvibe> \033[0m")
            except (EOFError, KeyboardInterrupt):
                print("\nstay vibe")
                break
            if line.strip() in ('exit', 'quit'):
                break
            if not line.strip():
                continue
            try:
                lexer = Lexer(line)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                if ast.statements:
                    last = ast.statements[-1]
                    from .core import ExprStmt
                    if isinstance(last, ExprStmt):
                        res = interp.eval(last.expr, interp.globals)
                        if res is not None:
                            print(f"\033[90m=> {interp._str(res)}\033[0m")
                    else:
                        interp.exec(last, interp.globals)
            except Exception as e:
                print(f"\033[91m{e}\033[0m")

if __name__ == "__main__":
    main()
