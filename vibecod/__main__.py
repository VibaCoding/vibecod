#!/usr/bin/env python3
import sys
import argparse
from .core import run_code, Interpreter

def main():
    parser = argparse.ArgumentParser(description="VIBEcod Language")
    parser.add_argument("-c", "--command", help="Execute one line of VIBE code")
    parser.add_argument("file", nargs="?", help="VIBE source file")
    parser.add_argument("-v", "--version", action="store_true", help="Show version")
    
    args = parser.parse_args()
    
    if args.version:
        print("VIBEcod 2.1.1")
        return
    
    # Единый интерпретатор для всего
    interp = Interpreter()
    
    if args.command:
        cmd = args.command.strip()
        # Если это не вызов spit/spit_color и не ключевое слово — обернём в spit
        if not cmd.startswith(('spit', 'spit_color', 'loopit', 'maybe', 'fn', 'vibe', 'yeet', 'florp', 'use')):
            cmd = f'spit({cmd})'
        run_code(cmd, interp=None, print_expr=True)
    elif args.file:
        with open(args.file, 'r') as f:
            run_code(f.read(), interp)
    else:
        print("\033[96mVIBEcod REPL v2.1.1\033[0m")
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
                run_code(line, interp)
            except Exception as e:
                print(f"\033[91m{e}\033[0m")

if __name__ == "__main__":
    main()
