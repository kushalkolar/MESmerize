Data types used for analysis
****************************

.. _API_Transmission:

Transmission
================
**Inherits from BaseTransmission**

.. autoclass:: mesmerize.Transmission
	:members: __init__, empty_df, from_pickle, to_pickle, from_hdf5, to_hdf5, get_proj_path, set_proj_path, to_dict, from_proj, _load_files, merge
	:member-order: bysource
	:exclude-members: __weakref__

HistoryTrace
============
.. autoclass:: mesmerize.analysis.data_types.HistoryTrace
	:special-members:
	:members:
	:private-members:
	:member-order: bysource
	:exclude-members: __weakref__

Examples
========

.. include:: ./transmission_examples.rst
