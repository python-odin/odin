from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name='odin',
    version='0.7',
    url='https://github.com/timsavage/odin',
    license='LICENSE',
    author='Tim Savage',
    author_email='tim@savage.company',
    description='Data-structure definition/validation/traversal, mapping and serialisation toolkit for Python',
    long_description=long_description,
    packages=find_packages(),
    install_requires=['six'],
    extras_require={
        # Documentation generation
        'doc_gen': ["jinja2>=2.7"],
        # Pint integration
        'pint': ["pint"],
        # Filter Query
        'filter_query': ["ply"],
        # Inspect
        'inspect': ['humanfriendly'],
    },

    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
