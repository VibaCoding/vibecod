import os
import traceback

from .env import Env


class Interpreter:
    def __init__(self):
        self.globals = Env()
        self.modules = {}

    def load_module(self, name: str):
        if name in self.modules:
            return self.modules[name]

        module = Env()

        if name == "math":
            module.define("add", lambda x: x[0] + x[1])
            module.define("mul", lambda x: x[0] * x[1])

        if name == "io":
            module.define("spit", lambda x: print(x[0]))

        self.modules[name] = module
        return module

    def use(self, name: str):
        self.globals.vars[name] = self.load_module(name)


# ---------------- CORE EXEC ----------------

def run_code(code: str, interp=None, filename="<memory>"):
    interp = interp or Interpreter()

    try:
        code = code.strip()

        if code.startswith("use "):
            interp.use(code.split(" ", 1)[1])
            print("MODULE LOADED:", code.split(" ", 1)[1])
            return

        print("VIBE EXEC:", code)

    except Exception as e:
        print(f"[VIBE ERROR] in {filename}: {e}")
        traceback.print_exc()


def run_file(path: str, interp=None):
    interp = interp or Interpreter()

    if not os.path.exists(path):
        print(f"[VIBE ERROR] file not found: {path}")
        return

    ext = os.path.splitext(path)[1]

    # 🟢 PY
    if ext == ".py":
        print(f"[VIBE] running python: {path}")
        os.system(f"python {path}")
        return

    # 🟢 TEXT
    if ext in [".txt", ".md"]:
        print(open(path, "r").read())
        return

    # 🟢 ZIP
    if ext == ".zip":
        import zipfile
        with zipfile.ZipFile(path) as z:
            print("\n".join(z.namelist()))
        return

    # 🔥 VIBE LANGUAGE (MAIN FEATURE)
    if ext == ".vibe":
        try:
            with open(path, "r") as f:
                code = f.read()

            return run_code(code, interp, filename=path)

        except Exception as e:
            print(f"[VIBE RUNTIME ERROR] {path}: {e}")
            return

    print(f"[VIBE ERROR] unsupported file type: {ext}")
