Citation guide
**************

Mesmerize provides interfaces to many great tools that were created by other developers. Please cite the papers for the following Viewer Modules and analysis methods that you use in addition to citing Mesmerize. I would also suggest citing numpy, pandas, scipy, sklearn, and matplotlib.

Mesmerize relies heavily on `pyqtgraph widgets <pyqtgraph.org>`_. `Citing pyqtgraph. <https://groups.google.com/forum/#!msg/pyqtgraph/fnNGN6j132E/WPr89jpSb_QJ>`_

Viewer
======

===================================================================     ========================================================
Module                                                                  Cite
===================================================================     ========================================================
:ref:`CNMF <module_CNMF>`                                               | Giovannucci A., Friedrich J., Gunn P., Kalfon J., Brown, B., Koay S.A., Taxidis J., Najafi F., Gauthier J.L., Zhou P., Baljit, K.S., Tank D.W., Chklovskii D.B., Pnevmatikakis E.A. (2019). CaImAn: An open source tool for scalable Calcium Imaging data Analysis. eLife 8, e38173. https://elifesciences.org/articles/38173

                                                                        | Pnevmatikakis, E.A., Soudry, D., Gao, Y., Machado, T., Merel, J., ... & Paninski, L. (2016). Simultaneous denoising, deconvolution, and demixing of calcium imaging data. Neuron 89(2):285-299. http://dx.doi.org/10.1016/j.neuron.2015.11.037
                                                                        
                                                                        | Pnevmatikakis, E.A., Gao, Y., Soudry, D., Pfau, D., Lacefield, C., ... & Paninski, L. (2014). A structured matrix factorization framework for large scale calcium imaging data analysis. arXiv preprint arXiv:1409.2903. `<http://arxiv.org/abs/1409.2903>`_
                
:ref:`CNMFE <module_CNMFE>`                                             | In addition to the above CNMF papers:
                                                                        | Zhou, P., Resendez, S. L., Rodriguez-Romaguera, J., Jimenez, J. C., Neufeld, S. Q., Giovannucci, A., … Paninski, L. (2018). Efficient and accurate extraction of in vivo calcium signals from microendoscopic video data. ELife, 7. doi: https://doi.org/10.7554/eLife.28728.001
:ref:`Caiman Motion Correction <module_CaimanMotionCorrection>`         | Giovannucci A., Friedrich J., Gunn P., Kalfon J., Brown, B., Koay S.A., Taxidis J., Najafi F., Gauthier J.L., Zhou P., Baljit, K.S., Tank D.W., Chklovskii D.B., Pnevmatikakis E.A. (2019). CaImAn: An open source tool for scalable Calcium Imaging data Analysis. eLife 8, e38173. https://elifesciences.org/articles/38173

                                                                        | Pnevmatikakis, E.A., and Giovannucci A. (2017). NoRMCorre: An online algorithm for piecewise rigid motion correction of calcium imaging data. Journal of Neuroscience Methods, 291:83-92. https://doi.org/10.1016/j.jneumeth.2017.07.031
                                                                        
:ref:`Nuset Segmentation <NusetSegmentation>`                           | Yang L, Ghosh RP, Franklin JM, Chen S, You C, Narayan RR, et al. (2020) NuSeT: A deep learning tool for reliably separating and analyzing crowded cells. PLoS Comput Biol 16(9): e1008193. https://doi.org/10.1371/journal.pcbi.1008193
===================================================================     ========================================================


Nodes/Analysis
==============

===================================================     ========================================================================
Node/Method                                             Cite
===================================================     ========================================================================
:ref:`k-Shape clustering <plot_KShape>`                 | Paparrizos, J., & Gravano, L. (2016). k-Shape. ACM SIGMOD Record, 45(1), 69–76. doi: http://dx.doi.org/10.1145/2723372.2737793

                                                        | Romain Tavenard, Johann Faouzi, Gilles Vandewiele and Felix Divo, Guillaume Androz, Chester Holtz, Marie Payne, Roman Yurchak, Marc Ruβwurm, Kushal Kolar, & Eli Woods. (2017). Tslearn, A Machine Learning Toolkit for Time Series Data. Journal of Machine Learning Research, (118):1−6, 2020. http://jmlr.org/papers/v21/20-091.html
                                                        
:ref:`Cross-correlation <plot_CrossCorrelation>`        | Romain Tavenard, Johann Faouzi, Gilles Vandewiele and Felix Divo, Guillaume Androz, Chester Holtz, Marie Payne, Roman Yurchak, Marc Ruβwurm, Kushal Kolar, & Eli Woods. (2017). Tslearn, A Machine Learning Toolkit for Time Series Data. Journal of Machine Learning Research, (118):1−6, 2020. http://jmlr.org/papers/v21/20-091.html

:ref:`TVDiff Node <node_TVDiff>`                        Rick Chartrand, “Numerical Differentiation of Noisy, Nonsmooth Data,” ISRN Applied Mathematics, vol. 2011, Article ID 164564, 11 pages, 2011. https://doi.org/10.5402/2011/164564.
===================================================     ========================================================================

Scientific Libraries
====================

=============== ==========================================================================================
Library
=============== ==========================================================================================
numpy           | Van Der Walt, S., Colbert, S. C. & Varoquaux, G. The NumPy array: A structure for efficient numerical computation. Comput. Sci. Eng. (2011) doi:10.1109/MCSE.2011.37

pandas          | McKinney, W. Data Structures for Statistical Computing in Python. Proc. 9th Python Sci. Conf. (2010)

scipy           | Virtanen, P., Gommers, R., Oliphant, T.E. et al. SciPy 1.0: fundamental algorithms for scientific computing in Python. Nat Methods (2020). https://doi.org/10.1038/s41592-019-0686-2

sklearn         | Pedregosa, F. et al. Scikit-learn: Machine learning in Python. J. Mach. Learn. Res. (2011)

matplotlib      | Hunter, J. D. Matplotlib: A 2D graphics environment. Comput. Sci. Eng. (2007)

pyqtgraph       | http://www.pyqtgraph.org/
=============== ==========================================================================================
