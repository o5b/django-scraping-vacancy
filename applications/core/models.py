import os
import uuid
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.deconstruct import deconstructible
from model_utils.managers import QueryManager


class Date(models.Model):
    """
    Дата / абстрактный класс
    """

    created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    modified = models.DateTimeField(
        verbose_name='Дата изменения',
        auto_now=True,
    )

    class Meta:
        abstract = True
        ordering = ['-created']


class Common(Date):
    """
    Общий / абстрактный класс
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        PUBLISHED = 'published', 'Опубликовано'

    status = models.CharField(
        verbose_name='Статус',
        choices=Status.choices,
        default=Status.PUBLISHED,
        max_length=50,
    )

    objects = models.Manager()
    drafted = QueryManager(status=Status.DRAFT)
    published = QueryManager(status=Status.PUBLISHED)

    class Meta(Date.Meta):
        abstract = True


class Single(models.Model):
    """
    Ограничивает класс одним инстансом
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk and self.__class__.objects.exists():
            raise ValidationError('Может быть только один объект этого класса')
        return super().save(*args, **kwargs)


@deconstructible
class PathAndRename:
    """
    Класс используется для генерации уникальных имён в FileField, ImageField
    Ex.: upload_to=PathAndRename('app/model/field')
    """

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        _, extension = os.path.splitext(filename)
        filename = f'{uuid.uuid4().hex}{extension}'
        return os.path.join(self.path, filename)
