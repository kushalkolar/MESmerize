.. _installation_guide:

Installation
************

.. _snap_install:

Snap
====


The easiest way to get Mesmerize is through the Snap Store

.. image:: https://snapcraft.io/static/images/badges/en/snap-store-black.svg
  :target: https://snapcraft.io/mesmerize

Command line snap installation:
``sudo snap install mesmerize``

After installation simply run ``mesmerize`` in the terminal and the application will launch in ~10-30 seconds.

Make sure you have ``snapd`` installed, which is required for running snap apps.
Ubuntu 16.04 and later usually come pre-installed with snapd.

You should be able to install ``snapd`` through apt for most Debian based distros::

	sudo apt update
	sudo apt install snapd

Installing ``snapd`` on Fedora::

	sudo dnf install snapd

To install ``snapd`` on other distros please see: https://docs.snapcraft.io/installing-snapd

If you have trouble installing Mesmerize via snap you might need to install `core18 <https://snapcraft.io/core18>`_ first::

	sudo snap install core18
	
.. note:: You might get the following warnings when you launch the snap, this is normal. Just be patient and wait a few minutes:

    /snap/mesmerize/x1/lib/python3.6/site-packages/tifffile/tifffile.py:8211: UserWarning: No module named 'numpy.core._multiarray_umath'
    Functionality might be degraded or be slow.

    warnings.warn('%s%s' % (e, warn))
    /snap/mesmerize/x1/lib/python3.6/site-packages/matplotlib/font_manager.py:281: UserWarning: Matplotlib is building the font cache using fc-list. This may take a moment.
    'Matplotlib is building the font cache using fc-list. '
    Bokeh could not be loaded. Either it is not installed or you are not running within a notebook
    Loading, please wait... 
    Qt: Session management error: None of the authentication protocols specified are supported



.. _pip_install:

PyPI
====
