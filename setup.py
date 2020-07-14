from setuptools import setup, find_packages


setup(
    name='mesmerize',
    version='0.1',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    entry_points={'console_scripts': ['mesmerize=mesmerize.__main__:main']},
    # setup_requires=['cython', 'numpy', 'scipy', 'scikit-learn', 'numba', 'joblib'],
    url='https://kushalkolar.github.io/MESmerize/',
    license='GNU General Public License v3.0',
    author='Kushal Kolar, Daniel Dondorp',
    author_email='kushalkolar@gmail.com',
    description='Calcium imaging analysis platform'
)
