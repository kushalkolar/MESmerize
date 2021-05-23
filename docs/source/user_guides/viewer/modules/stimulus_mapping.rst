.. _module_StimulusMapping:

Stimulus Mapping
****************

:ref:`API Reference <API_StimulusMapping>`

Video Tutorial
==============

This tutorial shows how to create a New Project, open images in the Viewer, use the Stimulus Mapping module and perform Caiman motion correction

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/D9zKhFkcKTk" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    

**Map temporal information such as stimulus or behavioral periods.**

Stimulus Mapping Module

.. image:: ./stim_maps_module.png

Stimulus periods illustrated on the viewer timeline

.. image:: ./stim_maps_viewer.png

The tabs that are available in the stimulus mapping module corresponds to the stimulus types in your :ref:`Project Configuration <StimulusTypeColumns>`.

You can add stimulus periods either manually or through a script.

Manual Annotation
=================

#. To add a stimulus manually click the "Add Row" button. This will add an empty row to the current tab page.

#. Enter a name for the stimulus, start time, end time, and pick a color for illustrating the stimulus periods on the Viewer timeline.

#. To remove a stimulus click the "Remove stim" button. Stimulus periods do not have to be added in chronological order.

#. Click "Set all maps" to set the mappings for all stimulus types. You can then choose to illustrate a stimulus on the viewer timeline by selecting it from "Show on timeline"

Import and Export are not implemented yet.

.. warning:: At the moment, only "frames" are properly supported for the time units.

.. note:: It is generally advisable to keep your stimulus names short with lowercase letters. When sharing your project you can provide a mapping for all your keys. This helps maintain consistency throughout your project and makes the data more readable.

Script
======

.. seealso:: :ref:`API Reference <API_StimulusMapping>`

You can also use the :ref:`Stimulus Mapping module's API <API_StimulusMapping>` to set the stimulus mappings from a pandas DataFrame.

.. include:: ../../../api_reference/viewer_modules/stimulus_mapping_api_example.rst
