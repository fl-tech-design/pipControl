from setuptools import setup

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name='pipControl',
    version='0.0.2',
    author='fl-tech & design',
    author_email='fl-tech-design@gmx.ch',
    description='A simple gui to control pip commands.',
    url='https://github.com/fl-tech-design/pipControl.git',
    install_requires=requirements
)
