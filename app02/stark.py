from stark.service.stark import site, StarkConfig
from django.urls import path
from django.shortcuts import HttpResponse
from app02 import models


class RoleConfig(StarkConfig):
    order_by = ['-id']
    list_display = [StarkConfig.display_checkbox, 'title']
    def extra_url(self):
        data = [
            path(r'xxxx/', self.xxxx),
        ]
        return data

    def xxxx(self):
        return HttpResponse("xxxx")


site.register(models.Role, RoleConfig)
