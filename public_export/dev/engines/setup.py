from setuptools import setup, find_packages

setup(
    name="osintneoai",
    version="1.0.0",
    description="OSINTNeoAi Master Intelligence & Forensic Investigation Suite",
    author="Anthony Michael DiMarcello III",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "g4f>=0.3.0",
        "pydantic>=2.0.0",
        "google-cloud-bigquery>=3.25.0",
        "shodan>=1.30.0",
        "maltego-trx>=1.6.0"
    ],
    entry_points={
        "console_scripts": [
            "osintneoai=cli.cli:main",
            "osintcli=cli.cli:main"
        ]
    },
    python_requires=">=3.10",
)
