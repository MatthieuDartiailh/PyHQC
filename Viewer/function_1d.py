# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 17:12:56 2013

@author: Matthieu
"""

from traits.api import HasTraits, Str, Float

class Abstract1DFunction(HasTraits):
    """
    """
    name = Str('Name displayed in the list of the function applier')

    def process(self, data):
        """
        """
        raise NotImplementedError('You must implement a process method\n\
                                    see Abstract1DFunction')

    def update(self, data):
        """
        """
        raise NotImplementedError('You must implement an update method\n\
                                    see Abstract1DFunction')

class Normalise(Abstract1DFunction):
    """
    """
    name = 'Normalise'
    min_value = Float
    max_value = Float

    def process(self, data):
        """
        """
        min_val = data.min()
        max_val = data.max()
        norm = (max_val-min_val)

        self.min_value = min_val
        self.max_value = max_val

        #In place modification of the array
        data -= min_val
        data *= 2
        data /= norm
        data -= 1

        return data

    def update(self, update):
        """
        """
        max_up = max(update)
        min_up = min(update)
        if max_up > self.max_value:
            self.max_value = max_up
        if min_up < self.min_value:
            self.min_value = min_up

        norm = self.max_value - self.min_value

        #In place modification of the array
        update -= self.min_value
        update *= 2
        update /= norm
        update -= 1

        return update

FUNCTIONS_1D = ['Normalise']