from setuptools import setup

setup(
    name='bingtiles',
    version='0.0.1',
    description='Small library for accessing Bing Static Maps API',
    author='Tolga Demirdal',
    url='https://github.com/shadymeowy/python-bing-tiles',
    setup_requires=[],
    install_requires=['requests', 'Pillow'],
    packages=['bingtiles', 'bingtiles.provider'],
    entry_points={
        'console_scripts': [
            'bingtiles = bingtiles.__main__:main',              
        ],          
    },
    extras_require={
        'processbar': ['tqdm'],
    },
)
 
