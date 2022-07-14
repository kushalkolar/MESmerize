.. Mesmerize documentation master file, created by
   sphinx-quickstart on Mon Apr  8 17:48:39 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Deprecated - Please use newer mesmerize packages
************************************************

**The Mesmerize desktop application is no longer in active development and is now treated as legacy software. Please checkout the new mesmerize packages which will be ready for public use very soon!**

**These new packages are also MUCH easier to install! They are also much more efficient, faster, and offer richer and more versatile features.**

**The batch management system offered by ``mesmerize-core`` is conceptually similar to that within the original Mesmerize package, but it is much more efficient.**

| **mesmerize-core:** https://github.com/nel-lab/mesmerize-core
| **mesmerize-viz (WIP):** https://github.com/kushalkolar/mesmerize-viz
| **mesmerize-napari:** https://github.com/nel-lab/mesmerize-napari

Mesmerize Documentation
***********************
   
.. image:: ./banner.png


| biorxiv: https://doi.org/10.1101/840488
| GitHub: https://github.com/kushalkolar/MESmerize
| Questions/Discussion: `Gitter room <https://gitter.im/mesmerize_discussion/community?utm_source=share-link&utm_medium=link&utm_campaign=share-link>`_ |gitter_badge|
| Contact: kushalkolar@alumni.ubc.ca

.. |gitter_badge| image:: https://badges.gitter.im/mesmerize_discussion/community.svg
                    :target: https://gitter.im/mesmerize_discussion/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge

.. toctree::
	:maxdepth: 1
	:caption: Overview

	./Overview
	./user_guides/installation
	./getting_help
	./user_guides/faq
	./citation_guide
        ./users

.. toctree::
	:maxdepth: 1
	:caption: Project Organization:

	./user_guides/project_organization/new_project/new_project
	./user_guides/project_organization/project_browser/project_browser

.. toctree::
	:maxdepth: 1
	:caption: Viewer

	./user_guides/viewer/overview
	./user_guides/viewer/add_to_project
	
.. toctree::
    :maxdepth: 1
    :caption: Viewer Modules
    
    ./user_guides/viewer/modules/tiff_file
    ./user_guides/viewer/modules/inscopix_importer
    ./user_guides/viewer/modules/batch_manager
    ./user_guides/viewer/modules/stimulus_mapping
    ./user_guides/viewer/modules/roi_manager
    ./user_guides/viewer/modules/caiman_motion_correction
    ./user_guides/viewer/modules/cnmf
    ./user_guides/viewer/modules/cnmf_3d
    ./user_guides/viewer/modules/cnmfe
    ./user_guides/viewer/modules/caiman_hdf5_importer
    ./user_guides/viewer/modules/suite2p_importer
    ./user_guides/viewer/modules/nuset_segmentation
    ./user_guides/viewer/modules/script_editor
    ./user_guides/viewer/modules/femtonics_importers
    
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
    :maxdepth: 1
    :caption: Developer Guide
    :glob:
    
    ./developer_guide/*

.. toctree::
	:maxdepth: 2
	:caption: API Reference
	:glob:
	
	./api_reference/common
	./api_reference/Viewer_data_types
	./api_reference/viewer_modules/viewer_modules
	./api_reference/viewer_modules/roi_manager
	./api_reference/viewer_modules/stimulus_mapping
	./api_reference/Analysis_data_types
	./api_reference/analysis
	./api_reference/nodes
	./api_reference/plotting/utils
	./api_reference/plotting/widgets/*



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

