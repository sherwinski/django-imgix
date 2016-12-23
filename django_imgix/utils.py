def pick(keys, _dict):
    """
    Returns a new dictionary based on `_dict`,
    restricting keys to those in the iterable `keys`.
    """

    key_set = set(keys) & set(_dict.keys())

    return dict((key, _dict[key]) for key in key_set)


def merge_dicts(*dicts):
    merged = {}
    for _dict in dicts:
        merged.update(_dict)
    return merged
