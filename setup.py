from setuptools import setup

setup(
    name='odin',
    version="0.3.0",
    url='https://github.com/timsavage/odin',
    license='LICENSE',
    author='Tim Savage',
    author_email='tim.savage@poweredbypenguins.org',
    description='Object Data Mapping for Python',
    long_description=open("README.rst").read(),
    package_dir={'': 'src'},
    packages=['odin', 'odin.fields'],
    install_requires=['six'],
    extras_require={
        # Extra performance
        'performance': ['simplejson'],
        # Documentation support using Jinja2
        'doc': ["jinja2>=2.7"],
    },

    classifiers=[
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
)
