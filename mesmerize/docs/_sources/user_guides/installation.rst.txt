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


.. _pip_install:

PyPI
====
