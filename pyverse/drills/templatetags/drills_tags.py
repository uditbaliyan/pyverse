from django import template

from pyverse.drills.quizitems import options

register = template.Library()


@register.filter(name="drill_options")
def drill_options(question):
    return options(question)
