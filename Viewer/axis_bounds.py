#==============================================================================
# module : axis_bounds.py
# author : Matthieu Dartiailh
#==============================================================================
"""Implementation of a commodity class for computing axis bounds from set of
data

This module defines a single class AxisBounds.
"""

from traits.api\
    import HasTraits, Set, Int, Float,Bool

class AxisBounds(HasTraits):
    """
    Commodity class computing the axis bounds

    This class is used to compute and update axis bounds from a numpy array.

    Parameters
    ----------
    val : iterable
        Initial value of the array used to build the axis bounds

    Methods
    -------
    append(iterable)
        Append the list to the existing set of data and update the min, max, and
        length of the set if necessary
    set(iterable)
        Create or replace the set of values using the iterable and compute the
        min, max, and length for the axis bounds
    """

    #==========================================================================
    # Public properties
    #==========================================================================
    values = Set
    min = Float
    max = Float
    max_data = Float
    length = Int

    #==========================================================================
    # Public method
    #==========================================================================
    def __init__(self, val = None):
        super(AxisBounds, self).__init__()
        if val is not None:
            self.set(val)

    def append(self, update_list):
        """Method called to update the axis bounds

        This method is to be called when the data used to compute the axis
        bounds is updated. The new value only should be passed to this method.

        Parameters
        ----------
        update_list : iterable
            Values appended to the data used to compute the axis bounds

        Returns
        -------
        none
        """
        self.values.update(set(update_list))
        self._update()

    def set(self, val):
        """Method call to set or replace the data used to compute the bounds


        """
        self.values = set(val)
        self._update()

    #==========================================================================
    # Private methods
    #==========================================================================
    def _update(self):
        """
        """
        update_needed = False
        aux = len(self.values)
        if aux != self.length:
            self.length = aux
            update_needed = True
        aux = min(self.values)
        if aux != self.min:
            self.min = aux
            update_needed = True
        aux = max(self.values)
        if aux != self.max_data:
            self.max_data = aux
            update_needed = True
        if update_needed:
            self._update_max()

    def _update_max(self):
        """
        """
        if self.length != 1:
            aux = (self.max_data - self.min)/(self.length-1)
        else:
            aux = 0
        self.max = self.max_data + aux

