from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    moblie = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name  # 复数形式
