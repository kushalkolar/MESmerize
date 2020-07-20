.. _API_StimulusMapping:

Stimulus Mapping
****************

ModuleGUI
=========

.. autoclass:: mesmerize.viewer.modules.stimulus_mapping.ModuleGUI
    :members: maps

Page
====

**Each Page instance contains the mapping data for one stimulus type**

.. autoclass:: mesmerize.viewer.modules.stimmap_modules.page.Page
    :members: set_data, get_dataframe, set_units, get_units, add_row, delete_row, clear
    :member-order: bysource
    
DataFrame Format
================

**Page.set_data() expects a DataFrame in the following format**

**Columns**

    ======= ===============================================================
    Column  Description
    ======= ===============================================================
    name    Stimulus name
    start   Start time of stimulus period
    end     End time of stimulus period
    color   Color to display in the viewer curve plot
    ======= ===============================================================

    Data types:
    
    ======= ===============================================================
    Column  Data type
    ======= ===============================================================
    name    str
    start   numpy.float64
    end     numpy.float64
    
    color   Tuple in RGBA format
    
            | (int, int, int, int)
            
            | Each int must be within the 0 - 255 range
    ======= ===============================================================

**Example**

    ========    =========== =============   =================== 
    name        start       end             color
    ========    =========== =============   =================== 
    control     0.0         328.0           (0, 75, 0, 255)
    stim_A      328.0       1156.0          (0, 0, 125, 255)
    stim_C      1156.0      2987.0          (125, 0, 0, 255)
    ========    =========== =============   =================== 
