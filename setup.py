from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='odin',

    version='0.10',

    description='Data-structure definition/validation/traversal, mapping and serialisation toolkit for Python',
    long_description=long_description,

    url='https://github.com/python-odin/odin',

    author='Tim Savage',
    author_email='tim@savage.company',

    license='BSD',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: BSD License',

        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    keywords='data-structure validation data-mapping',

    packages=find_packages(include=('odin*',)),

    install_requires=['six'],

    extras_require={
        # Additional codecs
        'yaml': ['pyyaml'],
        'msgpack': ['msgpack-python'],

        # Documentation generation
        'doc_gen': ["jinja2>=2.7"],

        # Pint integration
        'pint': ["pint"],

        # Filter Query
        'filter_query': ["ply"],

        # Inspect
        'inspect': ['humanfriendly'],
    },

    obsoletes=['jsrn'],
)
