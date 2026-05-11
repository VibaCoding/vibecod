import sys
from vibecod.core import run_code

def main():
    if len(sys.argv) < 2:
        print("vibe <file>")
        return

    with open(sys.argv[1]) as f:
        run_code(f.read())

if __name__ == "__main__":
    main()
