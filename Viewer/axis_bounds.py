"""
"""

from traits.api\
    import HasTraits, Set, Int, Float,Bool

class AxisBounds(HasTraits):
    """
    """

    values = Set
    min = Float
    max = Float
    max_data = Float
    length = Int
    compute_max = Bool

    def __init__(self, val = None):
        super(AxisBounds, self).__init__()
        if val is not None:
            self.set(val)

    def append(self, list):
        """
        """
        self.values.update(set(list))
        self._update()

    def set(self, val):
        """
        """
        self.values = set(val)
        self._update()

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

