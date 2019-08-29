.. _FlowchartNodes:

Nodes
*****

.. _nodes_Data:

Data
----
**These nodes are for performing general data related operations**


.. _node_LoadFile:

LoadFile
^^^^^^^^
    
    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Data.LoadFile>`
    
	Loads a save Transmission file. If you have a Project open it will automatically set the project path according to the open project. Otherwise you must specify the project path. You can specify a different project path to the project that is currently open (this is untested, weird things could happen). You should not merge Transmissions originating from different projects.
	
	.. note:: You can also load a saved Transmission file by dragging & dropping it into the Flowchart area. It will create a LoadFile node with the name of the dropped.
	
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


.. _nodeLoadProjDF:

LoadProjDF
^^^^^^^^^^
    
    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Data.LoadProjDF>`
    
	Load the entire Project DataFrame (root) of the project that is currently open, or a sub-DataFrame that corresponds a tab that you have created in the :ref:`ProjectBrowser`.

	**Output Data Column** *(numerical)*: _RAW_CURVE

		Each element in this output column contains a 1-D array representing the trace extracted from an ROI.

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
	Apply		Process data through this node
	=========== 	===========

	.. note::
		The **DF_Name** options do not update live with the removal or creation of tabs in the :ref:`ProjectBrowser`, you must create a new node to reflect these types of changes.



.. _node_Save:

Save
^^^^
    
    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Data.Save>`
    
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
	Apply		Process data through this node
	=========== 	===========

	.. note::
		You must always save a Transmission to a new file (pandas with hdf5 exihibts weird behavior if you overwrite, this is the easiest workaround). If you try to overwrite the file you will be presented with an error saying that the file already exists.
	


.. _node_Merge:

Merge
^^^^^
    
    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Data.Merge>`

	Merge multiple Transmissions into a single Transmission. The DataFrames of the individual Transmissions are concatenated using `pandas.concat <https://pandas.pydata.org/pandas-docs/version/0.24/user_guide/merging.html#concatenating-objects>`_ and History Traces are also merged. The History Trace of each indidual input Transmission is kept separately.

	.. warning::
		At the moment, if you create two separate data streams that originate from the same Transmission and then merge them at a later point, the analysis log (History Trace) of the individual data streams are not maintained. See the information about data blocks in the :ref:`concept_Transmission`.

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Transmissions to be merged
	Out		Merged Transmission
	========== 	=================



.. _node_ViewData:

ViewTransmission
^^^^^^^^^^^^^^^^
    
    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Data.ViewTransmission>`

	View the input Transmission object using the spyder Object Editor. For example you can explore the Transmission DataFrame and HistoryTrace.


.. _node_ViewHistoryTrace:

ViewHistory
^^^^^^^^^^^
    
    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Data.ViewHistory>`
    
	View the HistoryTrace of the input Transmission in a nice Tree View GUI.


.. _node_TextFilter:

TextFilter
^^^^^^^^^^
    
    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Data.TextFilter>`
    
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
	Apply		Process data through this node
	=========== 	===========
	
	**HistoryTrace output structure:** Dict of all the parameters for this node


.. _node_SpliceArrays:

SpliceArrays
^^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Data.SpliceArrays>`

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
	Apply		Process data through this node
	=========== 	===========


.. _node_DropNaNs:

DropNa
^^^^^^
    
    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Data.DropNa>`
    
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

	Apply		Process data through this node
	=========== 	===========
		


.. _node_NormRawMinMax:

NormRaw
^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Biology.NormRaw>`
    
    Scale the raw data such that the min and max values are set to the min and max values derived from the raw spatial regions of the image sequences they originate from. Only for CNMFE data.
    
    The arrays in the **_RAW_CURVE** column are scaled and the output is placed in a new column named **_NORMRAW**
    
    ==========  =================
    Terminal    Description
    ==========  =================
    In          Input Transmission
    Out         Transmission with the result placed in the output column
    ==========  =================

    ========== ================================
    Parameter  Description
    ========== ================================
    option      | Derive the raw min & max values from one of the following options:
                | *top_5:* Top 5 brightest pixels
                | *top_10:* Top 10 brighest pixels
                | *top_5p:* Top 5% of brightest pixels
                | *top_10p:* Top 10% of brightest pixels
                | *top_25p:* Top 25% of brightest pixels
                | *full_mean:* Full mean of the min and max array
    Apply      Process data through this node
    ========== ================================
    
    .. note:: If the raw min value is higher than the raw max value the curve will be excluded in the output. You will be presented with a warning box with the number of curves that were excluded due to this.

--------------------------

.. _nodes_Display:

Display
-------
**These nodes connect input Transmission(s) to various plots for visualization**

The actual Plot Widget instance that these nodes use can be accessed through the ``plot_widget`` attribute in the flowchart console.

For example

.. code-block:: python

    # Get a heatmap node that is named "Heatmap.0"
    >>> hn = get_nodes()['Heatmap.0']
    
    # the plot widget instance
    >>> hn.plot_widget
    
    <mesmerize.plotting.widgets.heatmap.widget.HeatmapTracerWidget object at 0x7f26e5d29678>

    
.. _node_BeeswarmPlots:

BeeswarmPlots
^^^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Display.BeeswarmPlots>`

	Based on pqytgraph Beeswarm plots.

	Visualize data points as a pseudoscatter and as corresponding Violin Plots. This is commonly used to visualize peak features and compare different experimental groups.

	For information on the plot widget see :ref:`Beeswarm Plots <plot_Beeswarm>`
	
	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission

			| The DataFrame column(s) of interest must have single numerical values, not arrays
	========== 	=================



.. _node_Heatmap:

Heatmap
^^^^^^^
    
    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Display.Heatmap>`
    
	Used for visualizing numerical arrays in the form of a heatmap. Also used for visualizing a hieararchical clustering tree (dendrogram) along with a heatmap with row order corresponding to the order leaves of the dendrogram.

	For information on the plot widget see :ref:`Heat Plot <plot_Heatmap>`

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission

			| The arrays in the DataFrame column(s) of interest **must** be of the same length
	========== 	=================
	
	.. note::
		Arrays in the DataFrame column(s) of interest **must** be of the same length. If they are not, you must splice them using the :ref:`node_SpliceArrays` node.

.. _node_CrossCorr:

CrossCorr
^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Display.CrossCorr>`

	Perform Cross-Correlation analysis. For information on the plot widget see :ref:`CrossCorrelation Plot <plot_CrossCorrelation>`
	

.. _node_Plot:

Plot
^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Display.Plot>`
    
    For information on the plot widget see :ref:`<plot_SimplePlot>`
    
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
	Apply		Process data through this node
	=========== 	===========



.. _node_Proportions:

Proportions
^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Display.Proportions>`

	Plot stacked bar chart of one categorical variable vs. another categorical variable.
	
	For information on the plot widget see :ref:`Proportions Plot <plot_Proportions>`

.. _node_ScatterPlot:

ScatterPlot
^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Display.ScatterPlot>`

	Create scatter plot of numerical data containing [X, Y] values
	
	For information on the plot widget see :ref:`Scatter Plot <plot_ScatterPlot>`

.. _node_TimeSeries:

TimeSeries
^^^^^^^^^^

	Plot the means along with confidence intervals or standard eviation of numerical arrays representing time series data.

	For more information see :ref:`plot_TimeSeries`


--------------------

.. _nodes_Signal:

Signal
------

**Routine signal processing functions**

I recommend this book by Tom O'Haver if you are unfamiliar with basic signal processing: https://terpconnect.umd.edu/~toh/spectrum/TOC.html


.. _node_ButterWorth:

Butterworth
^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Signal.Butterworth>`


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
	data_column	Data column containing numerical arrays to be filtered
	order		Order of the filter
	freq_divisor	Divisor for dividing the sampling frequency of the data to get Wn
	Apply		Process data through this node
	============ 	===========


.. _node_SavitzkyGolay:

SavitzkyGolay
^^^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Signal.SavitzkyGolay>`

	`Savitzky Golay filter <https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter>`_. Uses `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_.

	**Output Data Column** *(numerical)*: _SAVITZKY_GOLAY

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with filtered signals in the output data column
	========== 	=================

	============= 	===========
	Parameters		Description
	=============	===========
	data_column	Data column containing numerical arrays to be filtered
	window_length	Size of windows for fitting the polynomials. Must be an odd number.
	polyorder		Order of polynomials to fit into the windows. Must be less than *window_length*
	Apply		Process data through this node
	============= 	===========


.. _node_PowSpecDens:

PowSpecDens
^^^^^^^^^^^


.. _node_Resample:

Resample
^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Signal.Resample>`

	Resample the data in numerical arrays. Uses `scipy.signal.resample <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample.html>`_.

	**Output Data Column** *(numerical)*: _RESAMPLE

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with resampled signals in the output data column
	========== 	=================
	
	============= 	===========
	Parameters		Description
	=============	===========
	data_column	Data column containing numerical arrays to be resampled
	Rs		New sampling rate in *Tu* units of time.
	Tu		Time unit
	Apply		Process data through this node
	============= 	===========
	
	.. note::
		If Tu = 1, then Rs is the new sampling rate in Hertz.


.. _node_ScalerMeanVar:

ScalerMeanVariance
^^^^^^^^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Signal.ScalerMeanVariance>`

	Uses `tslearn.preprocessing.TimeSeriesScalerMeanVariance <https://tslearn.readthedocs.io/en/latest/gen_modules/preprocessing/tslearn.preprocessing.TimeSeriesScalerMeanVariance.html>`_
	
	**Output Data Column** *(numerical)*: _SCALER_MEAN_VARIANCE

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with scaled signals in the output column
	========== 	=================

	============= 	===========
	Parameters		Description
	=============	===========
	data_column	Data column containing numerical arrays to be scaled
	mu		Mean of the output time series
	std		Standard Deviation of the output time series
	Apply		Process data through this node
	============= 	===========


	.. note::
		if mu = 0 and std = 1, the output is the z-score of the signal.

.. _node_Normalize:

Normalize
^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Signal.Normalize>`

	Normalize the signal so that all values are between 0 and 1 based on the min and max of the signal.

	**Output Data Column** *(numerical)*: _NORMALIZE

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with scaled signals in the output column
	========== 	=================

	============= 	===========
	Parameters		Description
	=============	===========
	data_column	Data column containing numerical arrays to be scaled
	Apply		Process data through this node
	============= 	===========

.. _node_RFFT:

RFFT
^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Signal.RFFT>`

	Uses `scipy.fftpack.rfft <https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.rfft.html>`_. "Discrete Fourier transform of a real sequence"

	**Output Data Column** *(numerical)*: _RFFT

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with the RFT of signals in the output column
	========== 	=================

	============= 	===========
	Parameters		Description
	=============	===========
	data_column	Data column containing numerical arrays
	Apply		Process data through this node
	============= 	===========


.. _node_iRFFT:

iRFFT
^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Signal.iRFFT>`
    
	Uses `scipy.fftpack.irfft <https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.irfft.html>`_. "inverse discrete Fourier transform of real sequence x"

	**Output Data Column** *(numerical)*: _IRFFT


.. _node_PeakDetect:

PeakDetect
^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Signal.PeakDetect>`

	Simple Peak Detection using derivatives. The "Differentiation" chapter of Tom O'Haver's book has a section on Peak Detection which I recommend reading. https://terpconnect.umd.edu/~toh/spectrum/TOC.html

	**Output Data Column** *(DataFrame)*: peaks_bases
	
	.. seealso:: :ref:`Peak Editor GUI <plot_PeakEditor>`

	===================== 	=================
	Terminal   		Description
	===================== 	=================
	Derivative 		Transmission with derivatives of signals. Must have **_DERIVATIVE** column.

				| It's recommended to use a derivative from a normalized filtered signal.

	Normalized 		Transmission containing Normalized signals, used for thresholding

				| See :ref:`node_Normalize` node

	Curve      		Transmission containing original signals.

				| Usually not filtered to avoid distortions caused by filtering

	PB_Input *(optional)*		Transmission containing peaks & bases data (peaks_bases column).

					| Useful for visualizing a saved Transmission that has peaks & bases data
	Out			Transmission with the detected peaks & bases as DataFrames in the output column
	===================== 	=================
	
	.. warning:: The *PB_Input* terminal overrides all other terminals. Do not connect inputs to *PB_Input* and other terminals simultaneously.


	===================== 	=================
	Parameter   		Description
	===================== 	=================
	data_column		Data column of the input *Curve* Transmission for placing peaks & bases onto
	Fictional_Bases		Add bases to beginning and end of signal if first or last peak is lonely
	Edit			Open Peak Editor GUI, see :ref:`plot_PeakEditor`
	SlopeThr			Slope threshold
	AmplThrAbs			Absolute amplitude threshold
	AmplThrRel			Relative amplitude threshold
	Apply			Process data through this node
	===================== 	=================


.. _node_PeakFeatures:

PeakFeatures
^^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Signal.PeakFeatures>`

	Compute peak features. The DataFrame of the ouput Transmission contains one row for each peak.
	
    =========================       ===========================================
    Output Data Column              Description
    =========================       ===========================================
    _pf_peak_curve                  array representing the peak
    _pf_ampl_rel_b_ix_l             peak amplitude relative to its left base
    _pf_ampl_rel_b_ix_r             peak amplitude relative to its right base
    _pf_ampl_rel_b_mean             peak amplitude relative to the mean of its bases
    _pf_ampl_rel_zero               peak amplitude relative to zero
    _pf_area_rel_zero               `Simpson's Rule Integral of the curve <https://en.wikipedia.org/wiki/Simpson%27s_rule>`_
    _pf_area_rel_min                | `Simpson's Rule Integral <https://en.wikipedia.org/wiki/Simpson%27s_rule>`_ relative to the minimum value of the curve
                                    | Substracts the minimum values of the peak curve before computing the integral
    _pf_rising_slope_avg            slope of the line drawn from the left base to the peak
    _pf_falling_slope_avg           slope of the line drawn from the right base to the peak
    _pf_duration_base               distance between the left and right base
    _pf_p_ix                        index of the peak maxima in the parent curve
    _pf_uuid                        peak `UUID <https://en.wikipedia.org/wiki/Universally_unique_identifier>`_
    _pf_b_ix_l                      index of the left base in the parent curve
    _pf_b_ix_r                      index of the right base in the parent curve
    =========================       ===========================================
    
    .. seealso:: ``mesmerize/analysis/compute_peak_features`` for the code that computes the peak features.

    ==========  =================
    Terminal    Description
    ==========  =================
    In          Input Transmission. Must contain *peak_bases* column that contains peak_bases DataFrames.
    Out         Transmission with peak features in various output columns
    ==========  =================
    
    ============    =================
    Parameter       Description
    ============    =================
    data_column     Data column containing numerical arrays.
                    | Peak features are computed relative these curves.
    Apply           Process data through this node
    ===================== 	=================

--------

.. _nodes_Math:

Math
----

**Nodes for performing basic Math functions**


.. _node_Derivative:

Derivative
^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Math.Derivative>`

	Computes the first derivative.
	
	**Output Data Column** *(numerical)*: _DERIVATIVE

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with the derivative placed in the output column
	========== 	=================

	===================== 	=================
	Parameter   		Description
	===================== 	=================
	data_column		Data column containing numerical arrays
	Apply			Process data through this node
	===================== 	=================



.. _node_TVDiff:

TVDiff
^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Math.TVDiff>`

	Based on `Numerical Differentiation of Noisy, Nonsmooth Data. Rick Chartrand. (2011). <http://dx.doi.org/10.5402/2011/164564>`_. Translated to Python by Simone Sturniolo.



.. _node_XpowerY:

XpowerY
^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Math.XpowerY>`

	Raises each element of the numerical arrays in the data_column to the exponent Y

	**Output Data Column** *(numerical)*: _X_POWER_Y

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with the result placed in the output column
	========== 	=================

	===================== 	=================
	Parameter   		Description
	===================== 	=================
	data_column		Data column containing numerical arrays
	Y			Exponent
	Apply			Process data through this node
	===================== 	=================


.. _node_AbsoluteValue:

AbsoluteValue
^^^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Math.AbsoluteValue>`

	Element-wise absolute values of the input arrays. Computes root mean squares if input arrays are complex.

	**Output Data Column** *(numerical)*: _ABSOLUTE_VALUE

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with the result placed in the output column
	========== 	=================

	===================== 	=================
	Parameter   		Description
	===================== 	=================
	data_column		Data column containing numerical arrays
	Apply			Process data through this node
	===================== 	=================


.. _node_LogTransform:

LogTransform
^^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Math.LogTransform>`

	Perform Logarithmic transformation of the data.

	**Output Data Column** *(numerical)*: _LOG_TRANSFORM

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with the result placed in the output column
	========== 	=================

	============ 	=================
	Parameter   	Description
	============ 	=================
	data_column	Data column containing numerical arrays

	transform		*log10*: Base 10 logarithm

				| *ln*: Natural logarithm

				| *modlog10*: :math:`sign(x) * \log_{10} (|x| + 1)`

				| *modln*: :math:`sign(x) * \ln (|x| + 1)`

	Apply		Process data through this node
	============ 	=================


ArrayStats
^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Math.ArrayStats>`

    Perform a few basic statistical functions.
    
    **Output Data Column** *(numerical)*: Customizable by user entry
    Output data are single numbers, not arrays
    
	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with the result placed in the output column
	========== 	=================
	
	The desired function is applied to each 1D array in the *data_column* and the output is placed in the Output Data Column.

	
    ============    =================
    Parameter       Description
    ============    =================
    data_column     Data column containing numerical arrays
    function        | *amin*: Return the minimum of the input array
    
                    | *amax*: Return the maximum of the input array
                    
                    | *nanmin*: Return the minimum of the input array, ignore NaNs
                    
                    | *nanmax*: Return the maximum of the input array, ignore NaNs
                    
                    | *ptp*: Return the range (max - min) of the values of the input array
                    
                    | *median*: Return the median of the input array
                    
                    | *mean*: Return the mean of the input array
                    
                    | *std*: Return the standard deviation of the input array
                    
                    | *var*: Return the variance of the input array
                    
                    | *nanmedian*: Return the median of the input array, ignore NaNs
                    
                    | *nanmean*: Return the mean of the input array, ignore NaNs

                    | *nanstd*: Return the standard deviation of the input array, ignore NaNs

                    | *nanvar*: Return the variance of the input array, ignore NaNs
                    
    output_col      Enter a name for the output column
    Apply           Process data through this node
    ============    =================



.. _node_ZScore:

ZScore
^^^^^^
    
    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Math.ZScore>`

    Compute Z-Scores of the data. Uses `scipy.stats.zscore <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.zscore.html>`_. The input data are are divided into groups according to the *group_by* parameter. Z-Scores are computed for the data in each group with respect to the data only in that group.
    
    **Output Data Column** *(numerical)*: _ZSCORE
    
	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		Transmission with the result placed in the output column
	========== 	=================
	
	=============  =============================================================
	Parameter      Description
	=============  =============================================================
	data_column    Input data column containing numerical arrays
	group_by       Categorial data column to group by.
	Apply          Process data through this node
	=============  =============================================================
    
    
--------------------

.. _nodes_Biology:

Biology
-------

**Nodes for some biologically useful things which I couldn't categorize elsewhere**


.. _node_ExtractStim:

ExtractStim
^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Biology.ExtractStim>`

	Extract the portions of a trace corresponding to stimuli that have been temporally mapped onto it. It outputs one row per stimulus period.

	===================    ========================================
	Output Data Column     Description
	===================    ========================================
	STIM_TYPE              Stimulus type, corresponds to your :ref:`Project Config <project-configuration>`
	STIMULUS               Name of the stimulus.
	_EXTRACT_STIM          The extracted array based on the parameters.
	uuid_stim		  UUID for the extracted stimulus period
	===================    ========================================

	============         =================
	Parameter            Description
	============         =================
	data_column          Data column containing the signals to be extracted based on the stimulus maps
	Stim_Type            Type of stimulus to extract
	Stimulus             Name of the stimulus to extract
	start_offset         Offset the start index of the stimulus mapping by a value (in frames)
	end_offset           Offset the end index of the stimulus mapping by a value (in frames)

	zero_pos             Zero index of the extracted signal

                             | *start_offset*: extraction begins at the *start_offset* value, stops at the *end_offset*

                             | *stim_end*: extraction begins at the end of the stimulus, stops at the *end_offset*.

                             | *stim_center*: extraction begins at the midpoint of the stimulus period plus the *start_offset*, stops at *end_offset*
	============         =================


.. _node_DetrendDFoF:

DetrendDFoF
^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Biology.DetrendDFoF>`

	Uses the `detrend_df_f <http://flatironinstitute.github.io/CaImAn/core_functions.html#caiman.source_extraction.cnmf.utilities.detrend_df_f>`_ function from the CaImAn library. This node does not use any of the numerical data in a Transmission DataFrame to compute the detrended :math:`\Delta F / F_0`. It directly uses the CNMF output data for the Samples that are present in the Transmission DataFrame.

	**Output Data Column** *(numerical)*: _DETREND_DF_O_F

	
.. _node_StaticDFoFo:

StaticDFoFo
^^^^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Biology.StaticDFoFo>`
    
    Perform :math:`\frac{F - F_0}{F_0}` without a rolling window. :math:`F` is an input array and :math:`F_0` is the minimum value of the input array.
    
    **Output Data Column** *(numerical)*: _STATIC_DF_O_F
    
    ==========  =================
    Terminal    Description
    ==========  =================
    In          Input Transmission
    Out         Transmission with the result placed in the output column
    ==========  =================

    ============    =========================================
    Parameter       Description
    ============    =========================================
    data_column     Data column containing numerical arrays
    Apply           Process data through this node
    ============    =========================================

    
----------------------

.. _nodes_Clustering:

Clustering
----------


.. _node_KShape:

KShape
^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Clustering.KShape>`
    
	Perform KShape clustering. For more information see :ref:`KShape plot <plot_KShape>`.

.. _node_KMeans:

KMeans
^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Clustering.KMeans>`

	Basically `sklearn.cluster.KMeans <https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html>`_.
    
----------------------


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

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Hierarchical.Linkage>`

	Compute a linkage matrix which can be used to form flat clusters using the :ref:`node_FCluster` node.

	Based on `scipy.cluster.hierarchy.linkage <https://docs.scipy.org/doc/scipy-1.2.1/reference/generated/scipy.cluster.hierarchy.linkage.html>`_

	========== 	=================
	Terminal		Description
	========== 	=================
	In		Input Transmission
	Out		 dict containing the Linkage matrix and parameters, **not a Transmission object**
	========== 	=================

	============= 	=================
	Parameters		Description
	=============	=================
	data_column	Numerical data column used for computing linkage matrix
	method		linkage method
	metric		metric for computing distance matrix

	optimal_order	minimize distance between successive leaves, more intuitive visualization

			| `Click here for more info <https://docs.scipy.org/doc/scipy-1.2.1/reference/generated/scipy.cluster.hierarchy.linkage.html?highlight=optimal_ordering>`_

	Apply		Process data through this node
	============= 	=================
	

.. _node_FCluster:

FCluster
^^^^^^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Hierarchical.FCluster>`
	
	"Form flat clusters from the hierarchical clustering defined by the given linkage matrix."

	Based on `scipy.cluster.hierarchy.fcluster <https://docs.scipy.org/doc/scipy-1.2.1/reference/generated/scipy.cluster.hierarchy.fcluster.html>`_

	**Output Data Column** *(categorial)*: FCLUSTER_LABELS

	====================            =================
	Terminal                        Description
	====================            =================
	Linkage                         Linkage matrix, output from :ref:`node_Linkage` node.
	Data                            Input Transmission, usually the same input Transmission used for the :ref:`node_Linkage` node.
	IncM *(optional)*	           Inconsistency matrix, output from :ref:`node_Inconsistent`
	Monocrit *(optinal)*	           Output from :ref:`node_MaxIncStat` or :ref:`node_MaxInconsistent`
	Out                             Transmission with clustering data that can be visualized using the :ref:`node_Heatmap`
	====================            =================
	
	**Parameters:** Exactly as desribed in `scipy.cluster.hierarchy.fcluster <https://docs.scipy.org/doc/scipy-1.2.1/reference/generated/scipy.cluster.hierarchy.fcluster.html>`_
	
	
	**HistoryTrace output structure:** Dict of all the parameters for this node, as well as the parameters used for creating the linkage matrix and the linkage matrix itself from the :ref:`Linkage node <node_Linkage>`.


.. _node_Inconsistent:

Inconsistent
^^^^^^^^^^^^


.. _node_MaxIncStat:

MaxIncStat
^^^^^^^^^^


.. _node_MaxInconsistent:

MaxInconsistent
^^^^^^^^^^^^^^^

----------------------



.. _nodes_Transform:

Transform
---------

Nodes for transforming data

.. _node_LDA:

LDA
^^^

    :class:`Source <mesmerize.pyqtgraphCore.flowchart.library.Transform.LDA>`

    Perform Linear Discriminant Analysis. Uses `sklearn.discriminant_analysis.LinearDiscriminantAnalysis <https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html>`_
    
    ============    ==========================================================
    Terminal        Description
    ============    ==========================================================
    train_data      Input Transmission containing the training data
    predict         Input Transmission containing data on which to predict
    T               | Transmission with Transformed data and decision function. Output columns outlined below:
                    | **_LDA_TRANSFORM:** The transformed data, can be visualized with a :ref:`Scatter Plot <plot_ScatterPlot>` for instance
                    | **_LDA_DFUNC:** Decision function (confidence scores). Can be visualized with a :ref:`Heatmap <plot_Heatmap>`
    coef            | Transmission with LDA Coefficients. Output columns outlined below:
                    | **classes:** The categorical labels that were trained against
                    | **_COEF:** LDA Coefficients (weight vectors) for the classes. Can be visualized with a :ref:`Heatmap <plot_Heatmap>`
    means           | Transmission with LDA Means. Output columns outlined below:
                    | **classes:** The categorical labels that were trained against
                    | **_MEANS:** LDA means for the classes. Can be visualized with a :ref:`Heatmap <plot_Heatmap>`
    predicted       | Transmission containing predicted class labels for the data.
                    | The class labels are placed in a column named **LDA_PREDICTED_LABELS**
                    | The names of the class labels correspond to the labels from the training labels
                    | *optional*
    ============    ==========================================================
    
    =============== ===================================================================
    Parameter       Description
    =============== ===================================================================
    train_data      Single or multiple data columns that contain the input features.
    labels          Data column containing categorical labels to train to
    solver          | *svd:* Singular Value Decomposition
                    | *lsqr:* Least Squares solution
                    | *eigen*: Eigen decomposition
    shrinkage       Can be used with *lsqr* or *eigen* solvers.
    shrinkage_val   shrinkage value if *shrinkage* is set to "value"
    n_components    Number of components to output
    tol             Tolereance threshold exponent. The used value is 10^<tol>
    score           Displays mean score of the classification (read only)
    predict_on      | Single or multiple data columns that contain the data that are used for predicting on
                    | Usually the same name as the data column(s) used for the training data.
                    | *optional*
    =============== ===================================================================
    
    **HistoryTrace output structure:** Dict of all the parameters for this node
    
