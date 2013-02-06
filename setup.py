from setuptools import setup

if __name__ != "__main__":
    import sys
    sys.exit(1)

def long_desc():
    with open('README.rst', 'rb') as f:
        return f.read()

execfile('chru/version.py')

kw = {
    "name": "chr",
    "version": __version__,
    "description": "Python based URL shortening service",
    "long_description": long_desc(),
    "url": "https://github.com/plausibility/chr",
    "author": "plausibility",
    "author_email": "chris@gibsonsec.org",
    "license": "MIT",
    "packages": [
        'chru',
        'chru.api',
        'chru.web',
        'chru.utility',
    ],
    "include_package_data": True,
    "install_requires": [
        "requests",
        "flask",
        "flask-kvsession",
        "recaptcha-client",
        "mattdaemon>=1.1.0",
        "pysqlw>=1.3.0"
    ],
    "zip_safe": False,
    "keywords": "url short shortener slug",
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2"
    ],
    "entry_points": {
        "console_scripts": [
            'chru = chru.chra:main'
        ]
    }
}

if __name__ == "__main__":
    setup(**kw)
