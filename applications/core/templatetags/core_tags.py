from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def verbose_name(obj, field):
    return obj._meta.get_field(field).verbose_name


@register.filter()
def highlight_yellow(text, value):
    if text is not None:
        text = str(text)
        src_str = re.compile(value, re.IGNORECASE)
        str_replaced = src_str.sub(f"<span class=\"highlight\">{value}</span>", text)
    else:
        str_replaced = ''
    return mark_safe(str_replaced)


@register.filter
def get_youtube_id(value):
    pattern = r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})'
    g = re.search(pattern, value)
    if g:
        return g.groups()[0]
    return value


@register.filter
def ru_plural(value, variants):
    """
    Множественные окончания для русских слов.

    Пример:
        1 подписчик
        3 подписчика
        20 подписчиков

        {{ total_followers|ru_plural:'подписчик,подписчика,подписчиков' }}
    """

    variants = variants.split(',')
    value = abs(int(value))

    if value % 10 == 1 and value % 100 != 11:
        variant = 0
    elif value % 10 >= 2 and value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20):
        variant = 1
    else:
        variant = 2

    return variants[variant]
