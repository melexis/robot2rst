# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

project_url = 'https://github.com/melexis/robot2rst'

requires = ['robotframework', 'sphinxcontrib-robotdoc', 'mlx.traceability']

setup(
    name='mlx.robot2rst',
    version='1.0.0',
    url=project_url,
    author='Stein Heselmans',
    description='A script for converting a RobotFramework file, to an RST file',
    long_description=open("README.rst").read(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(exclude=['tests', 'doc']),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['mlx'],
    keywords=['robot', 'robotframework', 'sphinx', 'traceability'],
)
