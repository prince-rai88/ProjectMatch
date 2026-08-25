from django import template

from matcher.matching import display_name, initials, skill_tags

register = template.Library()


@register.filter
def profile_display_name(profile):
    return display_name(profile)


@register.filter
def profile_initials(profile):
    return initials(profile)


@register.filter
def profile_skill_tags(profile):
    return skill_tags(profile)
