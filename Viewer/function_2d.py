# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 22:00:35 2013

@author: Matthieu
"""

from traits.api import HasTraits, Int, Str, Float

class Abstract2DFunction(HasTraits):
    """
    """
    name = Str('Name displayed in the list of the function applier')

    def process(self, data):
        """
        """
        raise NotImplementedError('You must implement a process method\n\
                                    see Abstract2DFunction')

    def pre_update(self, data):
        """
        """
        return data

    def update(self, data):
        """
        """
        raise NotImplementedError('You must implement an update method\n\
                                    see Abstract2DFunction')

class NormalisePerSweep(Abstract2DFunction):
    """
    """
    name = 'Normalise'
    last_sweep = Int
    last_min = Float
    last_max = Float
    data_order = Str

    def process(self, data):
        """
        """
        min_per_sweep = data.min(axis = 0)
        max_per_sweep = data.max(axis = 0)
        norm_list = (max_per_sweep-min_per_sweep)

        self.last_min = min_per_sweep[-1]
        self.last_max = max_per_sweep[-1]
        self.last_sweep = len(norm_list)-1

        #In place modification of the array
        data -= min_per_sweep
        data *= 2
        data /= norm_list
        data -= 1

        return data

    def pre_update(self, data):
        """
        """
        #This is a view any change to it will affect data
        data_to_denormalise = data[-1]

        #In place modification of the array
        data_to_denormalise += 1
        data_to_denormalise *= (self.last_max - self.last_min)
        data_to_denormalise /= 2
        data_to_denormalise += self.last_min

        return data

    def update(self, data):
        """
        """
        #This is a view any change to it will affect data
        data_to_normalise = data[self.last_sweep::]

        min_per_sweep = data_to_normalise.min(axis = 0)
        max_per_sweep = data_to_normalise.max(axis = 0)
        norm_list = (max_per_sweep-min_per_sweep)

        self.last_min = min_per_sweep[-1]
        self.last_max = max_per_sweep[-1]
        self.last_sweep += len(norm_list)-1

        #In place modification of the array
        data_to_normalise -= min_per_sweep
        data_to_normalise *= 2
        data_to_normalise /= norm_list
        data_to_normalise -= 1

        return data

FUNCTIONS_2D = ['NormalisePerSweep']