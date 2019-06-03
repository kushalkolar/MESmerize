from setuptools import setup

setup(
    name='mesmerize',
    version='0.1',
    packages=['common', 'viewer', 'viewer.core', 'viewer.modules', 'viewer.modules.custom_modules',
              'viewer.modules.stimmap_modules', 'viewer.modules.batch_run_modules',
              'viewer.modules.roi_manager_modules', 'viewer.modules.roi_manager_modules.read_imagej',
              'viewer.image_menu', 'viewer.image_utils', 'analysis', 'analysis.pytemplates', 'plotting',
              'plotting.widgets', 'plotting.widgets.lda', 'plotting.widgets.kshape', 'plotting.widgets.heatmap',
              'plotting.widgets.scatter', 'plotting.widgets.beeswarms', 'plotting.widgets.peak_editor',
              'plotting.widgets.plot_window', 'plotting.widgets.cross_correlation',
              'plotting.widgets.curve_plot_window', 'plotting.variants', 'clustering', 'clustering.PCA', 'misc_widgets',
              'pyqtgraphCore', 'pyqtgraphCore.util', 'pyqtgraphCore.util.colorama', 'pyqtgraphCore.tests',
              'pyqtgraphCore.canvas', 'pyqtgraphCore.opengl', 'pyqtgraphCore.opengl.items', 'pyqtgraphCore.console',
              'pyqtgraphCore.pixmaps', 'pyqtgraphCore.widgets', 'pyqtgraphCore.dockarea', 'pyqtgraphCore.exporters',
              'pyqtgraphCore.exporters.tests', 'pyqtgraphCore.flowchart', 'pyqtgraphCore.flowchart.library',
              'pyqtgraphCore.imageview', 'pyqtgraphCore.metaarray', 'pyqtgraphCore.multiprocess',
              'pyqtgraphCore.GraphicsScene', 'pyqtgraphCore.graphicsItems', 'pyqtgraphCore.graphicsItems.ViewBox',
              'pyqtgraphCore.graphicsItems.PlotItem', 'pyqtgraphCore.parametertree', 'project_manager',
              'project_manager.project_browser'],
    url='https://kushalkolar.github.io/MESmerize/',
    license='GNU General Public License v3.0 ',
    author='Kushal Kolar, Daniel Dondorp',
    author_email='kushalkolar@gmail.com',
    description='Calcium imaging analysis platform'
)
