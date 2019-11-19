# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

project_url = 'https://github.com/melexis/robot2rst'

requires = ['robotframework', 'sphinxcontrib-robotdoc', 'mlx.traceability', 'mako']

setup(
    name='mlx.robot2rst',
    use_scm_version={'write_to': 'mlx/__robot2rst_version__.py'},
    url=project_url,
    author='Jasper Craeghs',
    author_email='jce@melexis.com',
    license='Apache License Version 2.0',
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(exclude=['tests', 'doc']),
    include_package_data=True,
    install_requires=requires,
    setup_requires=['setuptools_scm'],
    namespace_packages=['mlx'],
    keywords=['robot', 'robotframework', 'sphinx', 'traceability'],
)
