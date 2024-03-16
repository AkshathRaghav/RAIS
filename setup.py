from setuptools import find_packages, setup


def parse_requirements(filename: str) -> typing.List[str]:
    """
    Load requirements from a pip requirements file
    :param: filename - name of the requirements file to be parsed
    :return: list - list of modules mentioned in the requirements file
    """
    line_iter = (line.strip() for line in open(filename))
    return [line for line in line_iter if line and not line.startswith("#")]


requirements = [ir for ir in parse_requirements("requirements.txt")]
dev_requirements = [ir for ir in parse_requirements("requirements_dev.txt")]

setup(
    name="RAIS",
    version="0.0.1",
    author="Purdue RAIS",
    author_email="yunglu@purdue.edu",
    description="Tool to analyze the reproducibility of Artificial Intelligence Research",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AkshathRaghav/RAIS",
    packages=find_packages(),
    install_requires=requirements,
    tests_require=dev_requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires="~3.9.0",
)
