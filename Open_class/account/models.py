from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    teacher_name = models.CharField(max_length = 6) # 老師名字
    teacher_subject = models.CharField(max_length = 10) # 老師教的科目
    teacher_department = models.CharField(max_length = 3)# 老師教的部門
    def __str__(self):
        return self.teacher_name

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'teacher_name', 'teacher_department', 'teacher_subject', 'email', 'is_superuser', 'last_login']
    search_fields = ('teacher_name', 'teacher_subject', 'teacher_department')
