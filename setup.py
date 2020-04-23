import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wxparams",
    version="1.0",
    author="Yoshiki Kato",
    # author_email="",
    description="Weather Parameters Calculator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yoshiki443/weather_parameters",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT'
)
