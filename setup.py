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
        # User forgot to give an argument probably, let setuptools handle that.
        return True

    info_commands = ['--help-commands', '--name', '--version', '-V',
                     '--fullname', '--author', '--author-email',
                     '--maintainer', '--maintainer-email', '--contact',
                     '--contact-email', '--url', '--license', '--description',
                     '--long-description', '--platforms', '--classifiers',
                     '--keywords', '--provides', '--requires', '--obsoletes']
    # Add commands that do more than print info, but also don't need
    # any build step.
    info_commands.extend(['egg_info', 'install_egg_info', 'rotate'])

    for command in info_commands:
        if command in sys.argv[1:]:
            return False

    return True


s = dict(
    name='mesmerize',
    version='0.1',
    packages=find_packages(exclude=['use_cases', 'use_cases.*', 'tests']), #+ ['tests', 'tslearn', 'mesmerize.common', 'mesmerize.common.pytemplates', 'mesmerize.viewer',
              # 'mesmerize.viewer.core', 'mesmerize.viewer.modules', 'mesmerize.viewer.modules.pytemplates',
              # 'mesmerize.viewer.modules.custom_modules', 'mesmerize.viewer.modules.stimmap_modules',
              # 'mesmerize.viewer.modules.batch_run_modules', 'mesmerize.viewer.modules.roi_manager_modules',
              # 'mesmerize.viewer.modules.roi_manager_modules.read_imagej',
              # 'mesmerize.viewer.modules.script_editor_modules', 'mesmerize.viewer.image_menu',
              # 'mesmerize.viewer.image_utils', 'mesmerize.analysis', 'mesmerize.analysis.math',
              # 'mesmerize.analysis.pytemplates', 'mesmerize.analysis.pytemplates.old', 'mesmerize.plotting',
              # 'mesmerize.plotting.widgets', 'mesmerize.plotting.widgets.lda', 'mesmerize.plotting.widgets.kshape',
              # 'mesmerize.plotting.widgets.heatmap', 'mesmerize.plotting.widgets.scatter',
              # 'mesmerize.plotting.widgets.beeswarms', 'mesmerize.plotting.widgets.peak_editor',
              # 'mesmerize.plotting.widgets.plot_window', 'mesmerize.plotting.widgets.sosd_fourier',
              # 'mesmerize.plotting.widgets.cross_correlation', 'mesmerize.plotting.widgets.curve_plot_window',
              # 'mesmerize.plotting.variants', 'mesmerize.misc_widgets', 'mesmerize.pyqtgraphCore',
              # 'mesmerize.pyqtgraphCore.util', 'mesmerize.pyqtgraphCore.util.colorama', 'mesmerize.pyqtgraphCore.tests',
              # 'mesmerize.pyqtgraphCore.canvas', 'mesmerize.pyqtgraphCore.opengl',
              # 'mesmerize.pyqtgraphCore.opengl.items', 'mesmerize.pyqtgraphCore.console',
              # 'mesmerize.pyqtgraphCore.pixmaps', 'mesmerize.pyqtgraphCore.widgets', 'mesmerize.pyqtgraphCore.dockarea',
              # 'mesmerize.pyqtgraphCore.exporters', 'mesmerize.pyqtgraphCore.exporters.tests',
              # 'mesmerize.pyqtgraphCore.flowchart', 'mesmerize.pyqtgraphCore.flowchart.library',
              # 'mesmerize.pyqtgraphCore.imageview', 'mesmerize.pyqtgraphCore.metaarray',
              # 'mesmerize.pyqtgraphCore.multiprocess', 'mesmerize.pyqtgraphCore.GraphicsScene',
              # 'mesmerize.pyqtgraphCore.graphicsItems', 'mesmerize.pyqtgraphCore.graphicsItems.ViewBox',
              # 'mesmerize.pyqtgraphCore.graphicsItems.PlotItem', 'mesmerize.pyqtgraphCore.parametertree',
              # 'mesmerize.project_manager', 'mesmerize.project_manager.project_browser',
              # 'mesmerize.project_manager.project_browser.pytemplates'],
    include_package_data=True,
    entry_points={'console_scripts': ['mesmerize=mesmerize.__main__:main']},
    setup_requires=['cython', 'numpy', 'scipy', 'scikit-learn'],
    url='https://kushalkolar.github.io/MESmerize/',
    license='GNU General Public License v3.0',
    author='Kushal Kolar, Daniel Dondorp',
    author_email='kushalkolar@gmail.com',
    description='Calcium imaging analysis platform'
)

if is_building():
    try:
        from Cython.Distutils import build_ext as _build_ext
        #list_pyx = ['cydtw', 'cygak', 'cysax', 'cycc', 'soft_dtw_fast']
        numpy_include = pkg_resources.resource_filename('numpy', 'core/include')
        #ext = [Extension('tslearn.%s' % s, ['tslearn/%s.pyx' % s], include_dirs=[numpy_include]) for s in list_pyx]

        ext = [Extension("caiman.source_extraction.cnmf.oasis",
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
