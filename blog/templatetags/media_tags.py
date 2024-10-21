from django import template

register = template.Library()

@register.filter
def get_media(value):
    # Adjust the logic as needed for your media URL structure
    return f"/media/{value}"