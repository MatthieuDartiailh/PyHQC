from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig.toolkit is '':
    ETSConfig.toolkit = "qt4"

from traits.api\
    import (HasTraits, Float, Instance, Int, Button, Str, Bool, on_trait_change)
from traitsui.api\
    import (View, Item, HGroup, VGroup, UItem, TextEditor, Spring, Heading,
            Label)
from chaco.api import Plot, ArrayPlotData
from enable.component_editor import ComponentEditor
from numpy import linspace, array, cos, mod, sqrt, sin
from scipy import optimize

from math import pi as Pi
import math

def stoner_free_energy(phi,theta,field,inv_coercion_field):
    return -0.25*math.cos(2*(phi-theta)) - field*inv_coercion_field*cos(phi)

def energy_dqd(t,delta,theta,epsilon1):
    return sqrt((delta*sin(theta/2))**2 + (delta*cos(theta/2) + epsilon1*t)**2)

def kappa(t,delta,theta,epsilon1,epsilon2):
    return ( energy_dqd(t,delta,theta,epsilon1) +\
            epsilon2*(t + epsilon1*delta*cos(theta/2)))

class ElectrodeHysteresis(HasTraits):

    coercitive_field1 = Float(0.01)
    easy_axis_angle1 = Float(0)
    easy_axis_angle_input1 = Str('0')

    coercitive_field2 = Float(0.02)
    easy_axis_angle2 = Float(0)
    easy_axis_angle_input2 = Str('Pi/6')

    field_min = Float(-0.015)
    field_max = Float(0.015)
    points = Int(1000)

    cavity_freq = Float(6.7)
    cavity_quality = Float(3500)
    dqd_ready = Bool(False)
    dqd_t = Float(6.2)
    dqd_coupling = Float(10)
    dqd_delta = Float(3)
    dqd_gamma12 = Float(0.1)
    dqd_gamma13 = Float(0.1)
    lande = Float(28)

    data1 = Instance(ArrayPlotData)
    plot1 = Instance(Plot)
    data2 = Instance(ArrayPlotData)
    plot2 = Instance(Plot)
    data_diff = Instance(ArrayPlotData)
    plot_diff = Instance(Plot)
    data_g = Instance(ArrayPlotData)
    plot_g = Instance(Plot)


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
                        HGroup(
                            VGroup(
                                HGroup(Item('cavity_freq'),Label('GHz')),
                                Item('cavity_quality'),
                                HGroup(Item('dqd_t'),Label('GHz')),
                                HGroup(Item('dqd_coupling'),Label('MHz')),
                                HGroup(Item('dqd_delta'),Label('GHz')),
                                HGroup(Item('dqd_gamma12'),Label('GHz')),
                                HGroup(Item('dqd_gamma13'),Label('GHz')),
                                HGroup(Item('lande', style = 'readonly'),
                                       Label('GHz/T')),
                                ),
                            UItem('plot_g', editor = ComponentEditor()),
                            ),
                    ),
                resizable = True,
                )

    def __init__(self):

        super(ElectrodeHysteresis,self).__init__()
        self.new_value1(self.easy_axis_angle_input1)
        self.new_value2(self.easy_axis_angle_input2)

        self.data1 = ArrayPlotData()
        self.plot1 = Plot(self.data1,title = 'Electrode 1')
        self.plot1.padding = (80,10,20,40)
        self.plot1.index_axis.title = 'Field (mT)'
        self.plot1.value_axis.title = 'Orientation (rad)'

        self.data2 = ArrayPlotData()
        self.plot2 = Plot(self.data2,title = 'Electrode 2')
        self.plot2.padding = (80,10,20,40)
        self.plot2.index_axis.title = 'Field (mT)'
        self.plot2.value_axis.title = 'Orientation (rad)'

        self.data_diff = ArrayPlotData()
        self.plot_diff = Plot(self.data_diff,title = 'Current')
        self.plot_diff.padding = (80,10,20,40)
        self.plot_diff.index_axis.title = 'Field (mT)'
        self.plot_diff.value_axis.title = 'Current (a.u.)'

        self.data_g = ArrayPlotData()
        self.plot_g = Plot(self.data_g,title = 'DQD response')
        self.plot_g.padding = (80,10,20,40)
        self.plot_g.index_axis.title = 'Field (mT)'
        self.plot_g.value_axis.title = 'Phase contrast (rad)'

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

        self.data_g.set_data('x',dummy_x)
        self.data_g.set_data('y1',dummy_y1)
        self.data_g.set_data('y2',dummy_y2)
        self.plot_g.plot(('x','y1'),color = 'blue')
        self.plot_g.plot(('x','y2'),color = 'red')

    def _compute_fired(self):

        self.data1.set_data('x',
                            linspace(self.field_min,self.field_max,self.points))
        self.data2.set_data('x',
                            linspace(self.field_min,self.field_max,self.points))
        self.data_diff.set_data('x',
                            linspace(self.field_min,self.field_max,self.points))
        self.data_g.set_data('x',
                            linspace(self.field_min,self.field_max,self.points))

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
            del min_stoner1
            del min_stoner2

        for field in linspace(self.field_max, self.field_min, self.points):

            def min_stoner1(phi):
                return stoner_free_energy(phi, self.easy_axis_angle1,field,inv_field_coercion1)

            def min_stoner2(phi):
                return stoner_free_energy(phi, self.easy_axis_angle2,field,inv_field_coercion2)

            phi1 = optimize.fmin(min_stoner1,[phi1],disp = False)
            phi1_decr.append(float(phi1)%(2*Pi))
            phi2 = optimize.fmin(min_stoner2,[phi2],disp = False)
            phi2_decr.append(float(phi2)%(2*Pi))
            del min_stoner1
            del min_stoner2

        for field in linspace(self.field_min, self.field_max, self.points):

            def min_stoner1(phi):
                return stoner_free_energy(phi, self.easy_axis_angle1,field,inv_field_coercion1)

            def min_stoner2(phi):
                return stoner_free_energy(phi, self.easy_axis_angle2,field,inv_field_coercion2)

            phi1 = optimize.fmin(min_stoner1,[phi1],disp = False)
            phi1_incr.append(float(phi1)%(2*Pi))
            phi2 = optimize.fmin(min_stoner2,[phi2],disp = False)
            phi2_incr.append(float(phi2)%(2*Pi))
            del min_stoner1
            del min_stoner2

        phi1_decr.reverse()
        phi2_decr.reverse()

        phi_diff_incr = array(phi1_incr)-array(phi2_incr)
        phi_diff_decr = array(phi1_decr)-array(phi2_decr)

        self.data1.set_data('y1',phi1_incr)
        self.data1.set_data('y2',phi1_decr)
        self.plot1.value_range.low_setting = 'auto'
        self.plot1.value_range.high_setting = 'auto'

        self.data2.set_data('y1',phi2_incr)
        self.data2.set_data('y2',phi2_decr)
        self.plot2.value_range.low_setting = 'auto'
        self.plot2.value_range.high_setting = 'auto'

        self.data_diff.set_data('y1',cos(phi_diff_incr))
        self.data_diff.set_data('y2',cos(phi_diff_decr))
        self.plot_diff.value_range.low_setting = 'auto'
        self.plot_diff.value_range.high_setting = 'auto'

        self.data_g.set_data('aux1', mod(phi_diff_incr, Pi))
        self.data_g.set_data('aux2', mod(phi_diff_decr, Pi))
        self.dqd_ready = True
        self.compute_dqd_answer()

    @on_trait_change('dqd_t, dqd_delta, dqd_gamma12, dqd_gamma13,dqd_coupling,\
    dqd_ready')
    def compute_dqd_answer(self):
        if self.dqd_ready:
            mag_field = self.lande*self.data_g.get_data('x')
            delta = self.dqd_delta + mag_field
            theta1 = self.data_g.get_data('aux1')
            theta2 = self.data_g.get_data('aux2')

            ener1_1 = -energy_dqd(self.dqd_t, delta, theta1, +1)
            ener1_2 = -energy_dqd(self.dqd_t, delta, theta2, +1)
            ener2_1 = -energy_dqd(self.dqd_t, delta, theta1, -1)
            ener2_2 = -energy_dqd(self.dqd_t, delta, theta2, -1)
            ener3_1 = energy_dqd(self.dqd_t, delta, theta1, -1)
            ener3_2 = energy_dqd(self.dqd_t, delta, theta2, -1)

            aux1 = delta*sin(theta1/2)
            aux2 = delta*sin(theta2/2)

            kmm_1 = kappa(self.dqd_t, delta, theta1,-1,-1)
            kmm_2 = kappa(self.dqd_t, delta, theta2,-1,-1)
            kpm_1 = kappa(self.dqd_t, delta, theta1,+1,-1)
            kpm_2 = kappa(self.dqd_t, delta, theta2,+1,-1)
            kmp_1 = kappa(self.dqd_t, delta, theta1,-1,+1)
            kmp_2 = kappa(self.dqd_t, delta, theta2,-1,+1)

            g12_1 = (aux1*kmm_1 + aux1*kpm_1)/\
                sqrt((aux1**2+kmm_1**2)*(aux1**2+kpm_1**2))
            g12_2 = (aux2*kmm_2 + aux2*kpm_2)/\
                sqrt((aux2**2+kmm_2**2)*(aux2**2+kpm_2**2))
            g13_1 = (aux1*kpm_1 - aux1*kmp_1)/\
                sqrt((aux1**2+kmp_1**2)*(aux1**2+kpm_1**2))
            g13_2 = (aux2*kpm_2 - aux2*kmp_2)/\
                sqrt((aux2**2+kmp_2**2)*(aux2**2+kpm_2**2))

            detun12_1 = ener2_1-ener1_1-self.cavity_freq
            detun12_2 = ener2_2-ener1_2-self.cavity_freq
            detun13_1 = ener3_1-ener1_1-self.cavity_freq
            detun13_2 = ener3_2-ener1_2-self.cavity_freq

            dqd_response_1 = detun12_1*g12_1**2/\
                                (detun12_1**2 + self.dqd_gamma12**2) +\
                            detun13_1*g13_1**2/\
                                (detun13_1**2 + self.dqd_gamma13**2)
            dqd_response_2 = detun12_2*g12_2**2/\
                                (detun12_2**2 + self.dqd_gamma12**2) +\
                            detun13_2*g13_2**2/\
                                    (detun13_2**2 +self.dqd_gamma13**2)

            dqd_response_1 *= 2*self.cavity_quality/self.cavity_freq*\
                                                    self.dqd_coupling**2/1000000
            dqd_response_2 *= 2*self.cavity_quality/self.cavity_freq*\
                                                    self.dqd_coupling**2/1000000

            self.data_g.set_data('y1', dqd_response_1)
            self.data_g.set_data('y2', dqd_response_2)


    @on_trait_change('easy_axis_angle_input1')
    def new_value1(self,new):
        self.easy_axis_angle1 = eval(new)

    @on_trait_change('easy_axis_angle_input2')
    def new_value2(self,new):
        self.easy_axis_angle2 = eval(new)

if __name__ == "__main__":

    plotter = ElectrodeHysteresis()
    plotter.configure_traits()
