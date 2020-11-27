![banner](./banner.png)

| <span> | <span> | <span> | <span> |
|--------|--------|--------|--------|
| PyPI | [![PyPI version](https://badge.fury.io/py/mesmerize.svg)](https://badge.fury.io/py/mesmerize) | Downloads | [![Downloads](https://pepy.tech/badge/mesmerize)](https://pepy.tech/project/mesmerize) |
| License | [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) | Maintenance | [![GitHub commit activity](https://img.shields.io/github/commit-activity/m/kushalkolar/MESmerize)](https://github.com/kushalkolar/MESmerize/commits/master) |
| Documentation | [![Documentation Status](https://readthedocs.org/projects/mesmerize/badge/?version=master)](http://docs.mesmerizelab.org/en/master/?badge=master) | Code analysis | [![Maintainability](https://api.codeclimate.com/v1/badges/950e956456b688c0886e/maintainability)](https://codeclimate.com/github/kushalkolar/MESmerize/maintainability) |
| Chat & Help | [![Gitter](https://badges.gitter.im/mesmerize_discussion/community.svg)](https://gitter.im/mesmerize_discussion/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge) | Issue tracker | [![GitHub issues](https://img.shields.io/github/issues/kushalkolar/MESmerize)](https://github.com/kushalkolar/MESmerize/issues) |

Mesmerize is a platform for the annotation and analysis of neuronal calcium imaging data. Mesmerize encompasses the entire process of calcium imaging analysis from raw data to interactive visualizations. Mesmerize allows you to create FAIR-functionally linked datasets that are easy to share. The analysis tools are applicable for a broad range of biological experiments and come with GUI interfaces that can be used without requiring a programming background.

Associated bioRxiv paper: https://doi.org/10.1101/840488

<a href="https://doi.org/10.1101/840488">
<img src="https://www.biorxiv.org/sites/default/files/site_logo/bioRxiv_logo_homepage.png" alt="manuscript on biorxiv" width="160"/>
</a>

## Video Tutorials!
We have recently created detailed video tutorials! The main tutorial series provides a quick overview that takes you from raw imaging data, to downstream analysis and interactive visualizations:\
https://www.youtube.com/playlist?list=PLgofWiw2s4REPxH8bx8wZo_6ca435OKqg

Additional videos on specific aspects of Mesmerize will be posted here:\
[https://www.youtube.com/playlist?list=PLgofWiw2s4RF_RkGRUfflcj5k5KUTG3o_](https://www.youtube.com/playlist?list=PLgofWiw2s4RF_RkGRUfflcj5k5KUTG3o_)

More tutorial videos will be available soon.

## Installation

If you're familiar with anaconda or virtual environments, installation is as simple as:

```
pip install mesmerize
```

After installation just call ``mesmerize`` from inside the virtual environment to launch it.

If you're unfamiliar with virtual environments, see the docs for more detailed instructions on all operating systems:
http://docs.mesmerizelab.org/en/master/user_guides/installation.html

#### Caiman
In order to use [CaImAn](https://github.com/flatironinstitute/CaImAn) features you will need to have [CaImAn](https://github.com/flatironinstitute/CaImAn) installed into your environment. See the Mesmerize installation instructions linked above for more details: http://docs.mesmerizelab.org/en/master/user_guides/installation.html

Caiman is used for the following Viewer modules: CNMF, 3D CNMF, CNMFE, caiman motion correction and Detrend DFOF.

#### tslearn
In order to use tslearn features you will need ``tslearn~=0.2.2``. This can be installed via pip or conda, see the detailed installation instructions for more details: http://docs.mesmerizelab.org/en/master/user_guides/installation.html

tslearn is used for KShape clustering, cross-correlation analysis, and some of the flowchart nodes.

#### tensorflow
In order to use nuset segmentation you will need ``tensorflow v1.15``. You can use either ``tensorflow`` (CPU bound) or ``tensorflow-gpu``

```
pip install --upgrade pip setuptools
pip install tensorflow~=1.15
```

## Documentation
Documentation is available here: [http://docs.mesmerizelab.org/](http://docs.mesmerizelab.org/)

## Questions/Discussions

Feel free to ask questions or discuss things on gitter. For larger bugs/issues please use the issue tracker.

[![Gitter](https://badges.gitter.im/mesmerize_discussion/community.svg)](https://gitter.im/mesmerize_discussion/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

**Issue tracker:** https://github.com/kushalkolar/MESmerize/issues

## News

See the [changelog](https://github.com/kushalkolar/MESmerize/blob/master/CHANGELOG.md) for more details

**November 2020**

Changes:

- Bokeh based plots that use a bokeh-based datapoint tracer, still in very early stages
- k-Shape "gridsearch", select a n-partitions range and number of combinations, returns heatmap of all k-Shape runs with inertia values NOTE: The gridsearch is not saved when the plot is saved. Only the chosen kshape iteration will be saved. This will be fixed in a future release
- Plot neural dynamics in PCA or LDA space
- PadArrays flowchart node to pad dataframe arrays when sizes don't match, useful when splicing is undesired
- View mean, max, or std projection of caiman motion correction outputs by selecting them from the batch manager

**September 2020**

Version 0.3 released

Changes:

- Cross correlation plots with stimulus maps.
- Support for Femtonics .mes and .mesc recordings.
- Segmentation using deep learning via NuSeT.

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

- Experimental use of the bioformats importer for the Viewer.
- Export lite versions of projects for easier sharing.
- Browsers based visualizations for sharing analysis results.

## Acknowledgements

- [pyqtgraph](https://github.com/pyqtgraph/pyqtgraph) developers for creating such an expansive library, which we built upon to create many of the interactive elements of Mesmerize. 
- [CaImAn](https://github.com/flatironinstitute/CaImAn) developers have created a very robust library for pre-processing and signal extraction of calcium imaging data, which Mesmerize is able to interface with.
- Simon Daste provided sample data and assistance which allowed for creation of the Suite2p importer module.
- [Jordi Zwiggelaar](https://github.com/Blastorios) created the Mesmerize logo & banner.
