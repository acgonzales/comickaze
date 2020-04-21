import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="Comickaze",
    version="2.0.0",
    author="Aaron Gonzales",
    author_email="aaroncgonzales.dev@gmail.com",
    description="A package to search and download comics on ReadComicsOnline.ru",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Chr1st-oo/comickaze",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests",
        "bs4",
        "coloredlogs",
        "colorama",
        "progress",
        "img2pdf",
        "Click",
        "pyinquirer"
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    entry_points="""
        [console_scripts]
        comickaze=cli:cli
    """
)
