Data types used for analysis
****************************

.. _API_Transmission:

Transmission
================
**Inherits from BaseTransmission**

.. autoclass:: mesmerize.Transmission
	:members: __init__, empty_df, from_pickle, to_pickle, from_hicke, to_hickle, from_hdf5, to_hdf5, get_proj_path, set_proj_path, to_dict, from_proj, _load_files, merge
	:member-order: bysource

BaseTransmission
================
.. autoclass:: mesmerize.analysis.data_types.BaseTransmission
	:special-members:
	:members:
	:member-order: bysource
	:exclude-members: __weakref__
	:private-members:

.. _API_Transmission_helper_functions:

Helper functions
================

.. autofunction:: mesmerize.analysis.get_sampling_rate

.. autofunction:: mesmerize.analysis.get_array_size

.. _API_HistoryTrace:


HistoryTrace
================
.. autoclass:: mesmerize.analysis.data_types.HistoryTrace
	:special-members:
	:members:
	:private-members:
