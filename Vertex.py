class Vertex:

    def __init__(self, arg, **kwargs):
        if isinstance(arg, Vertex):
            self.id = arg.id
        else:
            self.id = str(arg)

    def getId(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __add__(self, other):
        return Vertex(self.id + '+' + other.id)

    def __str__(self):
        return "'%s'" % self.id

    def __hash__(self):
        return hash(self.id)