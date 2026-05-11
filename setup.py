from setuptools import setup, find_packages

setup(
    name="vibecod",
    version="2.0.0",
    description="VIBE Language",
    author="VIBE Team",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "vibecod = vibecod.__main__:main",
            "vibe = vibecod.__main__:main"
        ]
    },
)
