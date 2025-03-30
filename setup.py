from setuptools import setup, find_packages

setup(
    name="summit-seo",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.12.3",
        "requests>=2.31.0",
        "pandas>=2.2.1",
        "pydantic>=2.4.2",
        "pydantic-settings>=2.0.3",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.2",
            "pytest-cov>=4.1.0",
            "black>=24.2.0",
            "mypy>=1.8.0",
            "flake8>=7.0.0",
            "types-requests>=2.31.0",
            "types-beautifulsoup4>=4.12.0",
        ],
    },
    python_requires=">=3.12",
) 