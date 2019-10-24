import sys
from setuptools import setup, Extension, find_packages
import pkg_resources


def is_building():
    """
	Parse the setup.py command and return whether a build is requested.
	If False is returned, only an informational command is run.
	If True is returned, information about C extensions will have to
	be passed to the setup() function.
	"""
    if len(sys.argv) < 2:
        return True

    info_commands = ['--help-commands', '--name', '--version', '-V',
                     '--fullname', '--author', '--author-email',
                     '--maintainer', '--maintainer-email', '--contact',
                     '--contact-email', '--url', '--license', '--description',
                     '--long-description', '--platforms', '--classifiers',
                     '--keywords', '--provides', '--requires', '--obsoletes']

    info_commands.extend(['egg_info', 'install_egg_info', 'rotate'])

    for command in info_commands:
        if command in sys.argv[1:]:
            return False

    return True


s = dict(
    name='mesmerize',
    version='0.1',
    packages=find_packages(exclude=['use_cases', 'use_cases.*', 'tests']),
    include_package_data=True,
    entry_points={'console_scripts': ['mesmerize=mesmerize.__main__:main']},
    setup_requires=['cython', 'numpy', 'scipy', 'scikit-learn', 'numba', 'joblib'],
    url='https://kushalkolar.github.io/MESmerize/',
    license='GNU General Public License v3.0',
    author='Kushal Kolar, Daniel Dondorp',
    author_email='kushalkolar@gmail.com',
    description='Calcium imaging analysis platform'
)

if is_building():
    try:
        from Cython.Distutils import build_ext as _build_ext
        list_pyx = ['cygak', 'cysax', 'cycc', 'soft_dtw_fast']
        numpy_include = pkg_resources.resource_filename('numpy', 'core/include')
        ext = [Extension('tslearn.%s' % s, ['tslearn/%s.pyx' % s], include_dirs=[numpy_include]) for s in list_pyx]

        ext += [Extension("caiman.source_extraction.cnmf.oasis",
                                 sources=["caiman/source_extraction/cnmf/oasis.pyx"],
                                 include_dirs=[numpy_include],
                                 language="c++")]

        b = dict(include_dirs=[numpy_include],
                 ext_modules=ext,
                 cmdclass={'build_ext': _build_ext})
    except:
        b = {}
    setup(**{**s, **b})

else:
    setup(**s)

