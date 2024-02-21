from django.contrib import admin

# from django.http import HttpResponseRedirect
# from django.shortcuts import render
# from django.urls import reverse
# from django.utils.html import format_html
from api import models

# Register your models here.


@admin.register(models.TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        'user_id',
        'thread',
        'username',
        'first_name',
        'last_name',
        'language_code',
        'is_admin',
        'is_blocked_bot',
        'created_at',
        'updated_at',
        'deep_link',
    ]
    list_filter = [
        'is_blocked_bot',
    ]
    search_fields = ('username', 'user_id')


@admin.register(models.UserAction)
class UserActionAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_id', 'created_at', 'action']


@admin.register(models.Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['user', 'thread_id', 'created_at', 'updated_at']


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'thread_id',
        'user_id',
        'user_username',
        'platform',
        'text_input',
        'text_output',
        'annotations',
        'assistant_id',
        'run_id',
        'topic',
        'created_at',
        'updated_at',
    ]

    @admin.display()
    def user_id(self, obj):
        return obj.thread.user.user_id

    @admin.display()
    def user_username(self, obj):
        return obj.thread.user.username
