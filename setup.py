from setuptools import setup, find_packages
from pathlib import Path

REQUIREMENTS = [
    "IPython"
    "pandas",
    "numpy",
    "thermo",
    "re",
    "openai",
    "getpass",
    "sys",
    "brightway2"
]

setup(
    name='fauldier',
    version='0.1.0',
    author="Lukas Lazar",
    author_email="lukas.lazar@mail.de",
    description=(
    "Framework for lArge langUage moDel assIsted lifE cyclE inventoRy"
    "This library converts data from a generic Life Cycle Inventory (LCI) spreadsheet to the specific format" 
    "required for import into Brightway. It utilizes Large Language Models to automatically map non-standard names and"
    "handle inputs with typos, in multiple languages and unit inconsistencies."
    ),
    license="BSD",
    keywords="Life Cycle Assessment LCA Large Language Model LLM",
    url="https://github.com/ljlazar/fauldier",
    project_urls={
        "Publication": "" ,
        "Homepage": "https://github.com/ljlazar/fauldier",
        "Repository": "https://github.com/ljlazar/fauldier.git",
    },
    packages=["fauldier"],
    long_description=(Path(__file__).parent / "README.md").read_text(encoding='utf-8'),
    long_description_content_type="text/markdown",
    classifiers=[],
    install_requires=REQUIREMENTS,
)