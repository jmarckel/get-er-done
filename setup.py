"""A setuptools based setup module"""


from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'GetErDone',
    version = '0.0.1',
    description = 'REST based task application suite',
    long_description = long_description,
    url = 'https://github.com/jmarckel/get-er-done',
    author = 'Jeff Marckel',
    author_email = 'jbmarckel@gmail.com',

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    keywords = 'task',

    packages = find_packages(exclude = ['contrib', 'docs', 'tests']),

    include_package_data=True,

    install_requires = ['Flask', 'Flask-OAuthlib', 'flask-cors', 'jinja2', 'python-jose', 'six', 'cryptography'],

    entry_points = {
        'console_scripts': [
            'GetErDone-api=GetErDone.server.api:main',
            'GetErDone-spa=GetErDone.server.spa:main',
            'GetErDone-site=GetErDone.server.site:main',
            'GetErDone-webapp=GetErDone.server.webapp:main',
        ],
    },
)
