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
        raise RuntimeError(f"Undefined '{name}'")

    def set(self, name, value, line=0, col=0):
        if name in self.consts:
            raise RuntimeError(f"Cannot reassign '{name}'")
        if name in self.vars or not self.parent:
            self.vars[name] = value
        else:
            self.parent.set(name, value, line, col)

    def define(self, name, value, is_const=False):
        self.vars[name] = value
        if is_const:
            self.consts.add(name)
