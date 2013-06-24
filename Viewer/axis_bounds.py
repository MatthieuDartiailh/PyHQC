from traits.api\
    import HasTraits, Set, Int, Float,Bool,\
            on_trait_change

class AxisBounds(HasTraits):

    values = Set
    min = Float
    max = Float
    max_data = Float
    length = Int
    new_length = Bool

    def __init__(self, val = None):
        super(AxisBounds, self).__init__()
        if val is not None:
            self.set(val)

    def append(self, list):
        self.values.update(set(list))
        self.min = min(self.values)
        self.max_data = max(self.values)

    def set(self, val):
        self.values = set(val)
        self.min = min(self.values)
        self.max_data = max(self.values)

    @on_trait_change('values')
    def update_len(self):
        aux = len(self.values)
        if aux != self.length:
            self.length = aux
            self.new_length = True

    @on_trait_change('max_data')
    def update_max(self):
        if self.length != 1:
            aux = (self.max_data - self.min)/(self.length-1)
        else:
            aux = 0
        self.max = self.max_data + aux

