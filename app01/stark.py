from stark.service.stark import site, StarkConfig, Option, Row
from app01 import models


class DistinctNameOption(Option):
    """支持字段去重的配置类"""
    def get_query_set(self, _field, model_class, query_dict):
        """获取指定字段的值"""
        row = Row(model_class.objects.filter(**self.condition).values_list('name').distinct(), self, query_dict)
        return row


class DepartConfig(StarkConfig):

    list_display = [StarkConfig.display_checkbox, 'id', 'name', 'tel',
                    'user', StarkConfig.display_edit_del]
    action_list = [StarkConfig.multi_del, StarkConfig.multi_ini]
    search_list = ['name', 'tel', 'user__title']
    list_filter = [
        DistinctNameOption('name', value_func=lambda x: x[0], text_func=lambda x: x[0]),
        # Option('user', text_func=lambda x: x.title, value_func=lambda x: x.title),
        Option('user', text_func=lambda x: x.title, ),
        Option('level', is_choice=True, text_func=lambda x: x[-1], is_multi=True),
        Option('tel', text_func=lambda x: x.tel, value_func=lambda x: x.tel),
    ]


class UserInfoConfig(StarkConfig):
    search_list = ['title']
    list_display = [StarkConfig.display_checkbox, 'id', 'title', StarkConfig.display_edit]

    def get_add_btn(self):
        pass


site.register(models.UserInfo, UserInfoConfig)
site.register(models.Depart, DepartConfig)
