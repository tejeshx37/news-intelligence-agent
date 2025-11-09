#!/usr/bin/env python3
"""
Setup script for News Intelligence Agent
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

def read_requirements():
    """Read requirements from requirements.txt"""
    requirements_path = Path(__file__).parent / 'requirements.txt'
    if requirements_path.exists():
        with open(requirements_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

def read_readme():
    """Read README.md file"""
    readme_path = Path(__file__).parent / 'README.md'
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "News Intelligence Agent - AI-powered news analysis and processing"

setup(
    name="news-intelligence-agent",
    version="1.0.0",
    author="News Intelligence Team",
    author_email="team@newsintelligence.com",
    description="AI-powered news analysis and processing system",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/news-intelligence-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.991',
        ],
        'torch': [
            'torch>=1.12.0',
            'transformers>=4.20.0',
        ],
        'advanced': [
            'spacy>=3.4.0',
            'textblob>=0.17.1',
            'newspaper3k>=0.2.8',
        ],
    },
    entry_points={
        'console_scripts': [
            'news-intelligence=news_intelligence.cli:main',
            'train-models=news_intelligence.train:main',
            'upload-models=s3_upload.upload_to_s3:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.txt', '*.md', '*.json', '*.yml', '*.yaml'],
    },
    zip_safe=False,
)