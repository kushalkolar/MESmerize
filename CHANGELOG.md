# 0.5.0 (planned)

### New
- Experimental use of the bioformats importer for the Viewer.
- Export lite versions of projects for easier sharing.

# 0.4.0

### New
- Bokeh based plots that use a bokeh-based datapoint tracer, still in very early stages
- k-Shape "gridsearch", select a n-partitions range and number of combinations, returns heatmap of all k-Shape runs with inertia values
    NOTE: The gridsearch is not saved when the plot is saved. Only the chosen kshape iteration will be saved. This will be fixed in a future release
- Plot neural dynamics in PCA or LDA space
- PadArrays flowchart node to pad dataframe arrays when sizes don't match, useful when splicing is undesired
- View mean, max, or std projection of caiman motion correction outputs by selecting them from the batch manager

### Modified
- CNME Viewer module uses ``CNMFParams`` when running batch items instead of passing the params are args directly to ``CNMF.__init__()``
- Improved performance when importing a project dataframe in the flowchart
- The project ``curves`` dir is deprecated. Backwards compatibility is maintained
- Project browser supports filtering of list-type columns, such as stimulus/behavioral names
- Use tslearn v0.4
- Lots of bug fixes everywhere
- Fix finding (newer?) CUDA GPUs
- Fix bug with stimtuning plot if only one stim type is present

# 0.3.1

### Modified

- Spacemap plot supports 3D data
- Unlabelled stimulus periods can be excluded for Stimulus Tuning plots

# 0.3.0

### New
- Cross correlation plots with stimulus maps.
- Support for Femtonics .mes and .mesc recordings.
- Segmentation using deep learning via NuSeT.
- Caiman NoRMCorr motion correction can be used for 3D data, just treats each plane as an individual 2D recording
- Caiman 2D CNMF can be used on 3D data, useful if you can assume each cell appears in only 1 plane

### Fixed
- ROI removal is much faster when clearing the work environment
- Bug fix with saving Stimulus Tuning plots
- Unnoticable bug with viewer modules that don't have defined dock areas

# 0.2.3

### Fixed
- Batch Manager view input bug with multiple viewers.
- Transmission.from_proj() bug spiking data are None.

### Modified
- Transmissions spawned from Load_Proj_DF node no longer have the ``last_output`` attribute set to ``"_RAW_CURVE"``. This allows the ``"_DFOF"`` and ``"_SPIKES"`` data to be used immediately with certain nodes.
- Units combobox for stimulus mapping module is disabled.
- Doc links in Help menus now point to the online docs for the current Mesmerize version instead of having built-in docs.

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
