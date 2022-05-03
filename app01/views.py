from django.shortcuts import render, HttpResponse


def login(request):
    return HttpResponse('login')


def logout(request):
    return HttpResponse('logout')


def test(request):
    """测试页面"""
    from app01 import models
    fk_obj = models.Depart._meta.get_field('user')
    print(fk_obj, type(fk_obj), dir(fk_obj))
    user_info_queryset = fk_obj.related_model.objects.all()
    print(user_info_queryset)
    return HttpResponse('test.....')
    # from django.http.request import QueryDict
    #
    # url_param_str = request.GET.urlencode()
    # query_dict = QueryDict()
    # query_dict._mutable = True
    # query_dict['_filter'] = url_param_str
    #
    # new_param = query_dict.urlencode()
    # print(new_param)


    # # print(request.GET)
    # params = request.GET.copy()
    # params._mutable = True
    # params['k3'] = 'v3'
    # # 设置新值：不能直接通过类似字典的方式设置列表值
    # params.setlist("k4", [11, 22, 33])
    # print(params['k4'])# 只能获取到一个值
    # print(params.getlist('k4')) # 获取到多个值，以列表的形式返回
    #
    # # ########修改原来的值
    # # 不起作用
    # params.getlist('k1').append('ddddddddd')
    # old = params.getlist('k1')
    # old.append('ddddddddd')
    # params.setlist('k1', old)
    #
    # url = params.urlencode()
    # print(url)



    # from app01 import models
    # list_display = ['id', 'title']
    # # ########反射获取到所有字段的verbose_name
    # model_class = models.UserInfo
    # headr_list = []
    # for name in list_display:
    #     headr_list.append(model_class._meta.get_field(name).verbose_name)
    # print(headr_list)
    #
    # # ########反射获取到所有字段的值
    # user_queryset = models.UserInfo.objects.all()
    # for item in user_queryset:
    #     row = []
    #     for key in list_display:
    #         row.append(getattr(item, key))
    # print(row)




