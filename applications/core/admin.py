from django.contrib import admin
from django.utils.html import mark_safe

from . import models


class CommonAdmin(admin.ModelAdmin):
    list_filter = ['status', 'created']
    readonly_fields = ['created', 'modified']
    actions = ['make_published', 'make_drafted']

    def make_published(self, request, queryset):
        queryset.update(status=models.Common.Status.PUBLISHED)

    make_published.short_description = 'Выставить статус "Опубликовано"'

    def make_drafted(self, request, queryset):
        queryset.update(status=models.Common.Status.DRAFT)

    make_drafted.short_description = 'Выставить статус "Черновик"'


class CommonInlineAdmin:
    readonly_fields = ['created', 'modified']


class ThumbAdminMixin:
    image_list = []

    def __init__(self, *args, **kwargs):
        if self.image_list:
            for image in self.image_list:
                name = f'thumb_{image}'

                def fn(obj):
                    photo = getattr(obj, image)
                    if not photo:
                        return '—'
                    return mark_safe(f'<img src="{photo.url}" width="100">')

                fn.short_description = 'Превью'

                setattr(self, name, fn)
        super().__init__(*args, **kwargs)
