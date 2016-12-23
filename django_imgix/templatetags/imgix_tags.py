from django import template
from django.utils.html import escape

from .. import get_imgix_url, MAIN_SOURCE_KEY


register = template.Library()


@register.simple_tag
def get_imgix(image_url, alias=None, wh=None, source=MAIN_SOURCE_KEY, **kwargs):
    """
    Template tag that returns an Imgix image URL.

    :param image_url: the image URL that will be passed to Imgix
    :param alias: An optional alias name corresponding to a key in IMGIX_ALIASES setting.
    :param wh: An optional string in the format '600x400'.
    :param source: An optional string that determines the source to use. Defaults to the
                   main source.
    :param kwargs: optional, arbitrary number of key-value pairs to override settings
                   and pass to the Imgix API.
                   See https://www.imgix.com/docs/reference
    :returns: An Imgix URL
    """
    return escape(get_imgix_url(image_url, alias=alias, wh=wh, source=source, **kwargs))
