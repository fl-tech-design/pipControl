from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='pipControl',
    version='0.1',
    author='fl-tech & design',
    author_email='fl-tech-desig@gmx.ch',
    description='A simple gui to control pip.',
    url='https://github.com/fl-tech-design/pipControl.git',
    install_requires=requirements
)
