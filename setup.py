from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vibecod",
    version="2.1.0",
    author="VibaCoding",
    author_email="roma.lukanin.00@gmail.com",
    description="VIBE Language — гибридный язык с квантовой душой",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VibaCoding/vibecod",
    project_urls={
        "Bug Tracker": "https://github.com/VibaCoding/vibecod/issues",
        "Source Code": "https://github.com/VibaCoding/vibecod",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Interpreters",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "vibe = vibecod.__main__:main",
            "vibecod = vibecod.__main__:main",
        ],
    },
    install_requires=[],
    include_package_data=True,
)
