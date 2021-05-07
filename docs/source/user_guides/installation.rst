.. _installation_guide:

Installation
************

Mesmerize can be installed on Linux, Mac OSX and Windows. On Windows, Mesmerize can be installed in an anaconda environment. For Mac OSX and Linux you may use either virtual environments or conda environments, but we have had much better experience with virtual environments.

All platforms
=============

We provide a ready to use VM with Mesmerize and all features pre-installed. You can run this VM on Windows, Mac OSX, or Linux. This is the easiest way to get started with Mesmerize if you don't want to setup anaconda or virtual environments by yourself. Just install VirtualBox and import the ``mesmerize-v060-vm.ova`` file.

- VirtualBox: https://www.virtualbox.org/wiki/Downloads
- Download the VM file ``mesmerize-v060-2-vm.ova`` from zenodo: https://zenodo.org/record/4738514

When you start the VM, just double click the mesmerize launcher on the desktop.

- You can setup *Shared Folders* in the settings for the VM to share data between the VM and your host computer.
- You can mount network drives etc. from within the VM.
- Do not delete the ``venvs`` directory, this will remove the virtual environment for Mesmerize.
- An example batch with a few examples from the caiman sample data is provided at ``/home/user/example_batch``.

The details for the user account on the VM are:

username: ``user`` |
password: ``password`` |

You can use the same password for ``sudo``.

By default the VM is set to use 7 threads and 12GB of RAM. You may modify this according to the resources available on your host computer. You generally want to leave 2-4 threads free on your host computer.

If you get the following error when importing the VM you probably don't have enough space on your computer, I recommend importing the VM on a computer that has a few hundred gigabytes of free space::

    E_INVALIDARG (0x80070057)

Video instructions:

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/IQIHo4r-WIw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


To update Mesmerize in the VM::

    # activate the environment
    source ~/venvs/mesmerize/bin/activate
    # get the latest version of mesmerize
    pip install --upgrade mesmerize

.. note:: Virtualization features of your CPU must be enabled in your BIOS. VirtualBox will throw errors if it is not.

Linux
=====

pip (PyPI)
----------

**You will need python==3.6 for tensorflow v1**

#. Install python 3.6::

    # Debian & Ubuntu based
    sudo apt-get install python3.6
    
    # Fedora/CentOS
    sudo dnf install python36
    
.. note:: If you're using Ubuntu 20.04 you'll need to add a PPA to get python3.6

    .. code-block::

        sudo add-apt-repository ppa:deadsnakes/ppa
        sudo apt update
        sudo apt install python3.6 python3.6-dbg python3.6-dev python3.6-doc python3.6-gdbm python3.6-gdbm-dbg python3.6-tk python3.6-tk-dbg python3.6-venv


#. Install build tools and other dependencies::
    
    # Debian & Ubuntu based distros
    sudo apt-get install build-essential python3.6-dev python3.6-venv qt5-default tcl graphviz git llvm
    
    # Fedora/CentOS
    sudo dnf install @development-tools
    sudo dnf install python3-devel tcl graphviz
    sudo dnf install llvm
    
For other distributions install the equivalent meta package to get build tools.

If you're on Fedora/CentOS you'll also need ``redhat-rpm-config``, install using::

    sudo dnf install redhat-rpm-config
    
#. Create a new virtual environment::

    python3.6 -m venv <new_venv_path>

#. Activate this environment::
    
    source <new_venv_path/bin/activate>

#. Make sure you have a recent version of pip and setuptools::
    
    pip install --upgrade pip setuptools
    
#. Install numpy & cython::

    pip install numpy cython

#. Install ``tensorflow`` v1.15 (v2 is not supported for nuset) if you want to use Caiman or Nuset::
    
    # CPU bound
    pip install tensorflow~=1.15
    # GPU
    pip install tensorflow-gpu~=1.15
    
#. Install tslearn & bottleneck (optional)::

    pip install tslearn~=0.4.1 bottleneck==1.2.1

#. Install mesmerize::

    pip install mesmerize

#. Now you should be be able to launch mesmerize from the terminal::

    mesmerize
    
You will always need to activate the environment for Mesmerize before launching it.

#. If you want Caiman features you'll need to install caiman into the same environment as mesmerize::

    git clone https://github.com/flatironinstitute/CaImAn
    cd CaImAn/
    git checkout v1.8.8
    source <new_venv_path/bin/activate>
    pip install -e .

#. You might need to setup Caiman using ``caimanmanager.py``. Please see their docs for details: https://caiman.readthedocs.io/en/master/Installation.html#installation-on-macos-and-linux

#. In order to use some features that launch subprocesses, such as the batch manager, you will need to check your :ref:`System Configuration settings in Mesmerize <SystemConfiguration>` to make sure that it activates the environment that mesmerize is installed in. By default the pre-run commands contain ``# source /<path_to_env>/activate'``, you will need to uncomment the line (remove the ``#``) and set the path to your environment.

.. note:: Caiman=>1.8.9 requires tensorflow v2, which is currently not supported by nuset. If you want to use the latest version of caiman, you will need to install tensorflow v2 and use python3.8

    
Mac OSX
=======

This requires Anaconda and will install Mesmerize in an Anaconda environment. If you want to install into a python virtual environment use the instructions for the Linux installation from step #3 onward. Tested on macOS Catalina 10.15.1

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

#. Install Mesmerize. On Mac installing tslearn before mesmerize creates problems on anaconda for some reason::

    pip install mesmerize
    
#. Install cython, and downgrade pandas::

    conda install Cython pandas~=0.25.3

#. Install tslearn~=0.4.1::

    conda install -c conda-forge tslearn=0.4.1
    
#. Install bottleneck (optional)::

    pip install bottleneck==1.2.1

#. To launch Mesmerize call it from the terminal::

    mesmerize
    
You will always need to activate the environment for Mesmerize before launching it.

**You might get a matplotlib error similar to below**::

    Bad val 'qt5' on line #1
    "backend: qt5
    
    in file "/Users/kushal/.matplotlib/matplotlibrc"
    Key backend: Unrecognized backend string 'qt5': valid strings are ['GTK3Agg', 'GTK3Cairo', 'MacOSX', 'nbAgg', 'Qt4Agg', 'Qt4Cairo', 'Qt5Agg', 'Qt5Cairo', 'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo', 'agg', 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']


**To fix this, execute the following which appends the default matplotlib backend-option. Note that this will probably affect matplotlib in all your environments**::

    echo "backend: qt5" >> ~/.matplotlib/matplotlibrc
    
You might need to setup Caiman using ``caimanmanager.py``. Please see their docs for details: https://caiman.readthedocs.io/en/master/Installation.html#installation-on-macos-and-linux

In order to use some features that launch subprocesses, such as the batch manager, you will need to check your :ref:`System Configuration settings in Mesmerize <SystemConfiguration>` to make sure that it activates the environment that mesmerize is installed in.

Windows
=======

Tested on Windows 10, not sure if it'll work on earlier Windows versions.

Download & install Anaconda for Python 3: https://www.anaconda.com/distribution/

**Make sure you select the option to add anaconda to the PATH environment variable during installation.**

You will also need git: https://gitforwindows.org/

.. warning:: It is **highly** recommended that you use Mesmerize in a new dedicated environment, even if you already have major dependencies (like caiman) installed in another environment.

**All commands are to be run in the powershell**

#. You will need anaconda to be accessible through powershell. You may need to run powershell as administrator for this step to to work. Close & open a new non-admin powershell after running this::

    conda init powershell

You will need a relatively recent version of Anaconda in order to run conda commands through the powershell.
    
#. Create a new anaconda environment::

    conda create -n mesmerize python=3.6

#. Activate the environment::

    conda activate mesmerize
    
#. Install caiman::

    conda install -c conda-forge caiman
    
#. Downgrade pandas, install Cython::

    conda install Cython pandas~=0.25.3
    
#. Install tslearn (optional)::

    conda install -c conda-forge tslearn=0.4.1
    
#. Install bottleneck (optional)::

    pip install bottleneck==1.2.1
    
#. Install graphviz::

    conda install graphviz

#. Install pywin32::

    pip install pywin32
    
#. Install Mesmerize::
    
    pip install mesmerize

#. Allow powershell to execute scripts. Run powershell as administrator to execute these commands. This is required for the batch manager and k-Shape GUI which launch external processes. This may affect the security of your system by allowing scripts to be executable. I'm not an expert on Windows so if someone knows a better way to do this let me know! As far as I know, I'm not sure why you would try to execute untrusted scripts so this shouldn't be a concern?::

    Set-ExecutionPolicy RemoteSigned
    Set-ExecutionPolicy Bypass -scope Process -Force
    
#. Launch Mesmerize::

    mesmerize

You might need to setup Caiman using ``caimanmanager.py``. Please see their docs for details: https://caiman.readthedocs.io/en/master/Installation.html#installation-on-macos-and-linux
    
.. note:: In order to use some features, such as the batch manager, you will need to check your :ref:`System Configuration settings in Mesmerize <SystemConfiguration>` to make sure that it activates the conda environment that mesmerize is installed in. By default the pre-run commands contain ``# conda activate mesmerize`` but you will need to uncomment the line (remove the ``#``) or change it if you are using an environment with a different name.

    
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
    
#. Install ``tensorflow`` or ``tensorflow-gpu``, you must use version ``~=1.15``::

    pip install tensorflow~=1.15

#. Install tslearn (required) & bottleneck (optional)::

    pip install tslearn~=0.4.1 bottleneck==1.2.1

    
#. If you want Caiman features you'll need to install caiman into the same environment as mesmerize::

    git clone https://github.com/flatironinstitute/CaImAn
    cd CaImAn/
    source <new_venv_path/bin/activate>
    pip install -e .

#. You might need to setup Caiman using ``caimanmanager.py``. Please see their docs for details: https://caiman.readthedocs.io/en/master/Installation.html#installation-on-macos-and-linux
    
#. Fork the main repo on github and clone it, or install from our repo::
    
    git clone https://github.com/kushalkolar/MESmerize.git
    # or your own form
    # git clone https://github.com/<your_github_username>/MESmerize.git
    cd MESmerize
    
#. Switch to new branch::

    git checkout -b my-new-feature

#. Install in editable mode::

    pip install -e .

#. Make your changes to the code & push to your fork::

    git push origin my-new-feature
    
#. Create a pull request if you want to incorporate it into the main Mesmerize repo.


