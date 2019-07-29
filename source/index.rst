.. Mesmerize documentation master file, created by
   sphinx-quickstart on Mon Apr  8 17:48:39 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Mesmerize's documentation!
=====================================

| GitHub: https://github.com/kushalkolar/MESmerize
| Help forum: https://groups.google.com/d/forum/mesmerize

.. toctree::
	:maxdepth: 1
	:caption: Overview

	./Overview
	./user_guides/installation
	./user_guides/faq

.. toctree::
	:maxdepth: 1
	:caption: Project Organization:

	./user_guides/project_organization/new_project/new_project
	./user_guides/project_organization/project_browser/project_browser

.. toctree::
	:maxdepth: 1
	:caption: Viewer

	./user_guides/viewer/overview
	./user_guides/convert_meta_data
	./user_guides/viewer/add_to_project
	
.. toctree::
    :maxdepth: 1
    :caption: Viewer Modules
    
    ./user_guides/viewer/modules/batch_manager
    ./user_guides/viewer/modules/roi_manager
    ./user_guides/viewer/modules/caiman_motion_correction
    ./user_guides/viewer/modules/cnmf
    ./user_guides/viewer/modules/cnmfe
    
.. toctree::
	:maxdepth: 1
	:caption: Flowchart

	./user_guides/flowchart/overview
	./user_guides/flowchart/nodes
	./user_guides/flowchart/examples

.. toctree::
	:maxdepth: 1
	:caption: Plots
	:glob:

	./user_guides/plots/*

.. toctree::
	:maxdepth: 2
	:caption: Misc

	./user_guides/general/misc

.. toctree::
	:maxdepth: 2
	:caption: API Reference

	./api_reference/Viewer_data_types
	./api_reference/viewer_modules/viewer_modules
	./api_reference/viewer_modules/roi_manager
	./api_reference/Analysis_data_types
	./api_reference/plotting/widgets/kshape



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

