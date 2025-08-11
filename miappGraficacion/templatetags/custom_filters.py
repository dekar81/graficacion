# miappGraficacion/miappGraficacion/templatetags/custom_filters.py
from django import template
from urllib.parse import urlencode

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un valor de un diccionario o devuelve cadena vacía si no existe"""
    return dictionary.get(key, '')

@register.simple_tag
def param_replace(request, **kwargs):
    """
    Mantiene los parámetros GET existentes mientras reemplaza los especificados
    """
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value
        else:
            params.pop(key, None)
    return params.urlencode()