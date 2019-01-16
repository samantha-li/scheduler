from django.template.defaulttags import register
from django import template

@register.filter
def lookup(value, arg):
    return value[arg]

@register.filter
def add(arg1, arg2):
    return arg1 + arg2
