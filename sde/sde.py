from __future__ import print_function
import argparse
import sys
from .collection import DottedDict

if sys.version_info.major >= 3:
    # Python 3
    unicode = str


def isnumeric(s):
    return unicode(s).isnumeric()


def edit_json(key, value, file, must_exist=False):
    import json
    try:
        with open(file) as json_file:
            data = json.load(json_file)
    except IOError:
        data = {}
    data = DottedDict(data)
    if must_exist:
        try:
            # this is the way I found it works for array vals too
            # e.g. fruits.0.name
            data[key]
        except KeyError:
            raise ValueError('{} is not present in {}'.format(key, file))
    data[key] = value
    with open(file, 'w') as json_file:
        json_file.write(data.to_json())


def normalize_val(val):
    """Normalize JSON value to a proper type.
    https://google.github.io/styleguide/jsoncstyleguide.xml#Double_Quotes"""
    if val == "null":
        return None
    elif val == "true":
        return True
    elif val == "false":
        return False
    elif isnumeric(val):
        return int(val)
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

    if not args.is_string:
        val = normalize_val(args.val)

    if args.file.endswith('.json'):
        try:
            edit_json(args.key, val, args.file, must_exist=args.must_exist)
        except ValueError as e:
            print("\033[91mError: \033[0m" + str(e), file=sys.stderr)
            sys.exit(1)
