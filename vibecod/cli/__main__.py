import sys
from vibecod.core.interpreter import run_file

def main():
    if len(sys.argv) < 2:
        print("usage: vibe <file>")
        return

    run_file(sys.argv[1])

if __name__ == "__main__":
    main()
