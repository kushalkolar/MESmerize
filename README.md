[![Maintainability](https://api.codeclimate.com/v1/badges/950e956456b688c0886e/maintainability)](https://codeclimate.com/github/kushalkolar/MESmerize/maintainability) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![Gitter](https://badges.gitter.im/mesmerize_discussion/community.svg)](https://gitter.im/mesmerize_discussion/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/mesmerize) &nbsp;&nbsp;
<a href="https://doi.org/10.1101/840488">
<img src="https://www.biorxiv.org/sites/default/files/site_logo/bioRxiv_logo_homepage.png" alt="manuscript on biorxiv" width="160"/>
</a>

# Mesmerize

Mesmerize is a platform for the annotation and analysis of neuronal calcium imaging data. It encompasses the entire process of calcium imaging analysis from raw data to semi-final publication figures that are interactive, and aids in the creation of FAIR-functionally linked datasets. It is applicable for a broad range of experiments and is intended to be used by users with and without a programming background.

## News & upcoming

**July 2020**

Changes:
- Mesmerize can be installed via pip.
- Much easier to import imaging meta data from other sources.
- Create stimulus tuning curve plots.
- ΔF/F can now be extracted at the Viewer stage for caiman data, or set through other methods. Spikes and ΔF/F can be visualized in the Viewer.

**June 2020**

Version 0.2 released.

Changes:

- Windows is now supported!
- The Viewer can handle 3D data and 3D ROIs.
- For development, classes are provided for creating Volumetic ROI types, and a Volumetic ROI manager.
- Caiman 3D CNMF is supported.
- Updated CNMF(E) and motion correction modules to use the latest release of CaImAn. Parameter entry GUIs are much more flexible now.
- CNMF(E) data can be imported directly from hdf5 files from Caiman. Therefore you can use your own scripts/notebooks and existing CNMF hdf5 files for downstream analysis in Mesmerize.
- More customizable support for use of caiman modules within the Mesmerize viewer's script editor.
- Suite2p importer added, allowing you to perform downstream analysis of Suite2p output data in Mesmerize.
- Some cleanup with the batch manager
- bug fixes

*Please note that batches from v0.1 and v0.2 are not inter-compatible. Use the v0.1 branch if you need v0.1*

**Nov 2019:**

See our recent biorxiv manuscript where we use Mesmerize to analyze a calcium imaging dataset from *Ciona intestinalis* as well as other model organisms!

https://doi.org/10.1101/840488

## Questions/Discussions

Feel free to ask questions or discuss things on gitter. For larger bugs/issues please use the issue tracker.

[![Gitter](https://badges.gitter.im/mesmerize_discussion/community.svg)](https://gitter.im/mesmerize_discussion/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)


## Documentation
Documentation is available here: [http://www.mesmerizelab.org/](http://www.mesmerizelab.org/)

## Installation

**The easiest way to get Mesmerize is to install the snap (Linux only). You can also install directly from the repo on Windows, Linux & Mac OSX.**

See the docs for installation instructions in all operating systems:

http://mesmerizelab.org/user_guides/installation.html

### Snap
[https://snapcraft.io/mesmerize](https://snapcraft.io/mesmerize)

**Note: The snap comes with a version of Caiman from ~late 2018. We're currently working on getting the snap up to date with the latest release.**

**v0.2 will soon be available on snap**

After installation simply run `mesmerize` in the terminal and the application will launch in ~10-30 seconds.

Command line snap installation:
```bash
sudo snap install mesmerize.
```
Make sure you have `snapd` installed, which is required for running snap apps.
If you are on Ubuntu 16.04 or later snapd should be pre-installed.

You should be able to install `snapd` through apt for most Debian based distros
```bash
sudo apt update
sudo apt install snapd
```

Installing `snapd` on Fedora
```bash
sudo dnf install snapd
```

To install `snapd` on other distros please see: [https://docs.snapcraft.io/installing-snapd](https://docs.snapcraft.io/installing-snapd).

The snap has been tested to work on Ubuntu 18.04, Debian 9 (Stretch) and Fedora 29.
