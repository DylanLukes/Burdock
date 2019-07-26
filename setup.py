from setuptools import setup

from os import path
project_dir = path.abspath(path.dirname(__file__))
with open(path.join(project_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='burdock',
    version='0.1.2',
    packages=['burdock.cli',
              'burdock.core',
              'burdock.expander',
              'burdock.matcher',
              'burdock.util'],
    url='https://github.com/DylanLukes/burdock',
    license='BSD 3-Clause',

    author='Dylan A. Lukes',
    author_email='dlukes@eng.ucsd.edu',
    description='A Daikon frontend for Python data frames and CSV/TSV files.',

    long_description=long_description,
    long_description_content_type='text/markdown',

    install_requires=['pandas', 'jinja2'],
    entry_points= {
        'console_scripts': ['burdock=burdock.cli.__main__:entry'],
    },

    include_package_data=True
)
