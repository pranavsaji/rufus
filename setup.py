# setup.py

from setuptools import setup, find_packages

setup(
    name='Rufus',
    version='0.2.0',  # Incremented version
    packages=find_packages(),
    install_requires=[
        'aiohttp==3.10.10',
        'aiodns==3.2.0',
        'beautifulsoup4==4.12.3',
        'tqdm==4.66.5',
        'playwright==1.48.0',
        'sentence-transformers==3.2.1',
        'numpy==2.0.2',
        'scipy==1.13.1',
        'nltk==3.8.1',          
        'scikit-learn==1.5.2',     
        'spacy==3.8.2',
        'fastapi==0.115.3',
        'uvicorn==0.32.0',
        'nltk==3.8.1'
    ],
    author='Pranav Saji',
    author_email='pranavs.mec@gmail.com',
    description='Rufus: Intelligent Web Data Extraction Tool for LLMs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/pranavsaji/rufus',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'rufus=run_rufus:main',
        ],
    },
)

