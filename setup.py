import os
from importlib.machinery import SourceFileLoader

from setuptools import find_packages, setup

module = SourceFileLoader(
    "version", os.path.join("rpcgrid", "version.py")
).load_module()


setup(
    name='rpcgrid',
    version=module.__version__,
    author=module.__author__,
    author_email=module.team_email,
    license=module.package_license,
    description=module.package_info,
    long_description='''
# RPCGrid (development)

Remote procedure call package for any protocol and any transport layer.

Easy implementation Remote procedure call (RPC) package for some protocol and some transport layer.



## Features
+ async/await support
+ logging remote procedure call
+ server/client side remote procedure call
+ custom transport and protocols
+ block/non-block call
+ parallel rpc calls in async mode

#### Protocol
+ JsonRPC protocol support


#### Transport
+ Single/Multithreading remote procedure call
+ UDP/TCP socket remote procedure call 
+ RabbitMQ remote procedure call''',
    keywords='rpc microservice server rpcgrid '
    'async asyncio aio jsonrpc'
    'rabbit rabbitmq service'
    'remote procedure call',
    platforms="all",
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Internet',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Microsoft',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    project_urls={
        'Documentation': 'https://github.com/urands/rpcgrid/',
        'Source': 'https://github.com/urands/rpcgrid/',
        'Tracker': 'https://github.com/urands/rpcgrid/issues/',
    },
    packages=find_packages(exclude=['tests']),
    package_data={'rpcgrid': ['py.typed']},
    python_requires=">3.5.*, <4",
    extras_require={
        'develop': [
            'pytest',
            'sphinx',
            'flake8',
            'isort',
            'black',
            'sphinx-autobuild',
        ]
    },
)
