from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def institution(email, is_safe=True):
    try:
        institution = email.split('@')[1]
        institution = institution.split('.')[0]
        institution = institution.title()
        return f'({institution})'
    except Exception:
        return email


@register.filter
def gb_to_tb(gb):
    try:
        return f'{gb / 1000.0:.3f} TB'
    except Exception:
        return 'N/A'


@register.filter
def in_hours(td):
    if td:
        total_seconds = int(td.total_seconds())
        hours = total_seconds / 3600
        return round(hours, 2)
    else:
        return 'N/A'


@register.simple_tag
def efficiency_as_percentage(x, y=1):
    try:
        result = (x / y) * 100
        color = 'black'
        if result >= 70:
            color = 'green'
        elif result >= 50 and result < 70:
            color = 'orange'
        else:
            color = 'red'
        return mark_safe(f"<span style='color:{color};font-weight:bold;'> {result:.2f} %</span>")
    except Exception:
        return ''


@register.simple_tag
def percentage_color(x):
    if x >= 75:
        color = 'red'
    elif x >= 50 and x < 75:
        color = 'blue'
    else:
        color = 'green'
    return mark_safe(f"<span style='color:{color};font-weight:bold;'> {x:.2f} %</span>")
