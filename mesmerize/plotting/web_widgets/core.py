from bokeh.models import ColumnDataSource
from typing import *
import pandas
from uuid import UUID
import inspect


class BokehCallbackSignal:
    def __init__(
        self,
        dataframe: Optional[pandas.DataFrame] = None,
        source: Optional[ColumnDataSource] = None
    ):
        """

        :param dataframe: associate a DataFrame with this signal
                          ``dataframe`` is generally a superset of ``source``

        :param source:  associate a ColumnDataSource with this signal.
                        the data contained in ``source`` must be a subset of ``dataframe``.
                        ``source`` typically does not contain some columns from ``dataframe``
                        due to incompatibility of the ``ColumnDataSource`` type.
        """
        self.dataframe: Union[pandas.DataFrame] = dataframe
        self.source_data: Union[ColumnDataSource, None] = source

        self.callbacks = []
        self.callbacks_data = []

        self._pause_state = False

    def connect(self, func: callable):
        """
        Use this to just pass the new value from the widget or glyph to the callback function

        :param func:
        :return:
        """
        self.callbacks.append(func)

    def connect_data(self, func: callable, identifier: str):
        """
        Use this to pass a sub dataframe to the callback function.

        ``self.dataframe`` and

        :param func:
        :return:
        """

        self.callbacks_data.append((func, identifier))

    def disconnect(self, func: callable):
        if func in self.callbacks:
            self.callbacks.remove(func)
        elif func in self.callbacks_data:
            self.callbacks_data.remove(func)

    def pause(self):
        """
        Disable callback trigger
        """
        self._pause_state = True

    def unpause(self):
        """
        Enable callback trigger
        """
        self._pause_state = False

    def trigger(self, attr, old, val):
        """
        This function signature must have 3 and only 3 args, bokeh is very picky

        :param attr: name of the attribute

        :param old: old value of the attribute

        :param val: the index within `self.source_data` (such as from a glyph using a `ColumnDataSource`)
                    or the new value (such as from a widget)
        :type val:  Union[List[int], Any]

        :return:
        """
        if self._pause_state:
            return

        # if there are multiple values
        # such as if multiple datapoints were selected in a glyph
        if isinstance(val, list):
            if len(val) != 1:
                return

        if self.source_data is not None:
            self._trigger_callbacks_data(val)

        self._trigger_callbacks(val)

    def _trigger_callbacks(self, val: Any):
        """
        Trigger callbacks which directly take a value, such as from a widget

        :param val:
        :return:
        """
        for func in self.callbacks:
            print(f"VAL IN SIGNAL: {val}")
            if bool(inspect.signature(func).parameters):  # make sure the function takes arguments
                func(val)  # send out val directly
            else:
                func()  # else just call the function

    def _trigger_callbacks_data(self, val: List[int]):
        """
        Trigger the callbacks which take a subdataframe as the argument

        :param val: list containing a single integer, which is an index for source_data
        :return:
        """
        print(f"VAL IN SIGNAL: {val}")
        for func, identifier in self.callbacks_data:
            uid = self.source_data.data[identifier][val][0]  # get the source_data present at the `val` index
            print(uid)
            # subdataframe where the identifier UUID matches
            out = self.dataframe[self.dataframe[identifier] == uid]
            print(out.copy(deep=True))
            func(out)


class WebPlot:
    def __init__(self, *args, **kwargs):
        attrs = dir(self)
        self.signals: List[BokehCallbackSignal] = \
            [getattr(self, a) for a in attrs if isinstance(getattr(self, a), BokehCallbackSignal)]
        print("WEBPLOT INIT")
        print(self.signals)

    @classmethod
    def signal_blocker(cls, func):
        """Block callbacks, used when the plot x and y limits change due to user interaction"""
        print("***** SIGNAL BLOCKER CALLED ******")
        def fn(self, *args, **kwargs):
            print("self.signals is")
            print(self.signals)
            for signal in self.signals:
                print(f"Blocking signal {signal}")
                signal.pause()

            ret = func(self, *args, **kwargs)

            for signal in self.signals:
                signal.unpause()

            return ret
        return fn
