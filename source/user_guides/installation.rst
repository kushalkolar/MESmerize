.. _installation_guide:

Installation
************

.. _snap_install:

Snap
====

Installation
------------

The easiest way to get Mesmerize is through the Snap Store

.. image:: https://snapcraft.io/static/images/badges/en/snap-store-black.svg
  :target: https://snapcraft.io/mesmerize

Command line snap installation::

    sudo snap install mesmerize

Launch
------

After installation simply run ``mesmerize`` in the terminal and the application will launch in ~10-30 seconds. Make sure your PYTHONPATH environment variable is empty otherwise it might conflict with the snap.::

    export PYTHONPATH=
    
You can also open an ipython console in the snap environment::

    mesmerize.ipython
    
.. note:: You might get the following warnings when you launch the snap, this is normal. Just be patient and wait a few minutes:

        | warnings.warn('%s%s' % (e, warn))
        | /snap/mesmerize/x1/lib/python3.6/site-packages/matplotlib/font_manager.py:281: UserWarning: Matplotlib is building the font cache using fc-list. This may take a moment.
        | 'Matplotlib is building the font cache using fc-list. '
        | Bokeh could not be loaded. Either it is not installed or you are not running within a notebook
        | Loading, please wait... 
        | Qt: Session management error: Authentication Rejected, reason : None of the authentication protocols specified are supported and host-based authentication failed

    
Requirements
------------

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

Limitations
-----------

The snap installation has several limitations, most importantly you will not be able to access arbitrary filesystems. If you need this you will have to install directly from the repo (see From GitHub). If you are able to mount your external filesystem in /media (or wherever your distro places removeable media) then you should be able to access these filesystems if you do the following::

    sudo snap connect mesmerize:removable-media

Alternatively you can install the snap in devmode (gives that snap broad access to the system)::

    sudo snap install mesmerize --devmode
	
.. warning:: Analysis graphs do not work in the snap version at the moment.

From GitHub
===========

Easy
----

This installation method should work on Linux and Mac.

First, make sure you have compilers & python.

**For Debian & Ubuntu based distros**

    Get build tools and other things::

        sudo apt-get install build-essential
        
    For other distros look for the equivalent meta-package that contains gcc, glibc, etc.

    If you don't have python3.6::

        sudo apt-get install python3.6
    
    For other distros lookup how to install python3.6 through their package manager.
        
    Install dependencies::

        sudo apt-get install qt5-default tcl graphviz
    
    For other distros these packages probably have the same or similar names.
    
**For Mac OSX**
    
    Install Xcode::
        xcode-select --install

    This might take a while.

    Install brew::

        /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

    Install python 3.6.5::

        brew install https://raw.githubusercontent.com/Homebrew/homebrew-core/f2a764ef944b1080be64bd88dca9a1d80130c558/Formula/python.rb

**Install Mesmerize**
    
#. Create a virtual environment::
    
    # Choose a path to house the virtual environment
    python3.6 -m venv /path/to/venv
    
#. Activate the virtual environment::

    source /path/to/venv/bin/activate

#. Install some dependencies::

    pip install cython numpy python-dateutil
    
#. Install mesmerize::

    pip install git+https://github.com/kushalkolar/MESmerize.git@snap

Customized
----------


    
Troubleshooting
===============

Qt version
----------
    
.. _pip_install:

PyPI
====
