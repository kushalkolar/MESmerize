.. _developer_nodes:

Nodes
*****

The easiest way to create a new node is create a class that inherits from CtrlNode in one of the existing node modules.

Become familiar with the :ref:`Transmission object <concept_Transmission>` before creating a node. Almost all nodes work with a Transmission object for storing data. Make sure to conform to the conventions for naming of data columns and categorical columns.

Simple node
===========

The simplest type of node doesn't take any parameters and 

.. code-block:: python
    :linenos:
    
    class Derivative(CtrlNode):
    """Return the Derivative of a curve."""
    nodeName = 'Derivative'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        output_column = '_DERIVATIVE'

        self.t.df[output_column] = self.t.df[self.data_column].apply(np.gradient)
        self.t.last_output = output_column

        params = {'data_column': self.data_column,
                  'units': self.t.last_unit
                  }

        self.t.history_trace.add_operation(data_block_id='all', operation='derivative', parameters=params)

        return self.t
