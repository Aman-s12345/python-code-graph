from setuptools import setup, find_packages

# This code reads your README.md file 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python-code-graph",
    version="0.1.1",
    author="Aman Singh",
    author_email="amansinghbiuri@gmail.com",
    description="Generate code graphs for Python projects",
    # Now use the variable instead of a string literal
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aman-s12345/python-code-graph.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "python-code-graph=python_code_graph.cli:main",
        ],
    },
)