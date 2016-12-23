__author__ = 'daniel.kirov'

import re
try:
    from urlparse import urlparse
except ImportError:
    # Python 3 location
    from urllib.parse import urlparse

from django.utils import six
from django.template import TemplateSyntaxError
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import imgix

from .utils import pick, merge_dicts


WH_PATTERN = re.compile(r'(\d+)x(\d+)$')

FM_PATTERN = re.compile(r'([^\?]+)')
FM_MATCHES = {
    'jpg': 'jpg',
    'jpeg': 'jpg',
    'png': 'png',
    'gif': 'gif',
    'jp2': 'jp2',
    'jxr': 'jxr',
    'webp': 'webp',
}

# Sentinel to detect unset setting,
# to be omitted so that imgix-python
# applies it's own defaults.
USE_IMGIX_DEFAULT = {}


SOURCE_DEFAULTS = {
    'domains': (),
    'use_https': True,
    'sign_key': None,
    'shard_strategy': None,
    'format_detect': False,
    'web_proxy': False,
    'sign_with_library_version': False,
    'sign_mode': USE_IMGIX_DEFAULT,
    'shard_strategy': USE_IMGIX_DEFAULT,
}

MAIN_SOURCE_KEY = ''


def omit_use_default_keys(_dict):
    return dict(
        (k, v)
        for k, v in _dict.items()
        if v is not USE_IMGIX_DEFAULT
    )


def get_sources():
    # For compatibility with single-source settings.
    main_source = {
        'domains': getattr(settings, 'IMGIX_DOMAINS', ()),
        'use_https': getattr(settings, 'IMGIX_HTTPS', True),
        'sign_key': getattr(settings, 'IMGIX_SIGN_KEY', None),
        'format_detect': getattr(settings, 'IMGIX_DETECT_FORMAT', False),
        'web_proxy': getattr(settings, 'IMGIX_WEB_PROXY_SOURCE', False),
        'sign_with_library_version': getattr(settings, 'IMGIX_SIGN_WITH_LIBRARY_VERSION', False),
        'sign_mode': getattr(settings, 'IMGIX_SIGN_MODE', USE_IMGIX_DEFAULT),
        'shard_strategy': getattr(settings, 'IMGIX_SHARD_STRATEGY', USE_IMGIX_DEFAULT),
    }

    sources = getattr(settings, 'IMGIX_SOURCES', {}).copy()

    # Main source is under the empty string.
    # If a source is already defined there, use that instead of the top-level
    # settings variables.
    sources.setdefault(MAIN_SOURCE_KEY, main_source)

    for source_name, source_opts in sources.items():
        source = merge_dicts(SOURCE_DEFAULTS, source_opts)

        # Validate source.
        if not source['domains']:
            raise ValueError("Missing domains in source {0}".format(source_name))

        if source['web_proxy'] and not source['sign_key']:
            raise ImproperlyConfigured(
                "In order to use a web proxy source, "
                "add a 'sign_key' to source '{0}'".format(source_name)
            )

        # Remove keys where the corresponding value is USE_IMGIX_DEFAULT.
        sources[source_name] = omit_use_default_keys(source)

    return sources


def get_alias(alias):
    aliases = getattr(settings, 'IMGIX_ALIASES', None)

    if not isinstance(aliases, dict):
        raise ImproperlyConfigured(
            "No aliases set. Please set IMGIX_ALIASES in settings.py"
        )

    if alias not in aliases:
        raise ImproperlyConfigured(
            "Alias {0} not found in IMGIX_ALIASES".format(alias)
        )

    return aliases[alias]


def get_fm(image_url):
    _, image_end = image_url.split('.', 1)
    m = FM_PATTERN.match(image_end)
    if m:
        fm = m.group(1)
        return FM_MATCHES.get(fm, False)
    else:
        return False


IMGIX_URL_BUILDER_KWARGS = frozenset([
    'domains',
    'sign_mode',
    'sign_with_library_version',
    'use_https',
    'sign_key',
    'shard_strategy',
])


def get_imgix_url(image_url, alias=None, wh=None, source=MAIN_SOURCE_KEY, **kwargs):
    """
    Returns an Imgix image URL.

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

    create_url_opts = merge_dicts(
        get_alias(alias) if alias else {},
        kwargs
    )

    # Has the wh argument been passed? If yes,
    # set w and h arguments accordingly
    if wh:
        create_url_opts.update(parse_wh(wh))

    source_opts = get_sources()[source]

    # Is format detection on? If yes, use the appropriate image format.
    if source_opts['format_detect'] and 'fm' not in create_url_opts:
        fm = get_fm(image_url)
        if fm:
            create_url_opts['fm'] = fm

    # Take only the relative path of the URL if the source is not a Web Proxy Source
    if not source_opts['web_proxy']:
        image_url = urlparse(image_url).path

    # Build the Imgix URL
    builder_kwargs = pick(IMGIX_URL_BUILDER_KWARGS, source_opts)
    builder = imgix.UrlBuilder(**builder_kwargs)
    url = builder.create_url(image_url, create_url_opts)
    return url


def parse_wh(wh):
    size = wh
    if not isinstance(size, six.string_types):
        raise TemplateSyntaxError(
            "Invalid argument type for 'wh': %s" % wh
        )

    m = WH_PATTERN.match(size)

    if not m:
        raise TemplateSyntaxError(
            "%r is not a valid size." % size
        )

    w = int(m.group(1))
    h = int(m.group(2))

    result = {}
    if w > 0:
        result['w'] = w
    if h > 0:
        result['h'] = h

    return result
