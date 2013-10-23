from setuptools import setup

if __name__ != "__main__":
    import sys
    sys.exit(1)

def long_desc():
    with open('README.rst', 'rb') as f:
        return f.read()

kw = {
    "name": "chr",
    "version": "3.0.10",
    "description": "Minimalistic Python based URL shortening service",
    "long_description": long_desc(),
    "url": "https://github.com/plausibility/chr",
    "author": "plausibility",
    "author_email": "chris@gibsonsec.org",
    "license": "MIT",
    "packages": [
        'chrso'
    ],
    "include_package_data": True,
    "install_requires": [
        "flask",
        "wtforms",
        "flask-wtf",
        "redis",
        "hiredis",
    ],
    "zip_safe": False,
    "keywords": "url shrink short shortener",
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2"
    ]
}

if __name__ == "__main__":
    setup(**kw)
