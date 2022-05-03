# encoding=utf-8
from django.shortcuts import HttpResponse, render, reverse, redirect
from django.urls import path, re_path
from django import forms
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models import Q
from django.http.request import QueryDict
from django.utils.safestring import mark_safe
import functools
from types import FunctionType


class Row(object):
    """封装数据"""
    def __init__(self, data_list, option, query_dict):
        """初始化方法"""
        self.data_list = data_list
        self.option = option
        self.query_dict = query_dict

    def __iter__(self):
        # 原始搜索条件
        origin_search_list = self.query_dict.getlist(self.option.field)
        yield '<div class="row">'
        yield '<div class="whole">'

        toal_query_dict = self.query_dict.copy()
        toal_query_dict._mutable = True
        if origin_search_list:
            toal_query_dict.pop(self.option.field)
            yield '<a href="?%s">全部</a>' % toal_query_dict.urlencode()
        else:
            # 没有选择则全部加上active属性
            yield '<a href="?%s" class="active">全部</a>' % toal_query_dict.urlencode()

        yield '</div>'
        yield '<div class="others">'

        for item in self.data_list:
            val = self.option.get_value(item)
            text = self.option.get_text(item)

            query_dict = self.query_dict.copy()
            query_dict._mutable = True
            # 单选
            if self.option.is_multi == False:
                if str(val) in origin_search_list:
                    # 已经存在，再次点击去掉该条件
                    query_dict.pop(self.option.field)
                    yield ' <a href="?%s" class="active" >%s</a>' % (query_dict.urlencode(), text)
                else:
                    query_dict[self.option.field] = val
                    yield ' <a href="?%s">%s</a>' % (query_dict.urlencode(), text)
            else:
                # 已经选中
                multi_val_list = query_dict.getlist(self.option.field)
                if str(val) in multi_val_list:
                    multi_val_list.remove(str(val))
                    _class = 'active'
                    # query_dict.setlist(self.option.field, multi_val_list)
                    # yield ' <a href="?%s" class="active" >%s</a>' % (query_dict.urlencode(), text)
                else:
                    multi_val_list.append(str(val))
                    _class = ''

                query_dict.setlist(self.option.field, multi_val_list)
                yield ' <a href="?%s" class="%s">%s</a>' % (query_dict.urlencode(), _class, text)

        yield '</div>'
        yield '</div>'


class Option(object):
    """配置类"""
    def __init__(self, field, condition=None, is_choice=False, text_func=None, value_func=None, is_multi=False):
        self.field = field
        self.is_choice = is_choice
        self.text_func = text_func
        self.value_func = value_func
        self.is_multi = is_multi
        if not condition:
            self.condition = {}
        else:
            self.condition = condition

    def get_query_set(self, _field, model_class, query_dict):
        """获取指定字段的值"""
        if isinstance(_field, (ForeignKey, ManyToManyField)):
            # 跨表查询
            row = Row(_field.related_model.objects.filter(**self.condition), self, query_dict)
        else:
            # 查询model_class
            if self.is_choice:
                row = Row(_field.choices, self, query_dict)
            else:
                row = Row(model_class.objects.filter(**self.condition), self, query_dict)

        return row

    def get_text(self, item):
        """执行配置中的函数"""
        if self.text_func:
            return self.text_func(item)
        return str(item)

    def get_value(self, item):
        """"""
        if self.value_func:
            return self.value_func(item)

        if self.is_choice:
            return item[0]
        return item.pk


class BaseModelForm(forms.ModelForm):
    """modelform 基类"""

    def __new__(cls, *args, **kwargs):
        # cls.base_fields是一个元组，格式为：OrderedDict([('字段名', 字段的对象), ()])
        # print(cls.base_fields)

        for field_name in cls.base_fields:
            # 每个字段的对象
            field_obj = cls.base_fields[field_name]
            # 添加属性
            field_obj.widget.attrs.update({'class': 'form-control'})

        return forms.ModelForm.__new__(cls)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(self, *args, **kwargs)
    #     for field in iter(self.fields):
    #         print("************", field)
    #         if 'class' in self.fields[field].widget.attrs:
    #             if self.fields[field].widget.attrs['class'] == 'customer-form-radio':
    #                 self.fields[field].widget.attrs.update({
    #                     'class': 'customer-form-radio'
    #                 })
    #         else:
    #             self.fields[field].widget.attrs.update({
    #                 'class': 'form-control'
    #             })


class StarkConfig(object):
    """默认配置"""
    order_by = []
    list_display = []
    model_form_class = None
    action_list = []
    search_list = []
    list_filter = []

    def __init__(self, model_class, site):
        """初始化方法"""
        self.model_class = model_class
        self.site = site
        self.back_condition_key = "_filter"

    def multi_del(self, request):
        """批量删除操作"""
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(pk__in=pk_list).delete()
        return HttpResponse("删除成功")

    multi_del.text = '批量删除'

    def multi_ini(self, request):
        """批量初始化操作"""

    multi_ini.text = '批量初始化'

    def get_action_list(self):
        """获取所有批量操作的行为"""
        val = []
        # if not self.action_list:
        #     self.action_list = [self.multi_del, self.multi_ini]
        val.extend(self.action_list)
        return val

    def get_list_filter(self):
        """获取组合搜索的条件"""
        return self.list_filter

    def get_search_list(self):
        """获取搜索字段"""
        val = []
        val.extend(self.search_list)
        return val

    def get_action_dict(self):
        """获取所有批量操作的行为"""
        val = {}
        for item in self.action_list:
            val[item.__name__] = item
        return val

    def get_order_by(self):
        """获取所有要排序的字段"""
        return self.order_by

    def get_list_display(self):
        """获取所有要展示的字段"""
        return self.list_display

    def get_search_condition(self, request):
        """拼接好搜索条件"""
        search_list = self.get_search_list()
        q = request.GET.get('q', '')
        conn = Q()
        conn.connector = "OR"
        if q:
            for field in search_list:
                conn.children.append(('%s__contains' % field, q))
        return search_list, q, conn

    def get_add_btn(self):
        """返回添加按钮"""
        return mark_safe("<div style='margin:5px;'><a href='%s' class='btn btn-success'>添加</a></div>" \
                         % self.reverse_add_url())

    def get_model_form_class(self):
        """获取modelform"""
        if self.model_form_class:
            return self.model_form_class

        # 没有的话才自定义modelform
        class AddModelForm(BaseModelForm):
            """通用的modelform类，添加页面使用"""
            class Meta:
                model = self.model_class
                fields = "__all__"
        return AddModelForm

    def display_edit(self, row=None, header=False):
        """定制编辑功能"""
        if header:
            return "编辑"
        return mark_safe("<a href='%s'><i class='fa fa-edit' aria-hidden='true'></i></a>" \
                         % self.reverse_edit_url(row))

    def display_del(self, row=None, header=False):
        """定制删除功能"""
        if header:
            return "删除"
        return mark_safe("<a href='%s'><i class='fa fa-trash-o' aria-hidden='true'></i></a>"
                         % self.reverse_del_url(row))

    def display_edit_del(self, row=None, header=False):
        """定制编辑|删除功能"""
        if header:
            return "操作"
        return mark_safe("<a href='%s'><i class='fa fa-edit' aria-hidden='true'></i></a> |" \
                         " <a href='%s'><i class='fa fa-trash-o' aria-hidden='true'></i></a>"\
                         % (self.reverse_edit_url(row), self.reverse_del_url(row)))

    def display_checkbox(self, row=None, header=False):
        """定制checkbox"""
        if header:
            return "选择"
        return mark_safe("<input type='checkbox' name='pk' value='%s'/>" % row.pk)

    def changelist_view(self, request):
        """所有URL的查看列表页面"""
        if request.method == "POST":
            action_name = request.POST.get('action')
            # 先判断action_name是否在action_list中
            print("&&&&&&&&&&&", action_name)

            if action_name not in self.get_action_dict():
                return HttpResponse("非法操作！")
            res = getattr(self, action_name)(request)
            if res:
                return res

        header_list = []
        body_list = []
        list_display = self.get_list_display()
        # #########处理搜索
        search_list, q, conn = self.get_search_condition(request)

        # #########处理组合搜索
        # 组合搜索的条件
        comb_condition = {}
        list_filter = self.get_list_filter()
        list_filter_rows = []
        comb_condition = {}
        for option in list_filter:
            _field = self.model_class._meta.get_field(option.field)
            row = option.get_query_set(_field, self.model_class, request.GET)
            list_filter_rows.append(row)

            # 外键需要加上__id
            element = self.request.GET.getlist(option.field)
            if element:
                comb_condition["%s__in" % option.field] = element

        print('*********comb_condition', comb_condition)
        # #########处理分页
        from stark.utils.pagination import Pagination
        total_count = self.model_class.objects.filter(conn).filter(**comb_condition).count()
        query_params = request.GET.copy()
        query_params._mutable = True
        page = Pagination(request.GET.get('page'), total_count, request.path_info, query_params, per_page=5)

        query_set = self.model_class.objects.filter(conn).filter(**comb_condition)\
                        .order_by(*self.get_order_by()).distinct()[page.start:page.end]

        # print('**********', query_set)
        # #########处理action
        action_list = self.get_action_list()
        action_list = [{'name': func.__name__, 'text': func.text} for func in action_list]

        # #########处理添加按钮
        add_btn = self.get_add_btn()

        # #########处理表格相关数据
        if list_display:
            for key in list_display:
                # 如果是方法类型
                if isinstance(key, FunctionType):
                    # 函数类型，可以加括号调用，但是self代表的实例要手动传
                    header_list.append(key(self, header=True))
                else:# 字符串类型才从数据库去取
                    header_list.append(self.model_class._meta.get_field(key).verbose_name)
        else:
            # list_display为空，则展示model类
            header_list.append(self.model_class._meta.model_name)

        for row in query_set:
            if not list_display:
                body_list.append([row, ])
                continue
            row_list = []
            for key in list_display:
                if isinstance(key, FunctionType):
                    val = key(self, row=row)
                else:
                    val = getattr(row, key)
                row_list.append(val)
            body_list.append(row_list)

        return render(request, "stark/changelist.html",
                      {'header_list': header_list, 'body_list': body_list,
                       'add_btn': add_btn, 'action_list': action_list,
                       'search_list': search_list, 'q': q, 'page_html': mark_safe(page.page_html),
                       'list_filter_rows': list_filter_rows})

    def add_view(self, request):
        """所有添加页面，通过modelform实现"""
        model_form_class = self.get_model_form_class()
        if request.method == "GET":
            form = model_form_class()
            return render(request, 'stark/change.html', {'form': form})
        else:
            form = model_form_class(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.reverse_list_url())

    def change_view(self, request, pk):
        """所有URL的修改列表页面"""
        obj = self.model_class.objects.filter(pk=pk).first()
        if not obj:
            # 数据不存在
            return HttpResponse('数据不存在')

        ModelFormClass = self.get_model_form_class()
        if request.method == "GET":
            form = ModelFormClass(instance=obj)
            return render(request, "stark/change.html", {'form': form})

        form = ModelFormClass(instance=obj, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(self.reverse_list_url())
        # 校验失败的话返回错误信息
        return render(request, "stark/change.html", {'form': form})
        # return HttpResponse('StarkConfig.change_view')

    def delete_view(self, request, pk):
        """所有URL的删除页面"""
        cancel_url = self.reverse_list_url()
        if request.method == "GET":
            return render(request, 'stark/delete.html', {
                'cancel_url': cancel_url,
            })
        self.model_class.objects.filter(pk=pk).delete()
        return redirect(cancel_url)

    def wrapper(self, func):
        """预留的钩子函数"""
        @functools.wraps(func)
        def inner(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)
        return inner

    def get_urls(self):
        # 主键不一定叫id，但是pk一定代表主键
        info = self.model_class._meta.app_label, self.model_class._meta.model_name
        urlpatterns = [
            path(r"list/", self.wrapper(self.changelist_view), name="%s_%s_changelist" % info),
            path(r"add/", self.wrapper(self.add_view), name="%s_%s_add" % info),
            re_path(r"^(?P<pk>\d+)/change/", self.wrapper(self.change_view), name="%s_%s_change" % info),
            re_path(r"^(?P<pk>\d+)/del/", self.wrapper(self.delete_view), name="%s_%s_del" % info),
        ]

        # 支持扩展url
        extra = self.extra_url()
        if extra:
            urlpatterns.extend(extra)
        return urlpatterns

    def extra_url(self):
        """自行扩展的url钩子函数"""
        pass

    def reverse_edit_url(self, row):
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        namespace = self.site.namespace
        name = "%s:%s_%s_change" % (namespace, app_label, model_name)
        edit_url = reverse(name, kwargs={'pk': row.pk})
        # print('xxxxxxxxxxxxxxxxxx', edit_url)

        if self.request.GET:
            param_str = self.request.GET.urlencode()
            new_query_dict = QueryDict(mutable=True)
            new_query_dict['_filter'] = param_str
            edit_url = "%s?%s" % (edit_url, new_query_dict.urlencode())

        return edit_url

    def reverse_del_url(self, row):
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        namespace = self.site.namespace
        name = "%s:%s_%s_del" % (namespace, app_label, model_name)
        del_url = reverse(name, kwargs={'pk': row.pk})

        if self.request.GET:
            param_str = self.request.GET.urlencode()
            new_query_dict = QueryDict(mutable=True)
            new_query_dict['_filter'] = param_str
            del_url = "%s?%s" % (del_url, new_query_dict.urlencode())

        return del_url

    def reverse_add_url(self):
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        namespace = self.site.namespace
        name = "%s:%s_%s_add" % (namespace, app_label, model_name)
        add_url = reverse(name)
        # print('xxxxxxxxxxxxxxxxxx', add_url)

        if self.request.GET:
            param_str = self.request.GET.urlencode()
            new_query_dict = QueryDict(mutable=True)
            new_query_dict['_filter'] = param_str
            add_url = "%s?%s" % (add_url, new_query_dict.urlencode())
        return add_url

    def reverse_list_url(self):
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        namespace = self.site.namespace
        name = "%s:%s_%s_changelist" % (namespace, app_label, model_name)
        list_url = reverse(name)

        origin_condition = self.request.GET.get(self.back_condition_key)
        if not origin_condition:
            return list_url

        list_url = "%s?%s" % (list_url, origin_condition)
        return list_url

    @property
    def urls(self):
        return self.get_urls()


class AdminSite(object):
    """注册类"""
    def __init__(self):
        self._registry = {}
        self.app_name = "stark"
        self.namespace = "stark"

    def register(self, model_class, stark_config=None):
        """注册model"""
        if not stark_config:
            stark_config = StarkConfig

        # stark_config代表一个类名，可以实例化
        self._registry[model_class] = stark_config(model_class, self)
        # print(self._registry)

    def x1(self):
        return HttpResponse('x1')

    def get_urls(self):
        urlpatterns = []
        # urlpatterns.append(path(r'x1/', self.x1))
        # urlpatterns.append(path(r'x1/', ([
        #                                     path(r'add/', self.x1),
        #                                     path(r'change/', self.x1),
        #                                     path(r'del/', self.x1),
        #                                     path(r'edit/', self.x1),
        #                                  ], None, None)))

        for k, v in self._registry.items():
            # k=models.UserInfo, v=StrkConfig(models.UserInfo),封装：model_class=UserInfo， site=site对象
            # k=models.Role, v=RoleConfig(models.Role),封装：model_class=Role， site=site对象
            app_label = k._meta.app_label
            model_name = k._meta.model_name
            urlpatterns.append(path(r"%s/%s/" % (app_label, model_name),
                                    (v.urls, None, None)))
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace


# 单例模式
site = AdminSite()
