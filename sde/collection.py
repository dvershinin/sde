# -*- coding: utf-8 -*-

import json
import re
from abc import ABCMeta, abstractmethod

import six
import yaml
from six import add_metaclass, string_types, iteritems


# this was only introduced in six 1.13.0, but it's too old in RHEL,
# and we don't want to rebuild its package
# from six.moves import collections_abc
if six.PY2:
    import collections as collections_abc
else:
    import collections.abc as collections_abc

SPLIT_REGEX = re.compile(r"(?<!\\)(\.)")


def is_dotted_key(key):
    """Returns True if the key has any not-escaped dot inside"""
    return len(re.findall(SPLIT_REGEX, key)) > 0


def split_key(key, max_keys=0):
    r"""
    Splits a key but allows dots in the key name if they're escaped properly.

    Splitting this complex key:

    `complex_key = r'.dont\\.splitme.d\\.o\\. origen.splitme\\.dontsplit.splitme.'
    split_key(complex_key)`

    results in:

    `['', r'dont\\.splitme', r'd\\.o\\. origen', r'splitme\\.dontsplit', 'splitme', '']`


    Args:
        key (str): The key to be split.
        max_keys (int): The maximum number of keys to be extracted. 0 means no
            limits.

    Returns:
        A list of keys
    """
    parts = [x for x in re.split(SPLIT_REGEX, key) if x != "."]
    result = []
    while len(parts) > 0:
        if 0 < max_keys == len(result):
            break
        result.append(parts.pop(0))

    if len(parts) > 0:
        result.append(".".join(parts))
    return result


@add_metaclass(ABCMeta)
class DottedCollection(object):
    """Abstract Base Class for DottedDict and DottedDict"""

    @classmethod
    def factory(cls, initial=None):
        """Returns a DottedDict or a DottedList based on the type of the
        initial value, that must be a dict or a list. In other case the same
        original value will be returned.
        """
        if isinstance(initial, list):
            return DottedList(initial)
        if isinstance(initial, dict):
            return DottedDict(initial)
        return initial

    @classmethod
    def load_json(cls, json_value):
        """Returns a DottedCollection from a JSON string"""
        return cls.factory(json.loads(json_value))

    @classmethod
    def _factory_by_index(cls, dotted_key):
        """Returns the proper DottedCollection that best suits the next key in
        the dotted_key string. First guesses the next key and then analyzes it.
        If the next key is numeric then returns a DottedList. In other case a
        DottedDict is returned.
        """
        if not isinstance(dotted_key, string_types):
            next_key = str(dotted_key)
        elif not is_dotted_key(dotted_key):
            next_key = dotted_key
        else:
            next_key, tmp = split_key(dotted_key, 1)

        return DottedCollection.factory([] if next_key.isdigit() else {})

    def __init__(self, initial):
        """Base constructor. If there are nested dicts or lists they are
        transformed into DottedCollection instances.
        """
        if not isinstance(initial, list) and not isinstance(initial, dict):
            raise ValueError('initial value must be a list or a dict')

        self._validate_initial(initial)

        self.store = initial

        if isinstance(self.store, list):
            data = enumerate(self.store)
        else:
            data = iteritems(self.store)

        for key, value in data:
            try:
                self.store[key] = DottedCollection.factory(value)
            except ValueError:
                pass

    def _validate_initial(self, initial):
        """Validates data so no unescaped dotted key is present."""
        if isinstance(initial, list):
            for item in initial:
                self._validate_initial(item)
        elif isinstance(initial, dict):
            for key, item in iteritems(initial):
                if is_dotted_key(key):
                    raise ValueError("{0} is not a valid key inside a "
                                     "DottedCollection!".format(key))
                self._validate_initial(item)

    def __len__(self):
        return len(self.store)

    def __iter__(self):
        return iter(self.store)

    def __repr__(self):
        return repr(self.store)

    def to_json(self):
        """Returns a JSON representation of the DottedCollection"""
        return json.dumps(self, cls=DottedJSONEncoder, indent=4)

    def to_yaml(self):
        """Returns a YAML representation of the DottedCollection"""
        return yaml.dump(self, Dumper=DottedYAMLDumper)

    @abstractmethod
    def __getitem__(self, name):
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, name, value):
        raise NotImplementedError

    @abstractmethod
    def __delitem__(self, name):
        raise NotImplementedError

    @abstractmethod
    def to_python(self):
        raise NotImplementedError


class DottedList(DottedCollection, collections_abc.MutableSequence):
    """A list with support for the dotted path syntax"""

    def __init__(self, initial=None):
        DottedCollection.__init__(
            self,
            [] if initial is None else list(initial)
        )

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.store[index]

        if isinstance(index, int) \
                or (isinstance(index, string_types) and index.isdigit()):
            return self.store[int(index)]

        if isinstance(index, string_types) and is_dotted_key(index):
            my_index, alt_index = split_key(index, 1)
            target = self.store[int(my_index)]

            # required by the dotted path
            if not isinstance(target, DottedCollection):
                raise IndexError('cannot get "{0}" in "{1}" ({2})'.format(
                    alt_index,
                    my_index,
                    repr(target)
                ))

            return target[alt_index]

        raise IndexError('cannot get %s in %s' % (index, repr(self.store)))

    def __setitem__(self, index, value):
        if isinstance(index, int) \
                or (isinstance(index, string_types) and index.isdigit()):
            # If the index does not exist in the list, but it's the same index
            # we would obtain by appending the value to the list we actually
            # append the value. (***)
            if int(index) not in self.store and int(index) == len(self.store):
                self.store.append(DottedCollection.factory(value))
            else:
                self.store[int(index)] = DottedCollection.factory(value)

        elif isinstance(index, string_types) and is_dotted_key(index):
            my_index, alt_index = split_key(index, 1)

            # (***)
            if int(my_index) not in self.store \
                    and int(my_index) == len(self.store):
                self.store.append(
                    DottedCollection._factory_by_index(alt_index))

            if not isinstance(self[int(my_index)], DottedCollection):
                raise IndexError('cannot set "%s" in "%s" (%s)' % (
                    alt_index, my_index, repr(self[int(my_index)])))

            self[int(my_index)][alt_index] = DottedCollection.factory(value)

        else:
            raise IndexError('cannot use %s as index in %s' % (
                index, repr(self.store)))

    def __delitem__(self, index):
        if isinstance(index, int) \
                or (isinstance(index, string_types) and index.isdigit()):
            del self.store[int(index)]

        elif isinstance(index, string_types) and is_dotted_key(index):
            my_index, alt_index = split_key(index, 1)
            target = self.store[int(my_index)]

            # required by the dotted path
            if not isinstance(target, DottedCollection):
                raise IndexError('cannot delete "%s" in "%s" (%s)' % (
                    alt_index, my_index, repr(target)))

            del target[alt_index]

        else:
            raise IndexError('cannot delete %s in %s' % (
                index, repr(self.store)))

    def to_python(self):
        """Returns a plain python list and converts to plain python objects all
        this object's descendants.
        """
        result = list(self)

        for index, value in enumerate(result):
            if isinstance(value, DottedCollection):
                result[index] = value.to_python()

        return result

    def insert(self, index, value):
        self.store.insert(index, value)


class DottedDict(DottedCollection, collections_abc.MutableMapping):
    """A dict with support for the dotted path syntax"""

    def __init__(self, initial=None):
        DottedCollection.__init__(
            self,
            {} if initial is None else dict(initial)
        )

    def __getitem__(self, k):
        key = self.__keytransform__(k)

        if not isinstance(k, string_types) or not is_dotted_key(key):
            return self.store[key]

        my_key, alt_key = split_key(key, 1)
        target = self.store[my_key]

        # required by the dotted path
        if not isinstance(target, DottedCollection):
            raise KeyError('cannot get "{0}" in "{1}" ({2})'.format(
                alt_key,
                my_key,
                repr(target)
            ))

        return target[alt_key]

    def __setitem__(self, k, value):
        key = self.__keytransform__(k)

        if not isinstance(k, string_types):
            raise KeyError('DottedDict keys must be str or unicode')
        if not is_dotted_key(key):
            self.store[key] = DottedCollection.factory(value)
        else:
            my_key, alt_key = split_key(key, 1)

            if my_key not in self.store:
                self.store[my_key] = DottedCollection._factory_by_index(alt_key)

            self.store[my_key][alt_key] = value

    def __delitem__(self, k):
        key = self.__keytransform__(k)

        if not isinstance(k, string_types) or not is_dotted_key(key):
            del self.store[key]

        else:
            my_key, alt_key = split_key(key, 1)
            target = self.store[my_key]

            if not isinstance(target, DottedCollection):
                raise KeyError('cannot delete "{0}" in "{1}" ({2})'.format(
                    alt_key,
                    my_key,
                    repr(target)
                ))

            del target[alt_key]

    def to_python(self):
        """Returns a plain python dict and converts to plain python objects all
        this object's descendants.
        """
        result = dict(self)

        for key, value in iteritems(result):
            if isinstance(value, DottedCollection):
                result[key] = value.to_python()

        return result

    __getattr__ = __getitem__

    # self.store does not exist before __init__() initializes it

    def __setattr__(self, key, value):
        if key in self.__dict__ or key == 'store':
            object.__setattr__(self, key, value)
        else:
            self.__setitem__(key, value)

    def __delattr__(self, key):
        if key in self.__dict__ or key == 'store':
            object.__delattr__(self, key)
        else:
            self.__delitem__(key)

    def __contains__(self, k):
        key = self.__keytransform__(k)

        if not isinstance(k, string_types) or not is_dotted_key(key):
            return self.store.__contains__(key)

        my_key, alt_key = split_key(key, 1)
        target = self.store[my_key]

        if not isinstance(target, DottedCollection):
            return False

        return alt_key in target

    @staticmethod
    def __keytransform__(key):
        return key


#
# JSON stuff
#


class DottedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        """This is called by the encoder for each object."""
        if isinstance(obj, DottedCollection):
            return obj.store
        return json.JSONEncoder.default(self, obj)


#
# YAML stuff
#


class DottedYAMLDumper(yaml.Dumper):
    """
    We could do,

        dumper.add_representer(DottedDict, lambda dumper, data: data.store)

    But we'd have to do it for each type.

    This suggests making a custom dumper for a hierarchy of types:
        https://github.com/yaml/pyyaml/issues/51
    """

    def represent_data(self, data):
        """This is called by the representer for each object."""
        if isinstance(data, DottedCollection):
            return self.represent_data(data.store)
        return super(DottedYAMLDumper, self).represent_data(data)
