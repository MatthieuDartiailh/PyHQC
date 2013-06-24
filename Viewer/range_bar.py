from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import HasTraits, Str, Instance,\
            Bool, Button, on_trait_change

from traitsui.api\
    import View, UItem, HGroup

from chaco.api\
    import DataView


class RangeBar(HasTraits):

    x_auto_low = Button(label = 'Low')
    x_auto_high = Button(label = 'High')
    y_auto_low = Button(label = 'Low')
    y_auto_high = Button(label = 'High')
    has_color = Bool(True)
    c_auto_low = Button(label = 'Low')
    c_auto_high = Button(label = 'High')
    all_auto = Button(label = 'Auto-scale')

    x_name = Str
    y_name = Str
    c_name = Str
    plot = Instance(DataView)

    trait_view = View(
                    HGroup(
                        HGroup(
                            UItem('x_name', style = 'readonly'),
                            UItem('x_auto_low', width = -40),
                            UItem('x_auto_high', width = -40),
                            ),
                        HGroup(
                            UItem('y_name', style = 'readonly'),
                            UItem('y_auto_low', width = -40),
                            UItem('y_auto_high', width = -40),
                            ),
                        HGroup(
                            UItem('c_name', style = 'readonly'),
                            UItem('c_auto_low', width = -40),
                            UItem('c_auto_high', width = -40),
                            defined_when = 'has_color',
                            ),
                            UItem('all_auto', width = -100),                        label = 'Auto-set',
                        show_border = True,
                        )
                    )

    def __init__(self, plot, x_label = 'X', y_label = 'Y',
                        c_label = 'C'):

        super(RangeBar, self).__init__(x_name = x_label,\
                                        y_name = y_label,
                                        c_name = c_label)
        if isinstance(plot,DataView):
            self.plot = plot

            if hasattr(plot, 'color_mapper'):
                self.has_color = True
            else:
                self.has_color = False


    @on_trait_change('x_auto_low')
    def autoscale_x_low(self):
            self.plot.index_range.low_setting = 'auto'

    @on_trait_change('x_auto_high')
    def autoscale_x_high(self):
            self.plot.index_range.high_setting = 'auto'

    @on_trait_change('y_auto_low')
    def autoscale_y_low(self):
            self.plot.value_range.low_setting = 'auto'

    @on_trait_change('y_auto_high')
    def autoscale_y_high(self):
            self.plot.value_range.high_setting = 'auto'

    @on_trait_change('c_auto_low')
    def autoscale_c_low(self):
        self.plot.color_mapper.range.low_setting = 'auto'

    @on_trait_change('c_auto_high')
    def autoscale_c_high(self):
        self.plot.color_mapper.range.high_setting = 'auto'

    @on_trait_change('all_auto')
    def autoscale(self):
        self.plot.range2d.set_bounds(('auto','auto'),('auto','auto'))
        if self.has_color:
            self.plot.color_mapper.range.set_bounds('auto','auto')

if __name__ == "__main__":
    RangeBar(None).configure_traits()