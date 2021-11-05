<p align="center">
<img src="./newbanner.png" alt="Mesmerize Banner">
</p>

<p align="center">
    <em>State Of The Art Software for Calcium Imaging Analysis</em>
</p>

<p align="center">
  
<a href="https://pypi.org/project/mesmerize" target="_blank">
    <img src="https://badge.fury.io/py/mesmerize.svg" alt="Package version">
</a>

<a href="https://codeclimate.com/github/kushalkolar/MESmerize/maintainability" target="_blank">
    <img src="https://api.codeclimate.com/v1/badges/950e956456b688c0886e/maintainability" alt="Coverage">
</a>

<a href="https://www.gnu.org/licenses/gpl-3.0" target="_blank">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License">
</a>

<a href="https://gitter.im/mesmerize_discussion" target="_blank">
    <img src="https://badges.gitter.im/mesmerize_discussion/community.svg" alt="Chat and Help">
</a>
  
</p>

Mesmerize is a platform for the annotation and analysis of neuronal calcium imaging data. Mesmerize encompasses the entire process of calcium imaging analysis from raw data to interactive visualizations. Mesmerize allows you to create FAIR-functionally linked datasets that are easy to share. The analysis tools are applicable for a broad range of biological experiments and come with GUI interfaces that can be used without requiring a programming background.

---

**BioRxiv paper:** <a href="https://doi.org/10.1101/840488">https://doi.org/10.1101/840488</a>

**Documentation:** <a href="http://docs.mesmerizelab.org">http://docs.mesmerizelab.org</a>

**Video Tutorials:** <a href="https://www.youtube.com/watch?v=D9zKhFkcKTk&list=PLgofWiw2s4REPxH8bx8wZo_6ca435OKqg" target="_blank">Open YouTube</a>

**Additional Videos:** <a href="https://www.youtube.com/playlist?list=PLgofWiw2s4RF_RkGRUfflcj5k5KUTG3o_" target="_blank">Open YouTube</a>

---

# Installation

You can install **mesmerize** in any virtual environment using **pip**. 

```bash
pip install mesmerize
```

If you would like to have a **mesmerize** with all of its features installed, the easiest solution is to use the following **conda** environment.yml.

```yml
name: mesmerize

# From the conda ecosystem
dependencies:
  - python=3.8
  - pip
  - cython==0.29.*
  - numpy>=1.0.0,<2.0.0
  - tensorflow==2.6
  # From the PyPI ecosystem
  - pip:
    - tslearn==0.5.2
    - git+https://github.com/flatironinstitute/CaImAn.git@v1.9.4
    - git+https://github.com/Blastorios/MESmerize.git
```

We also provide a **virtual machine** with **mesmerize** and all of its features pre-installed:
http://docs.mesmerizelab.org/en/master/user_guides/installation.html#all-platforms

We do not provide a Docker Image due to the graphical nature of mesmerize. If you have a secure, non-sudo, Image by which you run mesmerize: feel free to share it with us at any time!

### Caiman
In order to use [CaImAn](https://github.com/flatironinstitute/CaImAn) features you will need to have [CaImAn](https://github.com/flatironinstitute/CaImAn) installed into your environment. See the Mesmerize documentation for more details.

Caiman is used for the following Viewer modules: `CNMF`, `3D CNMF`, `CNMFE`, `caiman motion correction` and `Detrend DFOF`.

### tslearn
In order to use tslearn features you will need `tslearn`. This can be installed via pip or conda, see the detailed installation instructions for more details: http://docs.mesmerizelab.org/en/master/user_guides/installation.html

tslearn is used for `KShape clustering`, `cross-correlation analysis`, and some flowchart nodes.

### tensorflow
In order to use nuset segmentation you will need `tensorflow`.

```
pip install tensorflow~=1.15
```

---

# Questions/Discussions

Feel free to ask questions or discuss things on <a href="https://gitter.im/mesmerize_discussion">gitter</a>. For larger bugs/issues please use the issue tracker.

**Issue tracker:** https://github.com/kushalkolar/MESmerize/issues

---

# News

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

---

# Upcoming

- Experimental use of the bioformats importer for the Viewer.
- Export lite versions of projects for easier sharing.
- Browsers based visualizations for sharing analysis results.

---

# Acknowledgements

- [pyqtgraph](https://github.com/pyqtgraph/pyqtgraph) developers for creating such an expansive library, which we built upon to create many of the interactive elements of Mesmerize. 
- [CaImAn](https://github.com/flatironinstitute/CaImAn) developers have created a very robust library for pre-processing and signal extraction of calcium imaging data, which Mesmerize is able to interface with.
- Simon Daste provided sample data and assistance which allowed for creation of the Suite2p importer module.
- [Jordi Zwiggelaar](https://github.com/Blastorios) created the Mesmerize logo & banner.
