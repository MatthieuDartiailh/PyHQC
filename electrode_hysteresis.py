from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import HasTraits, Float, CFloat, Instance,\
        Int, Button, Str, on_trait_change
from traitsui.api\
    import View, Item, HGroup, VGroup, UItem,\
        TextEditor, Spring, Label, Heading
from chaco.api import Plot, ArrayPlotData
from enable.component_editor\
    import ComponentEditor
from numpy import linspace, mod, array, cos
from scipy import optimize

from math import pi as Pi
import math

def stoner_free_energy(phi,theta,field,inv_coercion_field):
    return -0.25*math.cos(2*(phi-theta)) - field*inv_coercion_field*cos(phi)


class ElectrodeHysteresis(HasTraits):

    coercitive_field1 = Float(0.01)
    easy_axis_angle1 = Float(0)
    easy_axis_angle_input1 = Str('0')
    
    coercitive_field2 = Float(0.01)
    easy_axis_angle2 = Float(0)
    easy_axis_angle_input2 = Str('0')
    
    field_min = Float(-0.015)
    field_max = Float(0.015)
    points = Int(1000)
    
    data1 = Instance(ArrayPlotData)
    plot1 = Instance(Plot)
    data2 = Instance(ArrayPlotData)
    plot2 = Instance(Plot)
    data_diff = Instance(ArrayPlotData)
    plot_diff = Instance(Plot)
    
    
    compute = Button('Compute')
    
    traits_view = View(
                    VGroup(
                        HGroup(
                            VGroup(
                                Item('coercitive_field1'),
                                Item('easy_axis_angle_input1',
                                    editor = TextEditor(auto_set = False,
                                        enter_set = True),
                                    ),
                                Item('easy_axis_angle1', style = 'readonly'),
                                show_border = True,
                                label = 'Electrode 1',
                                ),
                            VGroup(
                                Item('coercitive_field2'),
                                Item('easy_axis_angle_input2',
                                    editor = TextEditor(auto_set = False,
                                        enter_set = True),
                                    ),
                                Item('easy_axis_angle2', style = 'readonly'),
                                show_border = True,
                                label = 'Electrode 2',
                                ),
                            ),
                        HGroup(
                            Item('field_min'),
                            Item('field_max'),
                            Item('points'),
                            ),
                        HGroup(
                            Spring(),
                            Heading('Increasing = blue, decreasing = red'),
                            Spring(),
                            UItem('compute'),
                            ),
                        HGroup(
                            UItem('plot1', editor = ComponentEditor()),
                            UItem('plot2', editor = ComponentEditor()),
                            UItem('plot_diff', editor = ComponentEditor()),
                            ),
                    ),
                )
                    
    def __init__(self):
        
        super(ElectrodeHysteresis,self).__init__()
        self.data1 = ArrayPlotData()
        self.plot1 = Plot(self.data1,title = 'Electrode 1')
        self.plot1.padding = (80,10,20,40)
        
        self.data2 = ArrayPlotData()
        self.plot2 = Plot(self.data2,title = 'Electrode 2')
        self.plot2.padding = (80,10,20,40)
        
        self.data_diff = ArrayPlotData()
        self.plot_diff = Plot(self.data_diff,title = 'Current')
        self.plot_diff.padding = (80,10,20,40)
        
        dummy_x = linspace(0,10,1000)
        dummy_y1 = 0*dummy_x
        dummy_y2 = 0*dummy_x
        
        self.data1.set_data('x',dummy_x)
        self.data1.set_data('y1',dummy_y1)
        self.data1.set_data('y2',dummy_y2)
        self.plot1.plot(('x','y1'),color = 'blue')
        self.plot1.plot(('x','y2'),color = 'red')
        
        self.data2.set_data('x',dummy_x)
        self.data2.set_data('y1',dummy_y1)
        self.data2.set_data('y2',dummy_y2)
        self.plot2.plot(('x','y1'),color = 'blue')
        self.plot2.plot(('x','y2'),color = 'red')
        
        self.data_diff.set_data('x',dummy_x)
        self.data_diff.set_data('y1',dummy_y1)
        self.data_diff.set_data('y2',dummy_y2)
        self.plot_diff.plot(('x','y1'),color = 'blue')
        self.plot_diff.plot(('x','y2'),color = 'red')
    
    def _compute_fired(self):
        
        self.data1.set_data('x',linspace(self.field_min,self.field_max,self.points))
        self.data2.set_data('x',linspace(self.field_min,self.field_max,self.points))
        self.data_diff.set_data('x',linspace(self.field_min,self.field_max,self.points))
        
        inv_field_coercion1 = 1/self.coercitive_field1
        phi1 = 0
        phi1_incr = []
        phi1_decr = []
        
        inv_field_coercion2 = 1/self.coercitive_field2
        phi2 = 0
        phi2_incr = []
        phi2_decr = []
        
        for field in linspace(0, self.field_max, self.points/2):
            
            def min_stoner1(phi):
                return stoner_free_energy(phi, self.easy_axis_angle1,field,inv_field_coercion1)
            
            def min_stoner2(phi):
                return stoner_free_energy(phi, self.easy_axis_angle2,field,inv_field_coercion2)
            
            phi1 = optimize.fmin(min_stoner1,[phi1],disp = False)
            phi2 = optimize.fmin(min_stoner2,[phi2],disp = False)
            
        for field in linspace(self.field_max, self.field_min, self.points):
            
            def min_stoner1(phi):
                return stoner_free_energy(phi, self.easy_axis_angle1,field,inv_field_coercion1)
            
            def min_stoner2(phi):
                return stoner_free_energy(phi, self.easy_axis_angle2,field,inv_field_coercion2)
            
            phi1 = optimize.fmin(min_stoner1,[phi1],disp = False)
            phi1_decr.append(float(phi1)%(2*Pi))
            phi2 = optimize.fmin(min_stoner2,[phi2],disp = False)
            phi2_decr.append(float(phi2)%(2*Pi))
            
        for field in linspace(self.field_min, self.field_max, self.points):
            
            def min_stoner1(phi):
                return stoner_free_energy(phi, self.easy_axis_angle1,field,inv_field_coercion1)
            
            def min_stoner2(phi):
                return stoner_free_energy(phi, self.easy_axis_angle2,field,inv_field_coercion2)
            
            phi1 = optimize.fmin(min_stoner1,[phi1],disp = False)
            phi1_incr.append(float(phi1)%(2*Pi))
            phi2 = optimize.fmin(min_stoner2,[phi2],disp = False)
            phi2_incr.append(float(phi2)%(2*Pi))
        
        phi1_decr.reverse()
        phi2_decr.reverse()
        
        phi_diff_incr = cos(array(phi1_incr)-array(phi2_incr))
        phi_diff_decr = cos(array(phi1_decr)-array(phi2_decr))
        
        self.data1.set_data('y1',phi1_incr)
        self.data1.set_data('y2',phi1_decr)
        self.plot1.value_range.low_setting = 'auto'
        self.plot1.value_range.high_setting = 'auto'
        
        self.data2.set_data('y1',phi2_incr)
        self.data2.set_data('y2',phi2_decr)
        self.plot2.value_range.low_setting = 'auto'
        self.plot2.value_range.high_setting = 'auto'
        
        self.data_diff.set_data('y1',phi_diff_incr)
        self.data_diff.set_data('y2',phi_diff_decr)
        self.plot_diff.value_range.low_setting = 'auto'
        self.plot_diff.value_range.high_setting = 'auto'
        
    @on_trait_change('easy_axis_angle_input1')
    def new_value1(self,new):
        self.easy_axis_angle1 = eval(new)
        
    @on_trait_change('easy_axis_angle_input2')
    def new_value2(self,new):
        self.easy_axis_angle2 = eval(new)
    
if __name__ == "__main__":

    plotter = ElectrodeHysteresis()
    plotter.configure_traits()
    