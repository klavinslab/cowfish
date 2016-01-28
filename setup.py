try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'cowfish',
    'author': 'Yaoyu Yang',
    'url': 'https://github.com/klavinslab/cowfish',
    'download_url': 'https://github.com/klavinslab/cowfish.git',
    'author_email': 'yaoyu _at_ uw.edu',
    'version': '0.0.5',
    'install_requires': ['FlowCytometryTools', 'aquariumapi', 'pandas'],
    'packages': ['cowfish'],
    'scripts': [],
    'name': 'cowfish',
    'license': 'Copyright University of Washington'
}

setup(**config)
