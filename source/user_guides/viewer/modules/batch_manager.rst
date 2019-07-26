.. _module_BatchManager:

Batch Manager
*************

**Batch process computationally intensive tasks.**

.. seealso:: :ref:`Batch Manager API <API_BatchManager>`

This is currently used for :ref:`Caiman Motion Correction <module_CaimanMotionCorrection>`, :ref:`CNMF <module_CNMF>`, and :ref:`CNMFE <module_CNMFE>`.

The Batch Manager can be accessed in the viewer through Modules -> Batch Manager. If you don't have a batch open you will be prompted with a dialog to open a batch or to select a location for a new batch.

.. warning:: The full path to the batch directory must not contain spaces or special characters, only a-Z, A-Z and numbers.

The Batch Manager processes the batch items in external processes, allowing you to add batch items when that batch is being processed.

Layout
======

.. thumbnail:: ./batch_manager.png

Window title: Name of batch directory

**Top:** Parent directory of batch directory

**Top left:** list of batch items and some controls.

    ===========    ================================================
    Colors          Description
    ===========    ================================================
    Green           Finished without exceptions
    Red             Did not finish, click on the item to see the exceptions in the bottom right information area
    Yellow          Currently being processed
    Orange          Item aborted by user
    Blue            Output data for this item are being moved from the work dir to the batch dir.
    ===========    ================================================        
    
    ======================    ================================================
    Button                      Description
    ======================    ================================================
    Start                       Process the batch from the first item.
    Start at selection          Process the batch starting from the item that is currently selected in the list.
    Delete selection            Delete the item that is currently being selected along with the associated data in the batch dir.
    Export shell scripts        Export bash scripts so that the batch items can be run on a computing cluster
    Abort                       Abort the current batch item
    New batch                   Create a new batch
    Open batch                  Open a batch
    View Input                  Open the input work environment, in the viewer, for the currently selected item
    Compress                    Not implemented
    ======================    ================================================
    
    **Use work dir:** Check this box to use the work dir that has been set in the :ref:`System Configuration <SystemConfiguration>`
    
**Top right:** Standard out from the external processes that are processing the batch items.

**Bottom left:** Parameters for the selected batch item. The first line is the UUID of the batch item.

**Bottom right:** Output information area for the currently selected item.

Scheduling
==========

You can schedule a batch to run at a later time using the following bash script. Doesn't work for a snap installation yet.

:download:`mesmerize-scheduler <./mesmerize-scheduler>`

**Usage:**

.. highlight:: none

.. code::

    Usage: mesmerize-scheduler -b <batch> -i <start item> -t <start time>                                                    
                                                                                                                                                                 
        -b      full batch path in quotes, no spaces                                                                                                                                 
        -i      uuid of the batch item to start from, no quotes                                                                                                                             
        -t      time at which to start the batch, no quotes                                                                                                                                   
                                                                                                                                                                                                
        examples of how to specify time:                                                                                                                                                            
                23:00  7:30Feb30                                                                                                                                                                    
                use 24hr time and no spaces                                                                                                                                                           
                                                                                                                                                                                                        
    Full usage example:                                                                                                                                                                                     
        mesmerize-scheduler -b "/share/data/temp/kushal/pc2_batch" -i a80d1923-e490-4eb3-ba4f-7e651d4cf938 -t 2:00                                                                                         
