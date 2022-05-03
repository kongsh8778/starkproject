def func():
    pass


class Foo:
    def display(self):
        pass


print(func)
f = Foo()
# 类调用是方法函数类型
print(Foo.display)
# 类对象调用是方法类型
print(f.display)


from types import MethodType, FunctionType


def check(arg):
    if isinstance(arg, MethodType):
        print("方法类型")
    elif isinstance(arg, FunctionType):
        print("函数类型")
    else:
        print('类型错误')


check(func)
check(Foo.display)
check(Foo().display)
