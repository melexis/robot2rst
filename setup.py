# -*- coding: utf-8 -*-

from setuptools import find_namespace_packages, setup

project_url = 'https://github.com/melexis/robot2rst'

requires = ['robotframework>=3.2', 'mako']

setup(
    name='mlx.robot2rst',
    url=project_url,
    author='Jasper Craeghs',
    author_email='jce@melexis.com',
    license='Apache License Version 2.0',
    description='Python script for converting a Robot Framework file to a reStructuredText (.rst) file',
    long_description=open("README.rst").read(),
    long_description_content_type='text/x-rst',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_namespace_packages(where=".", exclude=("doc.*", "doc", "build*")),
    package_dir={"": "."},
    include_package_data=True,
    package_data={
        'mlx.robot2rst': ['*.mako'],
    },
    install_requires=requires,
    python_requires='>=3.8',
    keywords=['robot', 'robotframework', 'sphinx', 'traceability'],
    entry_points={
        'console_scripts': [
            'mlx.robot2rst = mlx.robot2rst.robot2rst:entrypoint',
            'robot2rst = mlx.robot2rst.robot2rst:entrypoint',
        ]
    },
)
