from django import template

register = template.Library()

@register.simple_tag
def is_heritage_page(request_path):
    """Check if the current path is a heritage-related page"""
    return request_path.startswith('/heritage/')