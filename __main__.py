#!/usr/bin/env python3
import sys
import argparse
import os
import zipfile
from pathlib import Path

from .core import run_code, Interpreter


VERSION = "2.1.0"


# ---------------------------
# FILE HANDLERS
# ---------------------------

def read_file(path: str):
    p = Path(path)
    if not p.exists():
        print(f"[vibe] file not found: {path}")
        return

    ext = p.suffix.lower()

    if ext in (".txt", ".md", ".py", ".cpp", ".c", ".json"):
        print(p.read_text(encoding="utf-8", errors="ignore"))
        return

    print(f"[vibe] unsupported read format: {ext}")


def run_file(path: str):
    p = Path(path)
    if not p.exists():
        print(f"[vibe] file not found: {path}")
        return

    ext = p.suffix.lower()

    if ext == ".py":
        os.system(f"{sys.executable} {path}")
        return

    if ext == ".cpp":
        exe = "/tmp/vibe_cpp_out"
        compile_cmd = f"g++ {path} -o {exe}"
        if os.system(compile_cmd) == 0:
            os.system(exe)
        return

    if ext in (".txt", ".md"):
        print(p.read_text(encoding="utf-8", errors="ignore"))
        return

    if ext == ".vibe":
        run_code(p.read_text(encoding="utf-8", errors="ignore"))
        return

    print(f"[vibe] cannot run: {ext}")


def zip_view(path: str):
    p = Path(path)
    if not p.exists() or p.suffix != ".zip":
        print("[vibe] invalid zip")
        return

    with zipfile.ZipFile(p, 'r') as z:
        for name in z.namelist():
            print(name)


def zip_extract(path: str, target: str = "./extracted"):
    p = Path(path)
    if not p.exists():
        print("[vibe] zip not found")
        return

    with zipfile.ZipFile(p, 'r') as z:
        z.extractall(target)
    print(f"[vibe] extracted to {target}")


# ---------------------------
# VIBE COMMAND WRAPPER
# ---------------------------

def vibe_exec(args):
    if not args:
        print("vibe commands:")
        print("  vibe run <file>")
        print("  vibe read <file>")
        print("  vibe zip view <file.zip>")
        print("  vibe zip extract <file.zip>")
        return

    cmd = args[0]

    if cmd == "run":
        run_file(args[1])
        return

    if cmd == "read":
        read_file(args[1])
        return

    if cmd == "zip":
        if args[1] == "view":
            zip_view(args[2])
        elif args[1] == "extract":
            zip_extract(args[2], args[3] if len(args) > 3 else "./extracted")
        return

    print("[vibe] unknown command")


# ---------------------------
# MAIN
# ---------------------------

def main():
    parser = argparse.ArgumentParser("VIBEcod CLI")
    parser.add_argument("command", nargs="*", help="vibe command")
    parser.add_argument("-v", "--version", action="store_true")

    args = parser.parse_args()

    if args.version:
        print(f"VIBEcod {VERSION}")
        return

    if args.command:
        if args.command[0] == "vibe":
            vibe_exec(args.command[1:])
        else:
            print("[vibe] all commands must start with: vibe")
        return

    # REPL fallback
    print("\033[96mVIBEcod REPL\033[0m")
    interp = Interpreter()

    while True:
        try:
            line = input("vibe> ")
        except (EOFError, KeyboardInterrupt):
            print("\nstay vibe")
            break

        if line.strip() in ("exit", "quit"):
            break

        if not line.strip():
            continue

        try:
            run_code(line, interp)
        except Exception as e:
            print(f"\033[91m{e}\033[0m")


if __name__ == "__main__":
    main()
