from django.db import models


class Role(models.Model):
    """用户信息表"""
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title
