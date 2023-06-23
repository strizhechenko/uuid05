from pathlib import Path
from setuptools import setup

setup(
    name='uuid05',
    version='0.0.2',
    packages=['uuid05'],
    url='https://github.com/strizhechenko/uuid05',
    license='MIT',
    author='Oleg Strizhechenko',
    author_email='oleg.strizhechenko@gmail.com',
    description='Compact human-readable almost unique identifiers for temporary objects in '
                'small non-synchronizing distributed systems.',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    scripts=['cli/uuid05'],
)
