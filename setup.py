from setuptools import setup, find_packages

setup(
    name="recruitment_agency_new",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'agency-swarm',
        'python-dotenv'
    ]
) 