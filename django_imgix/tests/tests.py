from django.template import Context, Template
from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from imgix import UrlBuilder

from .. import get_imgix_url


def render_template(string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)


class GeneralImgixTests(TestCase):
    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    def test_correct_url_is_generated(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg"
            )

    def test_templatetag_escapes_url(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.jpg' w=600 h=400 %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?h=400&amp;w=600"
            )

    def test_arguments_are_used_correctly(self):
        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = get_imgix_url('media/image/image_0001.jpg', h=100, w=250, lossless=1, auto='format')
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=100&lossless=1&w=250"
            )

    def test_no_https(self):

        domains = 'test1.imgix.net'
        https = False

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_HTTPS=https):
            rendered = get_imgix_url('media/image/image_0001.jpg')
            self.assertEqual(
                rendered,
                "http://test1.imgix.net/media/image/image_0001.jpg"
            )

    def test_sharding(self):

        domains = [
            'test1.imgix.net',
            'test2.imgix.net',
            'test3.imgix.net',
        ]

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = get_imgix_url('media/image/image_0001.jpg')
            self.assertIn(
                rendered,
                [
                    "https://test1.imgix.net/media/image/image_0001.jpg",
                    "https://test2.imgix.net/media/image/image_0001.jpg",
                    "https://test3.imgix.net/media/image/image_0001.jpg",
                ]
            )

    def test_sign_key(self):

        domains = 'test1.imgix.net'
        key = '1234test'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_SIGN_KEY=key):
            rendered = get_imgix_url('media/image/image_0001.jpg')
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?s=3ffb2810efc98cca7de5cd9c8ee6aec1"
            )

    def test_alias_as_unnamed_argument(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            rendered = get_imgix_url('media/image/image_0001.jpg', 'alias_one')
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=350&w=150"
            )

    def test_alias_as_named_argument(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            rendered = get_imgix_url('media/image/image_0001.jpg', alias='alias_one')
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=350&w=150"
            )


    def test_alias_as_unnamed_argument_with_other_arguments(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            rendered = get_imgix_url(
                'media/image/image_0001.jpg',
                'alias_one',
                w=111,
                h=222,
                auto='override'
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=override&h=222&w=111"
            )


    def test_alias_as_named_argument_with_other_arguments(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            rendered = get_imgix_url(
                'media/image/image_0001.jpg',
                alias='alias_one',
                w=111,
                h=222,
                auto='override',
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=override&h=222&w=111"
            )


    def test_missing_alias_gives_useful_error(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_one': {'w': 150, 'h': 350, 'auto': 'format'},
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=aliases):
            try:
                rendered = get_imgix_url(
                    'media/image/image_0001.jpg',
                    alias='alias_two',
                    w=111,
                    h=222,
                    auto='override'
                )
            except ImproperlyConfigured as e:
                self.assertEqual(
                    str(e),
                    "Alias alias_two not found in IMGIX_ALIASES"
                )


    def test_no_aliases_specified_gives_useful_error(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_ALIASES=None):
            try:
                rendered = get_imgix_url(
                    'media/image/image_0001.jpg',
                    alias='alias_two',
                    w=111,
                    h=222,
                    auto='override'
                )
            except ImproperlyConfigured as e:
                self.assertEqual(
                    str(e),
                    "No aliases set. Please set IMGIX_ALIASES in settings.py"
                )


    def test_wh_argument(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = get_imgix_url(
                'media/image/image_0001.jpg',
                wh='1024x768',
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?h=768&w=1024"
            )



    def test_wh_argument_overrides_w_and_h(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = get_imgix_url(
                'media/image/image_0001.jpg',
                wh='1024x768',
                w=111,
                h=222,
                auto='format'
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=768&w=1024"
            )


    def test_wh_with_h_0_argument_overrides_w_but_not_h(self):
        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = get_imgix_url(
                'media/image/image_0001.jpg',
                wh='1024x0',
                w=111,
                h=222,
                auto='format'
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=222&w=1024"
            )


    def test_wh_with_w_0_argument_overrides_h_but_not_w(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = get_imgix_url(
                'media/image/image_0001.jpg',
                wh='0x768',
                w=111,
                h=222,
                auto='format'
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=768&w=111"
            )


    def test_wh_with_w_0_and_h_0_arguments_does_nothing(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains):
            rendered = get_imgix_url(
                'media/image/image_0001.jpg',
                wh='0x0',
                w=111,
                h=222,
                auto='format'
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?auto=format&h=222&w=111"
            )

    def test_web_proxy_setting_keeps_full_url(self):
        domains = 'test1.imgix.net'
        key = '1234key'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True,
                           IMGIX_SIGN_KEY=key):
            rendered = get_imgix_url(
                'i.imgur.net/media/image/image_0001.jpg',
                fm='png',
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/i.imgur.net/media/image/image_0001.jpg?fm=png&s=e999c394eb69bad44b3f605fcf96f4bf"
            )


# Tests related to the IMGIX_DETECT_FORMAT option
class DetectFormatTests(TestCase):


    def test_jpg_format_is_automatically_recognised(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True):
            rendered = get_imgix_url('media/image/image_0001.jpg')
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?fm=jpg"
            )


    def test_jpeg_format_is_automatically_recognised(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True):
            rendered = get_imgix_url('media/image/image_0001.jpeg')
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpeg?fm=jpg"
            )


    def test_png_format_is_automatically_recognised(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True):
            rendered = render_template(
                "{% load imgix_tags %}"
                "{% get_imgix 'media/image/image_0001.png' %}"
            )
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.png?fm=png"
            )


    def test_gif_format_is_automatically_recognised(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True):
            rendered = get_imgix_url('media/image/image_0001.gif')
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.gif?fm=gif"
            )


    def test_webp_format_is_automatically_recognised(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True):
            rendered = get_imgix_url('media/image/image_0001.webp')
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.webp?fm=webp"
            )


    def test_fm_in_alias_overrides_detect_format(self):

        domains = 'test1.imgix.net'
        aliases = {
            'alias_fm': {'fm': 'png'}
        }

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True,
                           IMGIX_ALIASES=aliases):
            rendered = get_imgix_url('media/image/image_0001.jpg', alias='alias_fm')
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?fm=png"
            )


    def test_inline_fm_argument_overrides_detect_format(self):

        domains = 'test1.imgix.net'

        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_DETECT_FORMAT=True):
            rendered = get_imgix_url('media/image/image_0001.jpg', fm='png')
            self.assertEqual(
                rendered,
                "https://test1.imgix.net/media/image/image_0001.jpg?fm=png"
            )


    def test_web_proxy_without_sign_key_raises(self):
        domains = 'test1.imgix.net'
        with self.settings(IMGIX_DOMAINS=domains,
                           IMGIX_WEB_PROXY_SOURCE=True,
                           IMGIX_SIGN_KEY=None):

            with self.assertRaises(ImproperlyConfigured):
                get_imgix_url('media/image/image_0001.jpg')


    def test_alternative_source(self):
        source_1_domains = 'test1.imgix.net'
        source_2_domains = 'test2.imgix.net'

        custom_settings = {
            'IMGIX_SOURCES': {
                '': {
                    'domains': source_1_domains,
                },
                'proxy': {
                    'domains': source_2_domains,
                    'web_proxy': True,
                    'sign_key': 'mock-sign-key',
                }
            }
        }

        with self.settings(**custom_settings):
            main_url = get_imgix_url('media/image/image_0001.jpg')

            self.assertEqual(
                'https://test1.imgix.net/media/image/image_0001.jpg',
                main_url
            )

            proxy_url = get_imgix_url('http://www.example.com/image1.jpg', source='proxy')

            self.assertEqual(
                'https://test2.imgix.net/http%3A%2F%2Fwww.example'
                '.com%2Fimage1.jpg?s=565a44b136186478b1f2805e1e7c8e8c',
                proxy_url
            )
