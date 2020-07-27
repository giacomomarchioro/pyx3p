import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="x3p",
    version="0.0.4",
    author="Giacomo Marchioro",
    author_email="giacomomarchioro@outlook.com",
    description="Unofficial Python module that allows opening the .x3p file format created by OpenGPS consortium",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/giacomomarchioro/pyx3p",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
