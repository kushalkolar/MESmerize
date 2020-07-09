from setuptools import setup, find_packages
from mesmerize import __version__

with open("README.md", 'r') as fh:
    long_description = fh.read()

setup(
    name='mesmerize',
    version=__version__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    entry_points={'console_scripts': ['mesmerize=mesmerize.__main__:main']},
    # setup_requires=['cython', 'numpy', 'scipy', 'scikit-learn', 'numba', 'joblib'],
    url='https://kushalkolar.github.io/MESmerize/',
    license='GNU General Public License v3.0',
    author='Kushal Kolar, Daniel Dondorp',
    author_email='kushalkolar@gmail.com',
    description='Calcium imaging analysis platform',
    long_description=long_description,
    classifiers=[
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
    ],
    python_requires='>=3.6'
)
