from __future__ import print_function
import argparse
import sys
import json
import yaml
import os.path

from .collection import DottedDict

_JSON = 'JSON'
_YAML = 'YAML'

_FORMATS = {
    '.json': _JSON,
    '.yaml': _YAML,
    '.yml': _YAML,
}

if sys.version_info[0] >= 3:
    # Python 3
    unicode = str


def edit_file(key, value, file, fmt, must_exist=False):
    data = DottedDict(read_file(file, fmt))
    if must_exist:
        try:
            # this is the way I found it works for array vals too
            # e.g. fruits.0.name
            data[key]
        except KeyError:
            raise ValueError('{} is not present in {}'.format(key, file))
    data[key] = value
    write_file(file, fmt, data)


def read_file(file, fmt):
    load = {
        _JSON: json.load,
        _YAML: yaml.safe_load,
    }[fmt]
    try:
        with open(file) as fd:
            data = load(fd)
    except IOError:
        data = {}

    return data


def write_file(file, fmt, data):
    to = {
        _JSON: data.to_json,
        _YAML: data.to_yaml,
    }[fmt]
    tmp = file + ".tmp"
    with os.fdopen(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL), "w") as fd:
        try:
            fd.write(to())
            fd.close()
            os.rename(tmp, file)
        except Exception:
            # We can assume we can remove it, because we successfully created
            # it with O_EXCL above.
            os.unlink(tmp)
            raise


def normalize_val(val):
    """Normalize JSON value to a proper type.
    https://google.github.io/styleguide/jsoncstyleguide.xml#Double_Quotes"""
    if val == "null":
        return None

    if val == "true":
        return True

    if val == "false":
        return False

    try:
        return int(val)
    except ValueError:
        pass

    try:
        return float(val)
    except ValueError:
        pass

    return val


def main():
    """The entrypoint to CLI app."""
    epilog = None
    parser = argparse.ArgumentParser(description='Simple data editor.',
                                     epilog=epilog,
                                     prog='sde')
    parser.add_argument('key', metavar='<key>', help='Key to edit')
    parser.add_argument('val', metavar='<val>', help='New value')
    parser.add_argument('file', metavar='<filename>', help='Filename to edit')
    parser.add_argument('-e', '--must-exist', dest='must_exist', action='store_true',
                        help='Throw error and exit if the key does not already exist')
    parser.add_argument('-s', '--string', dest='is_string', action='store_true',
                        help='Always treat value as a string by quoting it')
    parser.set_defaults(is_string=False, must_exist=False)
    args = parser.parse_args()

    if args.is_string:
        val = args.val
    else:
        val = normalize_val(args.val)

    extension = os.path.splitext(args.file)[-1].lower()

    fmt = _FORMATS.get(extension, None)
    if fmt is None:
        print("\033[91mError: \033[0mUnknown extension: " + extension, file=sys.stderr)
        sys.exit(1)

    try:
        edit_file(args.key, val, args.file, fmt, must_exist=args.must_exist)
    except ValueError as e:
        print("\033[91mError: \033[0m" + str(e), file=sys.stderr)
        sys.exit(1)
