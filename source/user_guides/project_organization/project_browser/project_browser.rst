.. _ProjectBrowser:

Project Browser
***************

**Browse, edit and sort the project DataFrame**

You can open the Project Browser from the :ref:`Welcome Window <WelcomeWindow>` after you have opened a project.

.. thumbnail:: ./overview.png

The columns that are visible in the Project Browser Window correspond to the :ref:`Project Configuration <project-configuration>`. For each column you will see a list which is a set of unique elements from that column in the project DataFrame.

Functions

Open Sample
===========

Double-click on a Sample in the *SampleID* column to open it in the :ref:`Viewer <ViewerOverview>`

Filter
======

You can sort your Project DataFrame into different groups (such as experimental groups) using simple text and numerical filters.



Editor
======

You can view and edit the Project DataFrame directly in a GUI using the DataFrame editor.

.. thumbnail:: ./dataframe_editor.png

.. warning:: Make sure you know what you are doing when you directly modify the Project DataFrame. Changes cannot be undone but you can restore a backup from the project's :ref:`dataframe directory <ProjectStructure>`. For example, do not modify data under the following columns: CurvePath, ImgInfoPath, ImgPath, ROI_State, any uuid column.

.. seealso:: Uses the `Spyder object editor <https://docs.spyder-ide.org/variableexplorer.html?highlight=object%20editor>`_

Export
======

Console
=======

If you are familiar with pandas you can interact with the project DataFrame directly. If you are unfamiliar with pandas it's very easy to learn.

.. seealso:: `Pandas documentation <https://pandas.pydata.org/pandas-docs/version/0.24/>`_

**Useful Callables**

=========================   ===================================
Callable                    Purpose
=========================   ===================================
get_dataframe()             returns dataframe of the current project browser tab
get_root_dataframe()        always returns dataframe of the root tab (entire project DataFrame)
set_root_dataframe()        pass a pandas.DataFrame instance to set it as the project DataFrame
=========================   ===================================

Usage
-----

General usage in order to modify the project DataFrame would be something like this:

.. code-block:: python
    
    # Get a copy the project DataFrame to modify
    df = get_root_dataframe().copy()
    
    # Do stuff to df
    ...
    
    # Set the project DataFrame with the modified one
    set_root_dataframe(df)    

Example
--------

Let's say you have been inconsistent in naming "ATENA" ROI Tags in the "cell_name" column. You can rename all occurances of 'atena' to 'ATENA'

.. code-block:: python

    # Get a copy of the project DataFrame
    >>> df = get_root_dataframe().copy()
    
    # View all occurances of 'atena'
    >>> df.cell_name[df.cell_name == 'atena']
    2      atena
    3      atena
    4      atena
    5      atena
    6      atena
    205    atena
    Name: cell_name, dtype: object
    
    # Rename all occurances of 'atena' to 'ATENA'
    >>> df.cell_name[df.cell_name == 'atena'] = 'ATENA'
    
    # Check that there are more occurances of 'atena'
    >>> df.cell_name[df.cell_name == 'atena']
    Series([], Name: cell_name, dtype: object)

    # Check that we have renamed the 'atena' occurances to 'ATENA'
    # Indices 2-6 and 205 were named 'atena'
    >>> df.cell_name
    0      untagged
    1      untagged
    2         ATENA
    3         ATENA
    4         ATENA
    5         ATENA
    6         ATENA
    7         atenp
    ...
    Name: cell_name, Length: 311, dtype: object
    
    # Check index 205
    >>> df.cell_name.iloc[205]
    'ATENA'
    
    # Finally set the changed DataFrame as the root (project) DataFrame
    >>> set_root_dataframe(df)

    
    
