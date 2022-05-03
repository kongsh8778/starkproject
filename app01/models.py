from django.db import models


class UserInfo(models.Model):
    """用户信息表"""
    title = models.CharField(max_length=32, verbose_name="人名")

    def __str__(self):
        return self.title


class UserDetail(models.Model):
    """用户详细信息表"""
    name = models.OneToOneField(to=UserInfo, on_delete=models.CASCADE)
    addres = models.CharField(verbose_name="住址", max_length=32)
    gender_choice = (
        (True, '男'),
        (False, '女')
    )
    gender = models.BooleanField(verbose_name="性别", default=True, choices=gender_choice)


class Publisher(models.Model):
    """出版社表"""
    user = models.ManyToManyField(to=UserInfo)


class Depart(models.Model):
    """部门表"""
    name = models.CharField(max_length=32, verbose_name="部门名称")
    tel = models.CharField(max_length=32, verbose_name="手机号")
    user = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE, verbose_name='负责人')
    level_choice = (
        (1, "高级"),
        (2, "中级"),
        (3, "初级"),
    )
    level = models.IntegerField(choices=level_choice, default=2, verbose_name="级别")

    def __str__(self):
        return self.name
