import setuptools


setuptools.setup(
    name="XyzB0ts",
    version="0.1",
    url="https://github.com/f88af65a/XyzB0ts",
    package_dir={"":"."},
    packages=setuptools.find_packages(where="."),
    requires=["redis","aiohttp","pillow"]
)
