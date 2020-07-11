from setuptools import setup, find_packages


setup(
    name='snap_dummy',
    version='0.0.0',
    packages=find_packages(),
    url='https://github.com/kushalkolar/MESmerize',
    license='GNU General Public License v3.0',
    author='Kushal Kolar, Daniel Dondorp',
    author_email='kushalkolar@gmail.com',
    description='dummy for snap',
    long_description='',
    install_requires=['Cython', 'numpy', 'python-dateutil']
)
