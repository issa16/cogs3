from django import template

register = template.Library()


@register.simple_tag
def gb_to_tb(gb):
    if gb:
        return f'{gb / 1024.0:.3f} TB'
    else:
        return ''


@register.simple_tag
def duration(td):
    if td:
        total_seconds = int(td.total_seconds())

        days = total_seconds // 86400
        remaining_hours = total_seconds % 86400
        remaining_minutes = remaining_hours % 3600
        hours = remaining_hours // 3600
        minutes = remaining_minutes // 60

        days_str = f'{days}d ' if days else ''
        hours_str = f'{hours}h ' if hours else ''
        minutes_str = f'{minutes}m ' if minutes else ''

        return f'{days_str}{hours_str}{minutes_str}'
    else:
        return 0


@register.simple_tag
def parse_pi_name(pi):
    try:
        name, position, email = pi.split(',')
        institution = email.split('@')[1]
        institution = institution.split('.')[0]
        institution = institution.title()
        return f'{name} ({institution})'
    except Exception:
        return pi
