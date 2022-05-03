class User:
    pass


class Color:
    pass


class Instance:
    def __init__(self, ele):
        self.ele = ele


_registry = {
    User: Instance(User),
    Color: Instance(Color),
}


for k, v in _registry.items():
    print(k, v.ele)