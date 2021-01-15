<!-- ix-docs-ignore -->
![imgix logo](https://assets.imgix.net/sdk-imgix-logo.svg)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fimgix%2Fdjango-imgix.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fimgix%2Fdjango-imgix?ref=badge_shield)

`django-imgix` is an app for integrating [imgix](https://www.imgix.com/) into Django sites.

[![Version](https://img.shields.io/pypi/v/django-imgix.svg)](https://pypi.org/project/django-imgix/)
[![Build Status](https://travis-ci.com/imgix/django-imgix.svg?branch=main)](https://travis-ci.com/imgix/django-imgix)
![Downloads](https://img.shields.io/pypi/dm/django-imgix)
![Python Versions](https://img.shields.io/pypi/pyversions/django-imgix)
[![License](https://img.shields.io/github/license/imgix/django-imgix)](https://github.com/imgix/django-imgix/blob/main/LICENSE)

---
<!-- /ix-docs-ignore -->

- [Installation](#installation)
- [Configuration](#configuration)
	- [`IMGIX_DOMAINS` (required)](#imgixdomains-required)
	- [`IMGIX_HTTPS`](#imgixhttps)
	- [`IMGIX_SIGN_KEY`](#imgixsignkey)
	- [`IMGIX_WEB_PROXY_SOURCE`](#imgixwebproxysource)
	- [`IMGIX_DETECT_FORMAT`](#imgixdetectformat)
	- [`IMGIX_ALIASES`](#imgixaliases)
- [Usage](#usage)
	- [Aliases](#aliases)

## Installation

Dependencies:
This app requires Django > 1.4 and imgix > 0.1

1. Run ```pip install django-imgix```
2. Add ```'django_imgix'``` to your ```INSTALLED_APPS```:

```python
INSTALLED_APPS = (
	...
	'django_imgix',
)
```

## Configuration

There are a few settings you can use to configure how django-imgix works:

### `IMGIX_DOMAINS` (*required*)

Give the domain name, or list of domain names, that you have registered with imgix:

```python
IMGIX_DOMAINS = 'my-domain.imgix.net'

or

IMGIX_DOMAINS = [
	'my-domain-1.imgix.net',
	'my-domain-2.imgix.net',
	'my-domain-3.imgix.net',
]
```

### `IMGIX_HTTPS`

Boolean value, defaults to `True` if not specified. If set to `False` it disables HTTPS support.

### `IMGIX_SIGN_KEY`

If you want to produce signed URLs you need to enable secure URLs in the 'Source' tab in your imgix.com account. This will generate a secret key that you need to specify here, e.g.

```python
IMGIX_SIGN_KEY = 'jUIrLPuMEm2aCRj'
```

This will make a hash from the image url and all parameters that you have supplied, which will be appended as a url parameter `s=hash` to the image, e.g.

`https://my-domain.imgix.net/media/images/dsc_0001.jpg?fm=jpg&h=720&w=1280s=976ae7332b279147ac0812c1770db07f`

### `IMGIX_WEB_PROXY_SOURCE`

Boolean value, defaults to `False` if not specified. If set to `True` image urls will be generated using the full original image URL, as needed for a Web Proxy Source.
Note that imgix requires all your URLs to be signed if you are using a Web Proxy Source (do that by specifying **IMGIX_SIGN_KEY**).

### `IMGIX_DETECT_FORMAT`

Boolean value, defaults to `False` if not specified. If set to `True` django-imgix will automatically detect popular image extensions and apply the `fm=` parameter to the image URL, where the value is equal to one of several [valid formats](https://www.imgix.com/docs/reference/format#param-fm).

Example:

```python
{% load imgix_tags %}
{% get_imgix '/media/images/dsc_0001.jpg' w=1280 h=720 %}
```

will produce:

`https://my-domain.imgix.net/media/images/dsc_0001.jpg?fm=jpg&h=720&w=1280`

Currently supported image formats for IMGIX_DETECT_FORMAT are jpg, jpeg, png, gif, jp2, jxr and webp.

### `IMGIX_ALIASES`

Read about aliases in the **Usage** section below.

## Usage

Django-imgix's functionality comes in the form of a template tag, `get_imgix`, that gets an image URL as its first argument and then an N number of optional arguments:

```python
{% load imgix_tags %}
<img src="{% get_imgix 'image_url' key=value ... %}"/>
```

Your `'image_url'` should be a relative URL, as it will be appended to a domain specified in `IMGIX_DOMAINS`, to form an absolute URL.

You can add as many `key=value` pairs as you want. Each `key=value` pair results in a url parameter
that imgix can recognise and use to generate your thumbnail.

For a full list of supported parameters, see [imgix's API docs](https://www.imgix.com/docs/reference/)

There is a special argument, `wh=WIDTHxHEIGHT`, which is made specifically so that transition from other image processing libraries such as **easy_thumbnails** is easier.
For example,

`{% get_imgix '/media/images/dsc_0001.jpg' wh='1280x720' %}`

is the same as saying

`{% get_imgix '/media/images/dsc_0001.jpg' w=1280 h=720 %}`

which resolves to

`http://my-domain.imgix.net/media/images/dsc_0001.jpg?h=720&w=1280`

`wh` will take precedence over `w` and `h` arguments, unless you use a 0 as one of the values in `wh`, e.g.

`{% get_imgix '/media/images/dsc_0001.jpg' wh='1280x0' w='777' h='555' %}`

will result in

`http://my-domain.imgix.net/media/images/dsc_0001.jpg?h=555&w=1280`

### Aliases

If you don't want to list all your `key=value` parameters inline all the time, you can group them into aliases.

To do that, first specify the aliases in your settings file:

```python
IMGIX_ALIASES = {
        'alias_one': {'w': 200, 'h': 300, 'lossless': 1, 'auto': 'format'},
        'alias_two': {'w': 450, 'h': 160, 'fm':'jpg', 'q': 70 },
    }
```

Then, in your template, either simply provide the alias name as the first unnamed argument, or use `alias='alias_name'`:

```python
{% load imgix_tags %}
<img src="{% get_imgix 'image_url' 'alias_one' %}"/>
... or ...
<img src="{% get_imgix 'image_url' alias='alias_one' %}"/>
```

Providing an alias means that any other arguments will be ignored.


## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fimgix%2Fdjango-imgix.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fimgix%2Fdjango-imgix?ref=badge_large)