.. _installation_guide:

Installation
************

Mesmerize can be installed on Linux, Mac OSX and Windows. For Linux we provide a snap package which comes with everything and doesn't require management of virtual environments or anaconda. On Windows, Mesmerize can be installed in an anaconda environment. For Mac OSX and Linux you may use either virtual environments or conda environments, but we have had much better experience with virtual environments.

.. _snap_install:

Linux
=====

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

.. _pypi_install:

pip (PyPI)
==========

**You will need python==3.6, there is a bug with Qt & python3.7**

Install python 3.6::
    # Debian & Ubuntu based
    sudo apt-get install python3.6
    # Fedora/CentOS
    sudo dnf install python36

Install build tools and other dependencies::
    
    # Debian & Ubuntu based distros
    sudo apt-get install build-essential python3-devel qt5-default tcl graphviz git
    
    # Fedora/CentOS
    sudo dnf install @development-tools
    sudo dnf install python3-devel tcl graphviz
    
It should be easy to google and find the name of the meta-package your your distribution uses to get necessary build tools.

If you're on Fedora/CentOS you'll also need ``redhat-rpm-config``, install using::
    sudo dnf install redhat-rpm-config
    
Create a new virtual environment::

    python3.6 -m venv <new_venv_path>

Activate this environment::
    
    source <new_venv_path/bin/activate>

Make sure you have a recent version of pip and setuptools::
    
    pip install --upgrade pip setuptools

install Cython & numpy::

    pip install Cython numpy

Install mesmerize::

    pip install mesmerize

Now you should be be able to launch mesmerize from the terminal::

    mesmerize
    
You will always need to activate the environment for Mesmerize before launching it.

If you want Caiman features you'll need to install caiman into this environment::

    git clone https://github.com/flatironinstitute/CaImAn
    cd CaImAn/
    source activate caiman
    pip install .

More information on caiman installation::

    https://caiman.readthedocs.io/en/master/Installation.html#installation-on-macos-and-linux

    
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

#. Install ``caiman`` for Caiman features::

    conda install -c conda-forge caiman

#. Install cython, numpy and pandas::

    conda install cython numpy pandas~=0.25.3

#. Install Mesmerize::

    pip install mesmerize

#. To launch Mesmerize call it from the terminal::

    mesmerize
    
You will always need to activate the environment for Mesmerize before launching it.

**You might get a matplotlib error, if so execute the following which appends the default matplotlib backend-option. Note that this will probably affect matplotlib in all your environments**::

    echo "backend: qt5" >> ~/.matplotlib/matplotlibrc

Windows
=======

Only Windows 10 is supported.

Download & install Anaconda for Python 3: https://www.anaconda.com/distribution/

You will also need git: https://gitforwindows.org/

.. warning:: It is **highly** recommended that you use Mesmerize in a new dedicated environment, even if you already have major dependencies (like caiman) installed in another environment.

**All commands are to be run in the powershell**

#. You will need anaconda to be accessible through powershell. You may need to run powershell as administrator for this step to to work. Close & open a new non-admin powershell after running this::

    conda init powershell

#. Create a new anaconda environment::

    conda create -n mesmerize

#. Activate the environment::

    conda activate mesmerize
    
#. Install caiman::

    conda install -c conda-forge caiman
    
#. Downgrade pandas::

    conda install pandas==0.25.3
        
#. Install tslearn::

    conda install -c conda-forge tslearn==0.2.1
    
#. Install graphviz::

    conda install graphviz
    
#. Install Mesmerize::
    
    pip install mesmerize

#. Allow powershell to execute scripts, this is required for the batch manager and k-Shape GUI which launch external processes. This may affect the security of your system by allowing scripts to be executable. I'm not an expert on Windows so if someone knows a better way to do this let me know! As far as I know, I'm not sure why you would try to execute untrusted scripts so this shouldn't be a concern?::

    Set-ExecutionPolicy RemoteSigned
    Set-ExecutionPolicy Bypass -scope Process -Force
    
#. Launch Mesmerize::

    mesmerize


From GitHub (Development)
=========================
First, make sure you have compilers & python3.6 (see the details above for various Linux distros or Mac OSX)
    
#. Create a virtual environment::
    
    # Choose a path to house the virtual environment
    python3.6 -m venv /path/to/venv
    
#. Activate the virtual environment::

    source /path/to/venv/bin/activate
    
#. Upgrade pip & setuptools & install some build dependencies::

    pip install --upgrade pip setuptools
    pip install Cython numpy

#. Fork the main repo on github and clone it::

    git clone https://github.com/<your_github_username>/MESmerize.git
    cd MESmerize
    
#. Switch to new branch::

    git checkout -b my-new-feature

#. Install in editable mode::

    pip install -e .

#. Make your changes to the code & push to your fork::

    git push origin my-new-feature
    
#. Create a pull request if you want to incorporate it into the main Mesmerize repo.
