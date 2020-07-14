![banner](./banner.png)

| <span> | <span> | <span> | <span> |
|--------|--------|--------|--------|
| PyPI | [![PyPI version](https://badge.fury.io/py/mesmerize.svg)](https://badge.fury.io/py/mesmerize) | Downloads | [![Downloads](https://pepy.tech/badge/mesmerize)](https://pepy.tech/project/mesmerize) |
| License | [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) | Maintenance | ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/kushalkolar/MESmerize) |
| Documentation | [![Documentation Status](https://readthedocs.org/projects/mesmerize/badge/?version=master)](https://mesmerize.readthedocs.io/en/master/?badge=master) | Code analysis | [![Maintainability](https://api.codeclimate.com/v1/badges/950e956456b688c0886e/maintainability)](https://codeclimate.com/github/kushalkolar/MESmerize/maintainability) |
| Chat & Help | [![Gitter](https://badges.gitter.im/mesmerize_discussion/community.svg)](https://gitter.im/mesmerize_discussion/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge) | Issue tracker | ![GitHub issues](https://img.shields.io/github/issues/kushalkolar/MESmerize) |

Mesmerize is a platform for the annotation and analysis of neuronal calcium imaging data. Mesmerize encompasses the entire process of calcium imaging analysis from raw data to interactive visualizations. Mesmerize allows you to create FAIR-functionally linked datasets that are easy to share. The analysis tools are applicable for a broad range of biological experiments and come with GUI interfaces that can be used without requiring a programming background.

Associated bioRxiv paper: https://doi.org/10.1101/840488

<a href="https://doi.org/10.1101/840488">
<img src="https://www.biorxiv.org/sites/default/files/site_logo/bioRxiv_logo_homepage.png" alt="manuscript on biorxiv" width="160"/>
</a>

## Installation

If you're familiar with anaconda or virtual environments, installation is as simple as:

```
pip install mesmerize
```

After installation simply call ``mesmerize`` from inside the virtual environment to launch it.

If you're unfamiliar with virtual environments, see the docs for more detailed instructions on all operating systems:
http://mesmerizelab.org/user_guides/installation.html

#### Caiman
In order to use [CaImAn](https://github.com/flatironinstitute/CaImAn) features you will need to have [CaImAn](https://github.com/flatironinstitute/CaImAn) installed into your environment. See the Mesmerize installation instructions linked above for more details: https://mesmerize.readthedocs.io/en/master/user_guides/installation.html

Caiman is used for the following Viewer modules: CNMF, 3D CNMF, CNMFE, caiman motion correction and Detrend DFOF.

#### tslearn
In order to use tslearn features you will need ``tslearn~=0.2.2``. This can be installed via pip or conda, see the detailed installation instructions for more details: https://mesmerize.readthedocs.io/en/master/user_guides/installation.html

tslearn is used for KShape clustering, cross-correlation analysis, and some of the flowchart nodes

## Documentation
Documentation is available here: [http://www.mesmerizelab.org/](http://www.mesmerizelab.org/)

## Questions/Discussions

Feel free to ask questions or discuss things on gitter. For larger bugs/issues please use the issue tracker.

[![Gitter](https://badges.gitter.im/mesmerize_discussion/community.svg)](https://gitter.im/mesmerize_discussion/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

**Issue tracker:** https://github.com/kushalkolar/MESmerize/issues

## News

See the [changelog](https://github.com/kushalkolar/MESmerize/blob/master/CHANGELOG.md) for more details

**July 2020**

Changes:
- Mesmerize can now be installed via pip.
- Much easier to import imaging meta data from other sources.
- Create stimulus tuning curve plots.
- ΔF/F must now be extracted at the Viewer stage for caiman data, or set through other methods. Spikes and ΔF/F can be visualized in the Viewer.

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

<a href="https://doi.org/10.1101/840488">
<img src="https://www.biorxiv.org/sites/default/files/site_logo/bioRxiv_logo_homepage.png" alt="manuscript on biorxiv" width="160"/>
</a>

## Upcoming

**Towards v0.3**
- Full support for recordings from Femtonics microscopes.
- Export lite versions of projects for easier sharing.
- Cross correlation analysis with stimulus maps.

## Acknowledgements

- [pyqtgraph](https://github.com/pyqtgraph/pyqtgraph) developers for creating such an expansive library, which we built upon to create many of the interactive elements of Mesmerize. 
- [CaImAn](https://github.com/flatironinstitute/CaImAn) developers have created a very robust library for pre-processing and signal extraction of calcium imaging data, which Mesmerize is able to interface with.
- Simon Daste provided sample data and assistance which allowed for creation of the Suite2p importer module.
- [Jordi Zwiggelaar](https://github.com/Blastorios) created the Mesmerize logo & banner.
