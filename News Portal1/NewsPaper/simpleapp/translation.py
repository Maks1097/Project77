from .models import Category, New
from modeltranslation.translator import register, TranslationOptions


@register(New)
class NewTranslationOptions(TranslationOptions):
    fields = ('name', 'news')


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', )