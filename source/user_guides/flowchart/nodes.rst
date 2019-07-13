Description of Flowchart Nodes
******************************


.. _nodes_Data:

Data
----
**These nodes are for performing general data related operations**


.. _node_LoadFile:

LoadFile
^^^^^^^^

	Loads a save Transmission file. If you have a Project open it will automatically set the project path according to the open project. Otherwise you must specify the project path. You can specify a different project path to the project that is currently open (this is untested, weird things could happen). You should not merge Transmissions originating from different projects.
	
	========== 	=================
	Terminal		Description
	========== 	=================
	Out 		Transmission loaded from the selected file.
	========== 	=================

	=========== 	===========
	Parameters		Description
	=========== 	===========
	load_trn		Button to choose a .trn file (Transmission) to load
	proj_path 		Button to select the Mesmerize project that corresponds to the chosen .trn file.
	=========== 	===========

	.. note::
		The purpose of specifying the Project Path when you load a save Transmission file is so that 	interactive plots and the :ref:`DatapointTracer` can find raw data that correspond to datapoints.


.. _node_Load_Proj_DF:

Load_Proj_DF
^^^^^^^^^^^^

	Load the entire Project DataFrame (root) of the project that is currently open, or a sub-DataFrame that corresponds a tab that you have created in the :ref:`ProjectBrowser`.

	========== 	=================
	Terminal		Description
	========== 	=================
	Out		Transmission created from the Project DataFrame or sub-DataFrame.
	========== 	=================

	=========== 	===========
	Parameters		Description
	=========== 	===========
	DF_Name		DataFrame name. List correponds to :ref:`ProjectBrowser` tabs.
	Update		Re-create Transmission from corresponding :ref:`ProjectBrowser` tab.
	Apply		:ref:`ApplyCheckBox`
	=========== 	===========

	.. note::
		The **DF_Name** options do not update live with the removal or creation of tabs in the :ref:`ProjectBrowser`, you must create a new node to reflect these types of changes.



.. _node_Save:

Save
^^^^

	Save the input Transmission to a file so that the Transmission can be used re-loaded in the Flowchart for later use.

	**Usage:** Connect an input Transmission to this node's **In** terminal, click the button to choose a path to save a new file to, and then click the Apply checkbox to save the input Transmission to the chosen file.

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Transmission to be saved to file
	========== 	=================

	=========== 	===========
	Parameters		Description
	=========== 	===========
	saveBtn		Button to choose a filepath to save the Transmission to.
	Apply		:ref:`ApplyCheckBox`
	=========== 	===========

	.. note::
		You must always save a Transmission to a new file (pandas with hdf5 exihibts weird behavior if you overwrite, this is the easiest workaround). If you try to overwrite the file you will be presented with an error saying that the file already exists.
	


.. _node_Merge:

Merge
^^^^^

	Merge multiple Transmissions into a single Transmission. The DataFrames of the individual Transmissions are concatenated using `pandas.concat <https://pandas.pydata.org/pandas-docs/version/0.24/user_guide/merging.html#concatenating-objects>`_ and History Traces are also merged. The History Trace of each indidual input Transmission is kept separately.

	.. warning::
		At the moment, if you create two separate data streams that originate from the same Transmission and then merge them at a later point, the History Trace of the individual data streams is not maintained.

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Transmissions to be merged
	Out		Merged Transmission
	========== 	=================



.. _node_ViewData:

ViewData
^^^^^^^^

	View the input Transmission object using the spyder Object Editor. For example you can explore the Transmission DataFrame and HistoryTrace.


.. _node_ViewHistoryTrace:

ViewHistoryTrace
^^^^^^^^^^^^^^^^

	View the HistoryTrace of the input Transmission in a nice Tree View GUI.


.. _node_TextFilter:

TextFilter
^^^^^^^^^^

	Include or Exclude Transmission DataFrame rows according to a text filter in a categorical column.

	**Usage Example:** If you want to select all traces that are from photoreceptor cells and you have a categorical column, named cell_types for example, containing cell type labels, choose "cell_type" as the *Column* parameter and enter "photoreceptor" as the *filter* parameter, and select *Include*. If you want to select everything that are not photoreceptors select *Exclude*.

	.. note::
		It is recommended to filter and group your data beforehand using the :ref:`ProjectBrowser` since it allows much more sophisticated filtering.
	
	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission its DataFrame filtered accoring parameters
	========== 	=================

	=========== 	===========
	Parameters		Description
	=========== 	===========
	Column		Categorical column that contains the text filter to apply
	filter		Text filter to apply
	Include		Include all rows matching the text filter
	Exclude		Exclude all rows matching the text filter
	Apply		:ref:`ApplyCheckBox`
	=========== 	===========


.. _node_SpliceArrays:

SpliceArrays
^^^^^^^^^^^^

	Splice arrays derived in the specified numerical data column and place the spliced output arrays in the output column.

	**Output Data Column** *(numerical)*: _SPLICE_ARRAYS	

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with arrays from the input column spliced and placed in the output column
	========== 	=================

	=========== 	===========
	Parameters		Description
	=========== 	===========
	data_column	Numerical data column containing the arrays to be spliced
	indices		The splice indices, "start_index:end_index"
	Apply		:ref:`ApplyCheckBox`
	=========== 	===========


.. _node_DropNaNs:

DropNaNs
^^^^^^^^

	Drop NaNs and Nones (null) from the Transmission DataFrame. Uses `DataFrame.dropna <https://pandas.pydata.org/pandas-docs/version/0.24/reference/api/pandas.DataFrame.dropna.html>`_ and `DataFrame.isna <https://pandas.pydata.org/pandas-docs/version/0.24/reference/api/pandas.DataFrame.isna.html>`_ methods.
	
	- If you choose "row" or "column" as axis, entire rows or columns will be dropped if any or all (see params) of the values are NaN/None.	

	- If you choose to drop NaNs/Nones according to a specific column, it will drop the entire row if that row has a NaN/None value for the chosen column.

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission NaNs and None's removed according to the params
	========== 	=================

	=========== 	===========
	Parameters		Description
	=========== 	===========
	axis		Choose to rows, columns, or a rows according to a specific column.

	how		*any:* Drop if any value in the row/column is NaN/None

			| *all:* Drop only if all values in the row/column are Nan/None

			| ignored if "axis" parameter is set to a specific column

	Apply		:ref:`ApplyCheckBox`
	=========== 	===========
		

.. _nodes_Display:

Display
-------
**These nodes connect input Transmission(s) to various plots for visualization**


.. _node_BeeswarmPlots:

BeeswarmPlots
^^^^^^^^^^^^^

	Based on pqytgraph Beeswarm plots.

	Visualize data points as a pseudoscatter and as corresponding Violin Plots. This is commonly used to visualize peak features and compare different experimental groups.

	For more information please see :ref:`plot_BeeswarmPlots`
	
	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission

			| The DataFrame column(s) of interest must have single numerical values, not arrays
	========== 	=================



.. _node_Heatmap:

Heatmap
^^^^^^^

	Used for visualizing numerical arrays in the form of a heatmap. Also used for visualizing a hieararchical clustering tree (dendrogram) along with a heatmap with row order corresponding to the order leaves of the dendrogram.

	For more information see :ref:`plot_Heatmap`

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission

			| The arrays in the DataFrame column(s) of interest **must** be of the same length
	========== 	=================
	
	.. note::
		Arrays in the DataFrame column(s) of interest **must** be of the same length. If they are not, you must splice them using the :ref:`node_SpliceArrays` node.


.. _node_Plot:

Plot
^^^^

	A simple plot.

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	========== 	=================

	=========== 	===========
	Parameters		Description
	=========== 	===========
	data_column	Data column to plot, must contain numerical arrays
	Show		Show/hide the plot window
	Apply		:ref:`ApplyCheckBox`
	=========== 	===========



.. _node_Proportions:

Proportions
^^^^^^^^^^^

	Plot stacked bar chart of one categorical variable vs. another categorical variable.
	
	For more information see :ref:`plot_Proportions`

.. _node_ScatterPlot:

ScatterPlot
^^^^^^^^^^^

	Create scatter plot of a numerical data column containing [X, Y] values (arrays of size 2).
	
	For more information see :ref:`plot_ScatterPlot`



.. _node_TimeSeries:

TimeSeries
^^^^^^^^^^

	Plot the means along with confidence intervals or standard eviation of numerical arrays representing time series data.

	For more information see :ref:`plot_TimeSeries`


--------

.. _nodes_Signal:

Signal
------

**Routine signal processing functions**

I recommend this book by Professor Tom O'Haver if you are unfamiliar with basic signal processing: https://terpconnect.umd.edu/~toh/spectrum/TOC.html


.. _node_ButterWorth:

Butterworth
^^^^^^^^^^^

	Creates a Butterworth filter using `scipy.signal.butter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html?highlight=signal%20butter>`_ and applies it using `scipy.signal.filtfilt <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html>`_. 

	The Wn parameter of `scipy.signal.butter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html?highlight=signal%20butter>`_ is calculated by dividing the sampling rate of the data by the *freq_divisor* parameter (see below).

	**Output Data Column** *(numerical)*: _BUTTERWORTH

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with filtered signals in the output data column
	========== 	=================

	============ 	===========
	Parameters		Description
	============	===========
	data_column	Data column containing numerical arrays
	order		Order of the filter
	freq_divisor	Divisor for dividing the sampling frequency of the data to get Wn
	Apply		:ref:`ApplyCheckBox`
	============ 	===========


.. _node_SavitzkyGolay:

SavitzkyGolay
^^^^^^^^^^^^^

	Savitzky Golay filter. Uses `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_.

	**Output Data Column** *(numerical)*: _SAVITZKY_GOLAY

.. _node_PowSpecDens:

PowSpecDens
^^^^^^^^^^^


.. _node_Resample:

Resample
^^^^^^^^


.. _node_ScalerMeanVar:

ScalerMeanVar
^^^^^^^^^^^^^


.. _node_Normalize:

Normalize
^^^^^^^^^


.. _node_RFFT:

RFFT
^^^^


.. _node_iRFFT:

iRFFT
^^^^^


.. _node_PeakDetect:

PeakDetect
^^^^^^^^^^


.. _node_PeakFeatures:

PeakFeatures
^^^^^^^^^^^^


--------


.. _nodes_Hierarchical:

Hierarchical
------------

These nodes allow you to perform Hierarchical Clustering using `scipy.cluster.hierarchy <https://docs.scipy.org/doc/scipy-1.2.1/reference/cluster.hierarchy.html>`_.

If you are unfamiliar with Hierarchical Clustering I recommend going through this chapter from Michael Greenacre: http://www.econ.upf.edu/~michael/stanford/maeb7.pdf

.. note::
	**Some of these nodes do not use Transmission objects for some inputs/outputs.**


.. _node_Linkage:

Linkage
^^^^^^^

	Compute a linkage matrix which can be used to form flat clusters using the :ref:`node_FCluster` node.

	Based on `scipy.cluster.hierarchy.linkage <https://docs.scipy.org/doc/scipy-1.2.1/reference/generated/scipy.cluster.hierarchy.linkage.html>`_

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Linkage matrix, **not a Transmission object**
	========== 	=================

	============= 	=================
	Parameters		Description
	=============	=================
	data_column	Numerical data column used for computing linkage matrix
	method		linkage method
	metric		metric for computing distance matrix

	optimal_order	minimize distance between successive leaves, more intuitive visualization

			| `Click here for more info <https://docs.scipy.org/doc/scipy-1.2.1/reference/generated/scipy.cluster.hierarchy.linkage.html?highlight=optimal_ordering>`_

	Apply		:ref:`ApplyCheckBox`
	============= 	=================
	





.. _node_FCluster:

FCluster
^^^^^^^^
	
	"Form flat clusters from the hierarchical clustering defined by the given linkage matrix."

	Based on `scipy.cluster.hierarchy.fcluster <https://docs.scipy.org/doc/scipy-1.2.1/reference/generated/scipy.cluster.hierarchy.fcluster.html>`_

	**Output Data Column** *(categorial)*: FCLUSTER_LABELS

	====================            =================
	Terminal                        Description
	====================            =================
	Linkage                         Linkage matrix, output from :ref:`node_Linkage` node.
	Data                            Input Transmission, usually the same input Transmission for the :ref:`node_Linkage`
	IncM *(optional)*	           Inconsistency matrix, output from :ref:`node_Inconsistent`
	Monocrit *(optinal)*	           Output from :ref:`node_MaxIncStat` or :ref:`node_MaxInconsistent`
	Out                             Transmission with clustering data that can be visualized using the :ref:`node_Heatmap`
	====================            =================


.. _node_Inconsistent:

Inconsistent
^^^^^^^^^^^^


.. _node_MaxIncStat:

MaxIncStat
^^^^^^^^^^


.. _node_MaxInconsisten:

MaxInconsistent
^^^^^^^^^^^^^^^
