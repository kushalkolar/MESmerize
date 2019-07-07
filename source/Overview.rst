Overview
********

.. image:: ./imgs/Overview/welcome_window.png
   :target: ./imgs/Overview/welcome_window.png
   :alt: alt text


The Viewer
^^^^^^^^^^


.. image:: ./imgs/Overview/overview.png
   :target: ./imgs/Overview/overview.png
   :alt: alt text


Opening Image sequences
^^^^^^^^^^^^^^^^^^^^^^^

Mesmerize is able to work with standard 2D imaging sequences stored as tiff files and also with mes files from Femtonics microscopes. The downstream analysis is the same regardless of the input source once it's in the viewer.

Stimulus mapping
^^^^^^^^^^^^^^^^

Stimulus information from mes files or CSV's can be mapped onto your imaging data.

CaImAn modules
^^^^^^^^^^^^^^

Mesmerize contains front-end GUI modules for the extremely useful and versatile CaImAn library. This makes it very easy for users to make use of the library without writing a single line of code.

**CaImAn Elastic Motion Correction**


.. image:: ./imgs/Overview/motion_correction.png
   :target: ./imgs/Overview/motion_correction.png
   :alt: alt text


**CNMFE**


.. image:: ./imgs/Overview/cnmfe.png
   :target: ./imgs/Overview/cnmfe.png
   :alt: alt text


The computationally intense procedures performed using the CaImAn library (Elastic Motion Correction and CNMF) can be organized using the Mesmerize Batch Manager.

Batch Manager
^^^^^^^^^^^^^


.. image:: ./imgs/Overview/batch_manager.png
   :target: ./imgs/Overview/batch_manager.png
   :alt: alt text


ROI Manager
^^^^^^^^^^^

Data analysis - pyqtgraph programmable flowcharts.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Types of Nodes**


* **Data Nodes**

  * Load_Proj_DF
  * Save
  * Load

* **Plotting**

  * Simple time series
  * Heatmap

* **Categorical Filters**

  * Align Stims
  * ROI Selection
  * Genotype selection
  * Peak Detection
  * Custom columns

* **Filters and Signal Processing**

  * Butterworth filter
  * Savitzsky-Golay filter
  * Derivative
  * Resample
  * Normalize
  * Z-Score

    * **Math**

  * LogTransform
  * Discreate fourier transform
  * Inverse discrete fourier transform
  * Absolute value

* **Clustering** - based on sklearn

  * KMeans
  * Agglomerative
  * LDA

* **Transform** - based on sklearn

  * Manifold Learning

    * Isomap
    * Locally Linear Embedding
    * Spectral Embedding
    * MDS

      * **Decomposition** - based on sklearn
      * PCA
