from setuptools import setup, find_packages


setup(
    name='earthsight',
    version='0.1.0',
    description='A tool to explore, analyze and understand earth observation data',
    url='https://github.com/k3blu3/earthsight',
    author='Krishna Karra',
    author_email='krishna.karra@gmail.com',
    license='Creative Commons',
    packages=find_packages(),
    setup_requires=['setuptools>=50'],
    install_requires=[
        'bqplot==0.12.14',
        'earthengine-api==0.1.239',
        'GDAL==3.1.3',
        'ipyleaflet==0.13.3',
        'ipython==7.18.1',
        'ipywidgets==7.5.1',
        'jupyterlab==2.2.9',
        'matplotlib==3.3.2',
        'numpy==1.19.2',
        'pandas==1.1.3',
        'Pillow==8.0.1',
        'Shapely==1.7.1',
        'voila==0.2.4'
    ],
    entry_points={
        'console_scripts': [
            'es = earthsight.run.run:main'
        ]
    }
)
