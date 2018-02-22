#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007


Define a family of algorithms, encapsulate each one, and make them
interchangeable. Strategy lets the algorithm vary independently from
clients that use it.
"""

import abc
import numpy as np

class Context:  # This would be class SignalOperations
    """
    Define the interface of interest to clients.
    Maintain a reference to a Strategy object.
    """

    def __init__(self, strategy):
        self._strategy = strategy

    def context_interface(self, signal, *args, **kwargs):
        return self._strategy.algorithm_interface(signal, args, kwargs)
        
#        print(args)
#        print(kwargs)


class Strategy(metaclass=abc.ABCMeta):  # This would be class algorithms
    """
    Declare an interface common to all supported algorithms. Context
    uses this interface to call the algorithm defined by a
    ConcreteStrategy.
    """
    def __init__(self):
        self.points = False
        
#    @classmethod
    @abc.abstractmethod
    def algorithm_interface(self):
        if self.points:
            print('points!')
        return self.result

class ConcreteStrategyA(Strategy):  # Savitzky-Golay filter for example
    """
    Implement the algorithm using the Strategy interface.
    """
    def algorithm_interface(self, signal,  *args):
        kwargs = args[1]
        args = args[0]
        print('Doing algorithm A with signal: ' + str(signal) + ', additional args '+ str(args) + ', and kwargs ' + str(kwargs))
        self.result = np.sin(signal)
        return super(ConcreteStrategyA, self).algorithm_interface()
    
class ConcreteStrategyB(Strategy):  # Get the derivative for example
    """
    Implement the algorithm using the Strategy interface.
    """
    def algorithm_interface(self, signal,  *args):
        kwargs = args[1]
        args = args[0]
        print('Doing algorithm B with signal: ' + str(signal) + ', additional args '+ str(args) + ', and kwargs ' + str(kwargs))
        self.result = np.cos(signal)
        return super(ConcreteStrategyB, self).algorithm_interface()
    
class get_zero_crossings(Strategy):
    def algorithm_interface(self, signal, *args):
        kwargs = args[1]
        args = args[0]
        print('Doing get_zero_crossings  with signal: ' + str(signal) + ', additional args '+ str(args) + ', and kwargs ' + str(kwargs))
        self.result = np.tan(signal)
        self.points = True
        return super(get_zero_crossings, self).algorithm_interface()

def main():
    concrete_strategy_a = ConcreteStrategyA()
    context = Context(concrete_strategy_a)
    sig = np.array([100,200,300])
    
    # Using StrategyA
    processed = context.context_interface(sig, 'pos_arg1', 'pos_arg2', keyarg1='karg1', keyarg2='karg2')
    print(processed)
    
    # Using StrategyB
    context = Context(ConcreteStrategyB())
    processed = context.context_interface(sig, 'B_pos_arg1', Bkeyarg1='B_karg1', Bkeyarg2='B_karg2')
    print(processed)
    
    # Iterate StrategyB again
    context = Context(get_zero_crossings())
    processed = context.context_interface(processed, 'G_pos_arg1', Gkeyarg1='G_karg1', Gkeyarg2='G_karg2')
    print(processed)

if __name__ == "__main__":
    main()
