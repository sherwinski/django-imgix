Django imgix
============

[![Build Status](https://travis-ci.org/pancentric/django-imgix.png?branch=master)](https://travis-ci.org/pancentric/django-imgix)

A simple Django application for creating [Imgix](https://www.imgix.com/ "Imgix") formatted image links in your templates


Installation
------------

Dependencies:
This app requires Django > 1.4 and imgix>0.1


1. Run ```  pip install django-imgix  ```
2. Add ``` 'django_imgix' ``` to your ``` INSTALLED_APPS ```:




```
	INSTALLED_APPS = (
		...
		'django_imgix',
	)
```


----------


Configuration
-------------
There are a few settings you can use to configure how django-imgix works:

**IMGIX_DOMAINS** (*required*)

Give the domain name, or list of domain names, that you have registered with Imgix:

```
IMGIX_DOMAINS = 'my-domain.imgix.net'
...
or
...
IMGIX_DOMAINS = [
	'my-domain-1.imgix.net',
	'my-domain-2.imgix.net',
	'my-domain-3.imgix.net',
	]
```

**IMGIX_HTTPS**

Boolean value, defaults to `True` if not specified. If set to `False` it disables HTTPS support.


**IMGIX_SIGN_KEY**

If you want to produce signed URLs you need to enable secure URLs in the 'Source' tab in your Imgix.com account. This will generate a secret key that you need to specify here, e.g.

```
IMGIX_SIGN_KEY = 'jUIrLPuMEm2aCRj'
```

This will make a hash from the image url and all parameters that you have supplied, which will be appended as a url parameter `s=hash` to the image, e.g.

`https://my-domain.imgix.net/media/images/dsc_0001.jpg?fm=jpg&h=720&w=1280s=976ae7332b279147ac0812c1770db07f`


**IMGIX_WEB_PROXY_SOURCE**

Boolean value, defaults to `False` if not specified. If set to `True` image urls will be generated using the full original image url, as needed for a Web Proxy Source.
Note that Imgix requires all your urls to be signed if you are using a Web Proxy Source (do that by specifying **IMGIX_SIGN_KEY**).


**IMGIX_DETECT_FORMAT**

Boolean value, defaults to `False` if not specified. If set to `True` django-imgix will automatically detect popular image extensions and apply the `fm=image_extension` attribute to the image url, where `image_extension`  is one of the formats listed [here](https://www.imgix.com/docs/reference/format#param-fm "Imgix fm parameter")


Example:
```
{% load imgix_tags %}
{% get_imgix '/media/images/dsc_0001.jpg' w=1280 h=720 %}
```
will produce

`https://my-domain.imgix.net/media/images/dsc_0001.jpg?fm=jpg&h=720&w=1280`


Currently supported image formats for IMGIX_DETECT_FORMAT are jpg, jpeg, png, gif, jp2, jxr and webp.

**IMGIX_SOURCES**

If you're using multiple sources, you can omit all previous settings and declare them all here in a dictionary. The dictionary key is a name for the source you can reference in calls to `get_imgix` and `get_imgix_url`. The default source is under the empty string key `''`, similar to the root logger in logging configurations. If you specify the `''` key in this setting in addition to the top-level settings above, the values in `''` will be used. 

The keys in each source map to the previous settings in the following manner:

- `IMGIX_DOMAINS` -> `domains`
- `IMGIX_WEB_PROXY_SOURCE` -> `web_proxy`
- `IMGIX_HTTPS` -> `use_https`,
- `IMGIX_SIGN_KEY` -> `sign_key`
- `IMGIX_DETECT_FORMAT` -> `detect_format`

If you don't declare some of these keys for a source, their default value will be used.

```python
IMGIX_SOURCES = {
    '': {
        'domains': ['test1.imgix.net'],
        'detect_format': True,
    },
    'proxy': {
        'domains': ['test-proxy.imgix.net'],
        'sign_key': 'my-sign-key',
    }
}
```

Then you can specify the source like this:

```python
# uses main source
get_imgix_url('/image1.jpg')

# uses proxy source
get_imgix_url('http://example.com/test-image.jpg', source='proxy')
```

**IMGIX_ALIASES**

Read about aliases in the **Usage** section below.

----------


Usage
-----

**Plain function `get_imgix_url`**

You can conveniently generate Imgix URLs based on the project settings you've declared with `get_imgix_url`. It takes an image URL as the first argument, and an arbitrary number of optional keyword arguments.

```python
from django_imgix import get_imgix_url

imgix_url = get_imgix_url('image_url', key1='value1', key2='value2')
```

If you are using a Web Proxy source, pass an absolute URL for `'image_url'`. Otherwise `'image_url'` should be a relative URL, as it will be appended to a domain specified in `IMGIX_DOMAINS`, to form an absolute URL.

You can add as many `key=value` pairs as you want. There are three specially treated keys: `source`, `alias`, `wh`.

- If `source` is supplied, it should correspond to a key in `IMGIX_SOURCES`. The configuration for that source will be used to general the URL.
- If `alias` is supplied, it should be a string corresponding to a key in the `IMGIX_ALIASES` setting. The dictionary under that key will be used as the base for the keyword arguments passed to `get_imgix_url` to override.
- If `wh` is supplied, it should be a string in the form `{width}x{height}`, which is made specifically so that transition from other image processing libraries such as **easy_thumbnails** is easier.

    For example,

    ```python
    get_imgix_url('/media/images/dsc_0001.jpg', wh='1280x720')
    ```

    is the same as saying

    ```python
    get_imgix_url('/media/images/dsc_0001.jpg', w=1280, h=720)
    ```

    which resolves to

    `http://my-domain.imgix.net/media/images/dsc_0001.jpg?h=720&w=1280`

    `wh` will take precedence over `w` and `h` arguments, unless you use a 0 as one of the values in `wh`, e.g.

    ```python
    get_imgix_url('/media/images/dsc_0001.jpg', wh='1280x0' w=777, h=555)
    ```

    will result in

    `http://my-domain.imgix.net/media/images/dsc_0001.jpg?h=555&w=1280`

All other `key=value` pairs will result in a URL parameter that Imgix can recognise and use to generate your image.

For a full list of supported parameters, see [here](https://www.imgix.com/docs/reference/ "Imgix API reference")

**Template tag `get_imgix`**

To use the template tag, load the tags first: `{% load imgix_tags %}`

The template tag accepts the same parameters as `get_imgix_url`, e.g.:

```python
get_imgix_url('/media/image1.jpg', w=600, h=400)
```

Is equivalent to the template tag call:

```
{% load imgix_tags %}
{% get_imgix '/media/image1.jpg' w=600 h=400 %}
```

#### **Aliases**

If you don't want to list all your `key=value` parameters inline all the time, you can group them into aliases.

To do that, first specify the aliases in your settings file:

```python
IMGIX_ALIASES = {
        'alias_one': {'w': 200, 'h': 300, 'lossless': 1, 'auto': 'format'},
        'alias_two': {'w': 450, 'h': 160, 'fm':'jpg', 'q': 70 },
    }

```

Then, in your template or function, either simply provide the alias name as the first unnamed argument, or use `alias='alias_name'`:

```
{% load imgix_tags %}
<img src="{% get_imgix 'image_url' 'alias_one' %}"/>
... or ...
<img src="{% get_imgix 'image_url' alias='alias_one' %}"/>
```

If you provide arguments in addition to `alias`, they will override that alias.
