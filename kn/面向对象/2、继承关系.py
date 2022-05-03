# encoding=utf-8

class StarkConfig:
    # 类属性
    list_display = []

    def __init__(self, model_class):
        """初始化方法"""
        self.model_class = model_class

    def changelist_view(self, request):
        print(self.list_display)
        return 123


class RoleConfig(StarkConfig):
    # 类属性
    list_display = ['id', "name"]


obj1 = StarkConfig('xiao')
obj2 = RoleConfig('kele')

obj1.changelist_view(1) # []
obj2.changelist_view(2) # ['id', 'name']
