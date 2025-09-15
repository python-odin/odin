"""Helper for generating a JSON schema in your project."""

import argparse
import importlib
import sys

from odin.contrib import json_schema


def resource_type(value: str) -> tuple[str, str]:
    package, _, resource_name = value.partition(":")
    if not (package and resource_name):
        raise ValueError("Invalid resource type")
    return package, resource_name


def get_opts() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="odin-json_schema",
    )
    parser.add_argument(
        "RESOURCE_TYPE",
        type=resource_type,
        help="The base resource to generate a JSON schema, in the form package.subpackage:ResourceType",
    )
    return parser.parse_args()


def main():
    opts = get_opts()

    package, resource_name = opts.RESOURCE_TYPE
    try:
        mod = importlib.import_module(package)
        resource_type = getattr(mod, resource_name)
    except ImportError:
        print(f"Unable to import {package!r}", file=sys.stderr)
        sys.exit(2)
    except AttributeError:
        print(
            f"Unable to get {resource_name!r} from package {package!r}", file=sys.stderr
        )
        sys.exit(3)

    json_schema.dump(resource_type, sys.stdout)


if __name__ == "__main__":
    main()
