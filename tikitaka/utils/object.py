import re
from collections import namedtuple


# --------------------------------------------------------------------------------------------------
class ObjectUtil:
    slicePattern = re.compile(r'(?P<start>\-?\d+)?:(?P<stop>\-?\d+)?(:(?P<step>\d+))?')

    @classmethod
    def get_from_path(cls, obj, path):
        paths = path.split('.')
        key = paths.pop(0)
        value = None
        found = False
        if isinstance(obj, list):
            def safe_cast(value, to_type):
                try:
                    return to_type(value)
                except Exception:
                    return None

            def maybe_index(key):
                if key == '#':
                    return key
                matched = re.match(cls.slicePattern, key)
                if matched:
                    return slice(safe_cast(matched.group('start'), int), safe_cast(matched.group('stop'), int),
                                 safe_cast(matched.group('step'), int))
                return safe_cast(key, int)

            maybe = maybe_index(key)
            if maybe is None:
                return None, False  # return
            if isinstance(maybe, int):
                try:
                    value = obj[maybe]
                    found = True
                except Exception:
                    return None, False  # return
            elif maybe == '#':
                try:
                    if paths:
                        for element in obj:
                            value, found = cls.get_from_path(element, '.'.join(paths))
                            if found is True:
                                return value, found  # return by itself
                        return None, False  # return
                    else:
                        value = obj[0]
                        found = True
                except Exception:
                    return None, False  # return
            elif isinstance(maybe, slice):
                try:
                    elements = obj[maybe]
                    if paths:
                        value = []
                        found = False
                        for element in elements:
                            v, f = cls.get_from_path(element, '.'.join(paths))
                            if f:
                                found = True
                            value.append(v)
                        return value, found  # return by itself
                    else:
                        value = elements
                        found = True
                except Exception:
                    return None, False
        elif isinstance(obj, dict):
            if key not in obj:
                return None, False  # return
            value = obj.get(key)
            found = True
        elif isinstance(obj, object):
            if not hasattr(obj, key):
                return None, False  # return
            value = getattr(obj, key)
            found = True

        if paths and value is not None:
            return cls.get_from_path(value, '.'.join(paths))

        return value, found

    @classmethod
    def object_to_dictionary(cls, obj):
        dictionary = {}
        for attr in obj.__dict__:
            value = getattr(obj, attr)
            if value is not None:
                dictionary[attr] = value
        return dictionary

    @classmethod
    def dictionary_to_namedtuple(cls, dictionary, typename=None, fields=None):
        if dictionary is None or not isinstance(dictionary, dict):
            return None
        copied = dictionary.copy()
        if fields is None:
            fields = sorted(copied.keys())
        for field in fields:
            if field not in copied:
                copied[field] = None
        FromDictionary = namedtuple(typename or 'FromDictionary', fields)
        return FromDictionary(**copied)