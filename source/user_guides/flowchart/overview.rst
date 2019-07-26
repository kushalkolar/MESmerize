.. _FlowchartOverview:

Flowchart Overview
******************
The flowchart allows you to analyze samples in your project and create plots by arranging analysis nodes. Each node takes an input, performs an operation, and produces an output. For example the :ref:`node_Derivative` node takes use-specified numerical arrays, computes the derivative of these arrays, and then outputs the result.

The Flowchart is based on the `pyqtgraph flowchart widgets <http://www.pyqtgraph.org/documentation/flowchart/>`_

**Flowchart Window**

.. thumbnail:: ./flowchart_overview.png

**Add node**: Right click -> Add node -> Choose from selection

Click on a node to highlight the Control Widget

**Remove node**: Right click -> Remove node

**Connecting nodes**: Click on a node terminal and drag to another terminal

**Save the flowchart layout**: Click "Save as..." to save the layout to a new file. You must specify the file extension as ".fc". If you save this file within the :ref:`"flowcharts" directory <ProjectStructure>` of your project it will show up in the :ref:`WelcomeWindow` when you open your project.

	.. note::
		This does not save the data, use the :ref:`node_Save` node to save data.

	.. warning::
		Due to a weird Qt or pyqtgraph bug certain parameter values (such as those in drop-down menus) can't be saved. Similarly, parameters values are lost when you save to an existing .fc file. If you're interested take a look at ``pyqtgraphCore.WidgetGroup``. Anyways you shouldn't be using the flowchart layout to save this information, that's what the History Trace in Transmission objects is for.

**Load an .fc file**: Click the "Load" button.

**Reset View button**: Reset the view, for example if you zoom out or pan too far.

.. _concept_Transmission:

Transmission
============

:ref:`API Reference <API_Transmission>`

Almost every node uses a Transmission object for input and output. A Transmission is basically a DataFrame and a History Trace (analysis log) of the data within the DataFrame.

	**Transmission DataFrame**

	The Transmission DataFrame is created from your :ref:`ProjectDataFrame` (or sub-DataFrame) by the :ref:`node_Load_Proj_DF` node. This initial DataFrame will contain the same columns as your Project DataFrame, and a new column named **_RAW_CURVE**. Each element (row) in the **_RAW_CURVE** column is a 1-D numerical array representing a single raw curve extracted from an ROI. 

	A new column named **_BLOCK_** is also added which contains the `UUID <https://en.wikipedia.org/wiki/Universally_unique_identifier>`_ for logging the analysis history of this newly created block of DataFrame rows, known as a *data block*. This allows you to merge Transmissions (see :ref:`_node_Merge` node) and maintain their independent analysis logs prior to the merge.

	**Naming conventions for DataFrame columns according to the data types**

	- *numerical data*: single leading underscore ( _ ). All caps if produced by a flowchart node.
	- *categorial data*: no leading underscore. All caps if produced by flowhchart node.
	- *special cases*: Peak detection data are placed in a column named **peaks_bases** where each element is a DataFrame.
	- *uuid data*: has uuid or UUID in the name

	.. note::
		_BLOCK_ is an exception, it contains UUIDs not numerical data.

	**History Trace**

	The History Trace of a Transmission is a log containing the discrete analysis steps, known as operations, along with their parameters and any other useful information. When a flowchart node performs an operation it stores the output(s) data in the Transmission DataFrame and appends the operation parameters to this log. A seperate log is kept for each data block present in the Transmission DataFrame.


.. _console_Flowchart:

Console
=======

You have direct access to the data within the nodes through the console in the flowchart. To show the console go to View -> Console.

.. seealso:: If you are unfamiliar with the console see the overview on :ref:`ConsoleOverview`

Call ``get_nodes()`` to view a dict of all nodes in the flowchart. You can access the output Transmission in most nodes through the attribute `t`. You can access the transmission dataframe through ``t.df``.

.. seealso:: See the :ref:`Transmission API <API_Transmission>` for more information. Sources for the nodes at mesmerize/pyqtgraphCore/flowchart/library.

**Example, directly accessing DataFrame elements through the flowchart console**

.. thumbnail:: ./flowchart_console.png
