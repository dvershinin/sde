import argparse
from .collection import DottedDict


def edit_json(key, value, file):
    import json
    try:
        with open(file) as json_file:
            data = json.load(json_file)
    except IOError:
        data = {}
    data = DottedDict(data)
    data[key] = value
    with open(file, 'w') as json_file:
        json_file.write(data.to_json())


def main():
    """The entrypoint to CLI app."""
    epilog = None
    parser = argparse.ArgumentParser(description='Simple data editor.',
                                     epilog=epilog,
                                     prog='sde')
    parser.add_argument('key', metavar='<key>', help='Key to edit')
    parser.add_argument('val', metavar='<val>', help='New value')
    parser.add_argument('file', metavar='<filename>', help='Filename to edit')
    args = parser.parse_args()
    
    if args.file.endswith('.json'):
        edit_json(args.key, args.val, args.file)