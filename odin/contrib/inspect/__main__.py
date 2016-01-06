import argparse

import sys

from .resource import ResourceSummary


def import_item(item):
    module, obj = item.rsplit('.', 1)
    module = __import__(module, globals(), locals(), [obj])
    return getattr(module, obj)


def get_options():
    parser = argparse.ArgumentParser(prog="odin.contrib.inspect")
    main_subparsers = parser.add_subparsers(dest='command')

    # Resource ##################################

    subparser = main_subparsers.add_parser('resource', help='Inspect a Odin resource')
    subparser.add_argument('RESOURCE', help='Name of the resource (to be imported)')

    return parser.parse_args()


def main():
    options = get_options()

    if options.command == 'resource':
        resource = import_item(options.RESOURCE)
        summary = ResourceSummary(resource)
        summary.fields(sys.stdout)
    else:
        print("No command supplied.", file=sys.stdout)
        exit(1)


if __name__ == '__main__':
    main()
