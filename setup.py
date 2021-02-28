from setuptools import setup, find_packages
from pathlib import Path


entry_points = {'console_scripts': ['mesmerize=mesmerize.__main__:main']}

install_requires = \
    [
        "cycler==0.10.0",
        "dask>=1.1.1",
        "future>=0.18.2",
        "h5py~=2.10.0",
        "ipykernel>=4.10",
        "ipython>=7.15.0",
        "ipyparallel>=6.3",
        "MarkupSafe>=1.1.1",
        "matplotlib<=3.2.1",
        "opencv-contrib-python>=4.2",
        "opencv-python>=4.2",
        "pandas~=0.25.3",  # do not change
        "Pillow>=5.4.1",
        "psutil~=5.8.0",
        "PyQt5>=5.9.2,<=5.12",
        "python-dateutil>=2.8.0",
        "QtPy>=1.6.0",
        "qtap",
        "scikit-image~=0.15.0",  # do not change
        "scikit-learn~=0.23.1",  # tslearn 0.4 has issues with newer sklearn
        "scipy>=1.2.1",  # do not change
        "seaborn==0.9.0",  # do not change
        "spyder==3.3.3",  # do not change
        "tifffile",  # do not change
        "tqdm>=4.37.0",
        "PeakUtils",  # caiman requirement
        "tables>=3.6.1",
        "joblib>=0.15.1",
        #"tslearn~=0.2.2",  # had to remove because of windows
        "graphviz>=0.13",
        "numba>=0.50.0",
        #"bottleneck==1.2.1",  # do not change
        "holoviews",
        "jupyter",
        "pynwb",  # caiman requirement
        "pyqtgraph",
        #"tensorflow~=1.15.0",  # do not change, caiman requirement
        "tk",  # do not change
        "tcl",
        "bokeh>=2.2.0",
        "nuset-lib",
        "sk-video"
    ]

classifiers = \
    [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
        "Intended Audience :: Science/Research"
    ]

with open("readme-pypi.md", 'r') as fh:
    long_description = fh.read()


with open(Path(__file__).parent.joinpath('mesmerize').joinpath('VERSION'), 'r') as vf:
    vesion_str = vf.read().split('\n')[0]


setup(
    name='mesmerize',
    version=vesion_str,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    entry_points=entry_points,
    url='https://github.com/kushalkolar/MESmerize',
    license='GNU General Public License v3.0',
    author='Kushal Kolar, Daniel Dondorp',
    author_email='kushalkolar@gmail.com',
    description='Calcium imaging analysis platform',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=classifiers,
    python_requires='~=3.6,<3.7',
    install_requires=install_requires
)
