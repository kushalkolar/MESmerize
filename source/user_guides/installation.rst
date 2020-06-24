.. _installation_guide:

Installation
************

**We currently support Linux & Mac OS X. On Windows it is tricky to set up an environment that works reliably with compilers for building some dependencies. From our experience it's much easier to just install Linux and use the Snap.**

.. _snap_install:

Linux
====

The easiest way to get Mesmerize is through the Snap Store. You can also install from the GitHub repo.

Snap
----

.. image:: https://snapcraft.io/static/images/badges/en/snap-store-black.svg
  :target: https://snapcraft.io/mesmerize

Command line snap installation::

    sudo snap install mesmerize

After installation simply run ``mesmerize`` in the terminal and the application will launch in ~10-30 seconds. Make sure your PYTHONPATH environment variable is empty otherwise it might conflict with the snap::

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
^^^^^^^^^^^^

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
^^^^^^^^^^^

The snap installation has several limitations, most importantly you will not be able to access arbitrary filesystems. If you need this you will have to install directly from the repo (see From GitHub). If you are able to mount your external filesystem in /media (or wherever your distro places removeable media) then you should be able to access these filesystems if you do the following::

    sudo snap connect mesmerize:removable-media

Alternatively you can install the snap in devmode (gives that snap broad access to the system)::

    sudo snap install mesmerize --devmode
	
.. warning:: Analysis graphs do not work in the snap version at the moment.

From GitHub
-----------

First, make sure you have compilers & python.

**For Debian & Ubuntu based distros**

Get build tools and other things::

    sudo apt-get install build-essential
    
For other distros look for the equivalent meta-package that contains gcc, glibc, etc.

If you don't have python3.6::

    sudo apt-get install python3.6

For other distros lookup how to install python3.6 through their package manager.
    
Install dependencies::

    sudo apt-get install qt5-default tcl graphviz git

For other distros these packages probably have the same or similar names.

**Create a virtual environment & install Mesmerize**
    
#. Create a virtual environment::
    
    # Choose a path to house the virtual environment
    python3.6 -m venv /path/to/venv
    
#. Activate the virtual environment::

    source /path/to/venv/bin/activate

#. Clone the repo::

    git clone https://github.com/kushalkolar/MESmerize.git


#. cd & switch to the snap branch::
    
    cd MESmerize
    git checkout snap

#. Install some build dependencies::

    pip install Cython numpy python-dateutil
    
#. Install remaining dependencies::

    pip install -r requirements.txt

#. Build some things::

    python setup.py build_ext -i

#. Add to PYTHONPATH environment variable. You will always need to add the path to MESmerize to the PYTHONPATH environment varible before launching.::

    export PYTHONPATH=$PWD:$PYTHONPATH
    
#. Launch::

    python ./mesmerize

    
Mac OSX
=======

This requires Anaconda and will install Mesmerize in an Anaconda environment. Tested on macOS Catalina 10.15.1

Download Anaconda for Python 3: https://www.anaconda.com/distribution/
    
First make sure you have xcode::

    xcode-select --install

This might take a while.

**Create an environment & install Mesmerize**

#. Create a new environment using python 3.6::

    conda create --name mesmerize python=3.6

#. Enter the environment::

    source activate mesmerize

#. Install cython, numpy and pandas::

    conda install cython numpy pandas

#. Clone the mesmerize repo and enter it::

    git clone https://github.com/kushalkolar/MESmerize.git
    cd MESmerize

#. Checkout the snap branch::

    git checkout snap

#. Install more dependencies::

    pip install -r requirements.txt

#. Install Mesmerize::

    CFLAGS='-stdlib=libc++' python setup.py build_ext -i

**Launching Mesmerize**

#. Export the path to the MESmerize repo directory::

    export PYTHONPATH=<path_to_MESmerize_dir>

#. Launch. It may take a few minutes the first time::

    python <path_to_MESmerize_dir>/mesmerize

**You might get a matplotlib error, if so execute the following which appends the default matplotlib backend-option. Note that this will probably affect matplotlib in all your environments**::

    echo "backend: qt5" >> ~/.matplotlib/matplotlibrc

Windows
=======

Only Windows 10 is supported.

Download & install Anaconda for Python 3: https://www.anaconda.com/distribution/

You will also need git: https://gitforwindows.org/

.. warning:: It is **highly** recommended that you use Mesmerize in a new dedicated environment, even if you already have major dependencies (like caiman) installed in another environment.

**All commands are to be run in the powershell**

#. You will need anaconda to be accessible through powershell. You may need to run powershell as administrator for this stepo to work. Close & open a new non-admin powershell after running this::

    conda init powershell

#. Create a new anaconda environment::

    conda create -n mesmerize
    
#. Install caiman::

    conda install -c conda-forge caiman
    
#. Downgrade pandas::

    conda install pandas==0.25.3
    
#. Install some packages::

    pip install scikit-learn==0.20.2 tifffile==0.15.1 opencv-python opencv-contrib-python Cython tables==3.5.2 Pillow==5.4.1 seaborn==0.9.0 spyder==3.3.3 graphviz
    
#. Install tslearn::

    conda install -c conda-forge tslearn==0.2.1
    
#. Install graphviz, this is different from the python interface to graphviz installed through pip::

    graphviz

#. Allow powershell to execute scripts, this is required for the batch manager and k-Shape GUI which launch external processes. This may affect the security of your system by allowing scripts to be executable. I'm not an expert on Windows so if someone knows a better way to do this let me know! As far as I know, I'm not sure why you would even try to execute untrusted scripts so this shouldn't be a concern?::

    Set-ExecutionPolicy RemoteSigned
    Set-ExecutionPolicy Bypass -scope Process -Force
    
#. Clone Mesmerize::

    git clone https://github.com/kushalkolar/MESmerize.git
    
#. Add the path to the MESmerize dir to your ``PYTHONPATH``. In the start menu enter "edit environment variables for your account", create a a new variable called ``PYTHONPATH`` and enter the path to the MESmerize dir. Or add the path to the MESmerize dir if you already have a ``PYTHONPATH`` environment variable

#. Launch Mesmerize::

    python <path to MESmerize dir>/mesmerize

    
Troubleshooting
===============

Qt version
----------
    
.. _pip_install:

PyPI
====
