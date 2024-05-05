from django.contrib import admin
from .models import Category, New
from modeltranslation.admin import TranslationAdmin


class NewTranslationAdmin(TranslationAdmin):
    model = New


class CategoryAdmin(TranslationAdmin):
    model = Category


admin.site.register(Category)
admin.site.register(New)