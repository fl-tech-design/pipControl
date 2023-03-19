from setuptools import setup
import os

temp_folder = "temp"
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

file1 = os.path.join(temp_folder, "installed_packs.txt")
if not os.path.exists(file1):
    with open(file1, "w") as f:
        f.write("Inhalt von file1.txt")

file2 = os.path.join(temp_folder, "outdated_packs.txt")
if not os.path.exists(file2):
    with open(file2, "w") as f:
        f.write("Inhalt von file2.txt")

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
