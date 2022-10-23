from setuptools import setup, find_packages
from pathlib import Path
def load_requires():
    filename = Path(__file__).parent / "requirements.txt"
    with filename.open("r", encoding="utf-8") as fp:
        packages = []
        for line in fp:
            packages.append(line)
        return packages


setup (
    name="YoutubeAnalyzer",
    version="0.0.1",
    description="A a cli tool for youtube data ingestion",
    author="Derek Olson, Mathew Bauer, Boris Bugingo, Ernad Ljalic, Matthew Jones",
    author_email="dereko@derekolsondev.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "youtubeIngest=cl:main",
        ]
    },
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=load_requires()
)