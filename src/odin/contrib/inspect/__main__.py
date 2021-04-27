from __future__ import absolute_import, print_function
import argparse
import sys

from .resource import ResourceSummary
from .mapping import MappingSummary


def import_item(item):
    module, obj = item.rsplit('.', 1)
    module = __import__(module, globals(), locals(), [obj])
    return getattr(module, obj)


def get_options():
    parser = argparse.ArgumentParser(prog="odin.contrib.inspect")
    main_subparsers = parser.add_subparsers(dest='command')

    # Resource ##################################

    subparser = main_subparsers.add_parser('resource', help='Inspect a Odin resource')
    subparser.add_argument('RESOURCE', help='Path to resource')

    # Mapping ###################################

    subparser = main_subparsers.add_parser('mapping', help='Inspect a Odin mapping')
    subparser.add_argument('MAPPING', help='Path to mapping')

    return parser.parse_args()


def main():
    options = get_options()

    if options.command == 'resource':
        resource = import_item(options.RESOURCE)
        summary = ResourceSummary(resource, sys.stdout)
        summary.render()
    elif options.command == 'mapping':
        mapping = import_item(options.MAPPING)
        summary = MappingSummary(mapping, sys.stdout)
        summary.render()
    else:
        print("No command supplied.", file=sys.stdout)
        exit(1)


if __name__ == '__main__':
    main()
