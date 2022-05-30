.. _developer_nodes:

Nodes
*****

The easiest way to create a new node is create a class that inherits from :class:`CtrlNode <mesmerize.pyqtgraphCore.flowchart.library.common.CtrlNode>`. You can place this class in one of the existing modules in mesmerize/pyqtgraphCore/flowchart/library

Become familiar with the :ref:`Transmission object <concept_Transmission>` before creating a node. Almost all nodes work with a Transmission object for storing data. Make sure to conform to the conventions for naming of data columns and categorical columns.

Simple node
===========

The simplest type of node performs an operation on a user-specified data column and doesn't take any parameters.

**Basic structure**

.. code-block:: python
    
    class MyNode(CtrlNode):
    """Doc String that is shown when node is clicked on"""
    nodeName = 'MyNode'
    uiTemplate = <list of tuples, see below>
    
    def processData(self, transmission: Transmission):
        self.t = transmission.copy()  #: input to this node
        
        # .. do stuff to the Transmission DataFrame
        
        params = <dict of analysis params>
        
        # log the analysis that was done
        self.t.history_trace.add_operation('all', 'mynode', params)
        
        # Send the output
        return self.t

Required class attributes:

- **nodeName: (str)** The name prefix used when instances of this node are created in the flowchart
- **uiTemplate: (list)** :ref:`List of UI element tuples (see section) <node_devGuide_uiTemplate>`

If the node only has one input and one output terminal it is sufficient to create a processData method that performs the node's analysis operation(s).

Example
-------

.. code-block:: python
    
    class Derivative(CtrlNode):
    """Return the Derivative of a curve."""
    nodeName = 'Derivative'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]
    
    # If there is only one input and one output temrinal, processData will 
    # always have a single argument which is just the input transmission, 
    # i.e. the output from the previous node.
    def processData(self, transmission: Transmission):
        # the input transmission
        self.t = transmission
        
        # If a comboBox widget named 'data_column' is specified in the 
        # uiTemplate, you can update its contents using the following method. 
        # This will populate the comboBox with all the data columns from the 
        # input transmission and select the input data column as the 
        # output data column from the previous node.
        self.set_data_column_combo_box()
        
        # Check if the Apply checkbox is checked
        if self.ctrls['Apply'].isChecked() is False:
            return
        
        # Make a copy of the input transmission so we can modify it to create an output
        self.t = transmission.copy()
        
        # By convention output columns are named after the node's name and in all caps
        # Columns containing numerical data have a leading underscore
        output_column = '_DERIVATIVE'
        
        # Perform this nodees operation
        self.t.df[output_column] = self.t.df[self.data_column].apply(np.gradient)
        
        # Set tranmission's `last_output` attribute as the name of the output column
        # This is used by the next node to know what thet last output data was
        self.t.last_output = output_column
        
        # Create a dict of parameters that this node used
        # Usually a dict that captures the state of the uiTemplate
        # the transmission `last_unit` attribute is the data units of the data 
        # in the output column (i.e. `t.last_output`). Change it only if the data units change
        params = {'data_column': self.data_column,
                  'units': self.t.last_unit
                  }
        
        # Add a log of this node's operation to the transmission's `HistoryTrace` instance
        # Nodes usually perform an operation on all datablocks pass 'all' to the data_block_id argument
        # By convention the operation name is the name of the node in lowercase letters
        self.t.history_trace.add_operation(data_block_id='all', operation='derivative', parameters=params)
        
        # return the modified transmission instance, which is then the output of this node
        return self.t


Complex node
============

For a more complex node with multiple inputs and/or outputs you will need to explicitly specify the terminals when instantiating the parent :class:`CtrlNode <mesmerize.pyqtgraphCore.flowchart.library.common.CtrlNode>` and create a simple override of the process() method.

Format of the dict specifying the node's terminals:

::

    {
        <terminal name (str)>:             {'io': <'in' or 'out'>}, 
        <another terminal name (str)>:     {'io', <'in' or 'out'>},
        <another terminal name (str)>:     {'io', <'in' or 'out'>}
        ...
    }
    
Override the process() method simply pass all kwargs to a processData() method and return the output
The processData() method must return a dict. This dict must have keys that correspond to the specified output terminals. The values of these keys are the outputs from the respective terminals.

Here is a trimmed down example from the :class:`LDA node <mesmerize.pyqtgraphCore.flowchart.library.Transform.LDA>`:

.. code-block:: python
    
    class LDA(CtrlNode):
    """Linear Discriminant Analysis, uses sklearn"""
    nodeName = "LDA"
    uiTemplate = [('train_data', 'list_widget', {'selection_mode': QtWidgets.QAbstractItemView.ExtendedSelection,
                                                    'toolTip': 'Column containing the training data'}),
                  ('train_labels', 'combo', {'toolTip': 'Column containing training labels'}),
                  ('solver', 'combo', {'items': ['svd', 'lsqr', 'eigen']}),
                  ('shrinkage', 'combo', {'items': ['None', 'auto', 'value']}),
                  ('shrinkage_val', 'doubleSpin', {'min': 0.0, 'max': 1.0, 'step': 0.1, 'value': 0.5}),
                  ('n_components', 'intSpin', {'min': 2, 'max': 1000, 'step': 1, 'value': 2}),
                  ('tol', 'intSpin', {'min': -50, 'max': 0, 'step': 1, 'value': -4}),
                  ('score', 'lineEdit', {}),
                  ('predict_on', 'list_widget', {'selection_mode': QtWidgets.QAbstractItemView.ExtendedSelection,
                                                 'toolTip': 'Data column of the input "predict" Transmission\n'
                                                            'that is used for predicting from the model'}),
                  ('Apply', 'check', {'applyBox': True, 'checked': False})
                  ]

    def __init__(self, name, **kwargs):
        # Specify the terminals with a dict
        CtrlNode.__init__(self, name, terminals={'train': {'io': 'in'},
                                                 'predict': {'io': 'in'},

                                                 'T': {'io': 'out'},
                                                 'coef': {'io': 'out'},
                                                 'means': {'io': 'out'},
                                                 'predicted': {'io': 'out'}
                                                 },
                          **kwargs)
        self.ctrls['score'].setReadOnly(True)
    
    # Very simple override
    def process(self, **kwargs):
        return self.processData(**kwargs)

    def processData(self, train: Transmission, predict: Transmission):
        self.t = train.copy()  #: Transmisison instance containing the training data with the labels
        self.to_predict = predict.copy()  #: Transmission instance containing the data to predict after fitting on the the training data
        
        # function from mesmerize.analysis.utils
        dcols, ccols, ucols = organize_dataframe_columns(self.t.df.columns)
        
        # Set available options for training data & labels
        self.ctrls['train_data'].setItems(dcols)
        self.ctrls['train_labels'].setItems(ccols)
        
        dcols = organize_dataframe_columns(self.to_predct.df.columns)
        # Set available data column options for predicting on
        self.ctrls['predict_on'].setItems(dcols)
        
        # Process further only if Apply is checked
        if not self.ctrls['Apply'].isChecked():
            return
        
        # Get the user-set parameters
        train_column = self.ctrls['train_data'].currentText()
        
        # ... get other params
        n_components = self.ctrls['n_components'].value()

        # ... do stuff
        
        # This node ouputs separate transmissions that are all logged
        self.t.history_trace.add_operation('all', 'lda', params)
        self.t_coef.history_trace.add_operation('all', 'lda', params)
        self.t_means.history_trace.add_operation('all', 'lda', params)
        
        # the `to_predict` transmission is logged differently
        self.to_predict.history_trace.add_operations('all', 'lda-predict', params_predict)
        
        # dict for organizing this node's outputs
        # The keys MUST be the same those specified for this node's output terminals
        out = {'T': self.t,
               'coef': self.t_coef,
               'means': self.t_means,
               'predicated': self.to_predct
               }

        return out


.. _node_devGuide_uiTemplate:

uiTemplate
==========

Specify the uiTemplate attribute as a list of tuples.

One tuple per UI element with the following structure:

(<name (str)>, <type (str)>, <dict of attributes to set>)

Examples:

.. code-block:: python
    
    ('dist_metric', 'combo', {'items': ['euclidean', 'wasserstein', 'bah'], 'toolTip': 'distance metric to use'})
    ('n_components', 'intSpin', {'min': 2, 'max': 10, 'value': 2, 'step': 1, 'toolTip': 'number of components'})
    ('data_columns', 'list_widget', {'selection_mode': QtWidgets.QAbstractItemView.ExtendedSelection})

The name can be anything. Accepted types and accepted attributes are outlined below

=============   ========================================================================================
widget type     attributes that can be set
=============   ========================================================================================
intSpin         | *min (int):* minimum value allowed in the spinbox
                | *max (int):* maximum value allowed
                | *step (int):* step size
                | *value (int):* default value
doubleSpin      | *min (float):* minimum value allowed in the spinbox
                | *max (float):* maximum value allowed
                | *step (float):* step size
                | *value (float):* default value
check           | *checked (bool):* default state of the checkBox
                | *applyBox (bool):* Whether this is an "Apply checkbox"
radioBtn        | *checked (bool):* default state of this radioButton
combo           | *items (list):* default list of items that will be set in the comboBox
list_widget     | *items (list):* default list of items that will be set in the list_widget
                | *selection_mode:* One of the accepted `QAbstractItemView selection modes <https://doc.qt.io/qtforpython/PySide2/QtWidgets/QAbstractItemView.html#PySide2.QtWidgets.PySide2.QtWidgets.QAbstractItemView.SelectionMode>`_
lineEdit        | *text (str):* default text in the line edit
                | *placeHolder (str):* placeholder text
                | *readOnly (bool):* set as read only
plainTextEdit   | *text (str):* default text in the text edit
                | *placeHolder (str):* placeholder text
label           | *text (str):* default text
button          | *text (str):* default text on the button
                | *checkable (bool):* whether this button is checkable
color           *Does not take any attributes*
=============   ========================================================================================

**All UI widget types outlined above take 'toolTip' as an attribute which can be used to display tooltips**
