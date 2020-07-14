# 0.2.2

### Fixed
- Heatmap plot widget properly handles live updates from input data
- Saving of Stimulus tuning curve plots
- Stimulus plots is faster since linear regions aren't redrawn for the same stimulus type.
- Curve plot now shows up when the sample is opened via the datapoint tracer.

### Modified
- Tuning curve plot widget returns stimulus xlabels and yvals to separate dataframe columns instead of being together in one column as a list.
- tslearn and bottleneck are optional dependencies.

# 0.2.1

### Fixed
- Changed default python call in system config for Windows to be ``python`` instead of ``python3``.

# 0.2.0

### New
- Mesmerize can now be installed via pip.
- Create stimulus tuning curve plots.
- ΔF/F must now be extracted at the Viewer stage for caiman data, or set through other methods. Spikes and ΔF/F can be visualized in the Viewer.
- Windows is now supported!
- The Viewer can handle 3D data and 3D ROIs.
- For development, classes are provided for creating Volumetic ROI types, and a Volumetic ROI manager.
- Caiman 3D CNMF is supported.
- CNMF(E) data can be imported directly from hdf5 files from Caiman. Therefore you can use your own scripts/notebooks and existing CNMF hdf5 files for downstream analysis in Mesmerize.
- Suite2p importer added, allowing you to perform downstream analysis of Suite2p output data in Mesmerize.

### Modified
- Much easier to import imaging meta data from other sources, users can just add a function to ``mesmerize.viewer.core.organize_metadata``.
- Updated CNMF(E) and motion correction modules to use the latest release of CaImAn. Parameter entry GUIs are much more flexible now.
- More customizable support for use of caiman modules within the Mesmerize viewer's script editor.
- Some API cleanup with the batch manager
