from django.contrib import admin
from .models import Topic, Word, Profile


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "key", "icon", "order")


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("emoji", "en", "uz", "ru", "de", "topic")
    list_filter = ("topic",)
    search_fields = ("en", "uz")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "stars", "correct")