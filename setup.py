import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="p4-bench-api-thaprau",
    version="0.0.1",
    author="Johan Paulsson",
    author_email="johan.paulsson@combitech.com",
    description="Package for creating network configuration files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thaprau/p4_bench_api",
    project_urls={
        "Bug Tracker": "https://github.com/thaprau/p4_bench_api/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)