.. _plot_KShape:

KShape
******

Perform `KShape clustering <http://www.cs.columbia.edu/~jopa/kshape.html>`_.

I recommend reading the paper on it: `Paparrizos, John, and Luis Gravano. "k-Shape: Efficient and Accurate Clustering of Time Series." In Proceedings of the 2015 ACM SIGMOD International Conference on Management of Data, pp. 1855-1870. ACM, 2015 <http://www.cs.columbia.edu/~jopa/Papers/PaparrizosSIGMOD2015.pdf>`_.

This GUI uses the `tslearn.clustering.KShape <https://tslearn.readthedocs.io/en/latest/gen_modules/clustering/tslearn.clustering.KShape.html#tslearn.clustering.KShape>`_ implementation.

.. seealso:: :ref:`API reference <API_KShape>`

.. note::
	This plot can be saved in an interactive form, see :ref:`Saving plots <save_ptrn>`

**Layout**

.. thumbnail:: ./kshape.png

**Left:** KShape parameters and Plot parameters

**Bottom left:** Plot of a random sample of input data from a cluster.

**Center:** Plot of cluster mean and either confidence interval, standard deviation, or neither. Uses on `seaborn.lineplot <https://seaborn.pydata.org/generated/seaborn.lineplot.html>`_

**Right:** Proportions plot. Exactly the same as :ref:`plot_Proportions`.

**Bottom Right:** Console

KShape Parameters
-----------------

The parameters and input data are simply fed to `tslearn.clustering.KShape <https://tslearn.readthedocs.io/en/latest/gen_modules/clustering/tslearn.clustering.KShape.html#tslearn.clustering.KShape>`_

Parameters outlined here are simply as they appear in the tslearn.

**data_column:** Input data for clustering.

**n_clusters:** Number of clusters to form.

**max_iter:** Maximum number of iterations of the k-Shape algorithm.

**tol:** Inertia variation threshold. If at some point, inertia varies less than this threshold between two consecutive iterations, the model is considered to have converged and the algorithm stops.

**n_init:** Number of times the k-Shape algorithm will be run with different centroid seeds. The final results will be the best output of n_init consecutive runs in terms of inertia.

**random_state:** Generator used to initialize the centers. If an integer is given, it fixes the seed. Defaults to the global numpy random number generator.

**training subset:** The subset of the input data that are used for used for training. After training, the predictions are fit on all the input data.

Plot Options
------------

**Plot cluster:** The cluster from which to plot random samples of input data in the bottom left plot

**Show centers:** Show the centroids returned by the KShape model

	.. warning::
		There's currently an issue where cluster centroids don't appear to be index correctly. See https://github.com/rtavenar/tslearn/issues/114


**max num curves:** Maximum number of input data samples to plot

**Error band:** The type of data to show for the the error band in the means plots.

**set x = 0 at:** The zero position of a means plots with respect to the cluster members in the plot.

**Save:** :ref:`Save the plot data and state in an interactive form <save_ptrn>`
