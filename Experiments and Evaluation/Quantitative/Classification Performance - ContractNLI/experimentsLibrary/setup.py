from setuptools import setup, find_packages

# Read the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='experimentsLibrary',  
    version='1.0.0',
    author='Raptopoulos Petros',
    author_email='petrosrapto@gmail.com',
    description='A library for conducting experiments for different models, APIs and prompting methods tailored for the ContractNLI dataset',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(where="src"),  # Finds all modules in `src/`
    package_dir={"": "src"},  # Treats `src` as the root for modules
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
