"""Planta Freedom Physics — Theory of Everything"""
from setuptools import setup, find_packages

setup(
    name='planta-freedom-physics',
    version='1.0.0',
    author='Gonçalo Melo de Magalhães',
    author_email='hi@planta.design',
    description='Planta Freedom Physics — Theory of Everything (F=P/D)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/iamgoncalo/planta-freedom-physics',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[
        'numpy>=1.24.0',
        'scipy>=1.10.0',
        'networkx>=3.0',
        'pyyaml>=6.0',
        'pydantic>=2.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS IS Independent',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    keywords='physics theory-of-everything AFI freedom perception distortion',
)
