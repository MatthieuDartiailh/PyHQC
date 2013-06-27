"""===========================================================================
module : float_display.py
author : Matthieu DARTIAILH
purpose : Define the class FloatDisplay packing tools for displaying
          floating points number with proper formatting and handling
          user input.
          Number of digits for the display can range from 0 to 8, format
          can be either auto (ie scientific for number with more than four
          digits), decimal, or scientific.
          reaction to user input should connected to the user input Event.


 last modified on : 2013/02/22
=========================================================================="""

# Use qt toolkit rather than wxWidget if another backend has not been set
# first
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig is None:
    ETSConfig.toolkit = "qt4"

#Loading Traits and Traitsui modules
from traits.api import Float, Str, Range,\
                        Event, Enum, on_trait_change
from traitsui.api import View, UItem, TextEditor

from has_preference_traits import HasPreferenceTraits

class FloatDisplay(HasPreferenceTraits):
    """Tool class for floatting points display
    """
    #Actual value being stored
    value = Float()
    display = Str('0.0')
    format = Str('g')
    digits = Range(low = 0, high = 8, value = 4, mode = 'spinner',
                   preference = 'async')
    user_input = Event()
    format_enum = Enum('Auto','Decimal','Scientific', preference = 'async')

    traits_view = View(UItem('display', editor=TextEditor(auto_set = False) ),
                    resizable = True)

    def __init__(self,value = 0, format = None,
                    digits = None, style = 'simple', **kwargs):
        super(FloatDisplay, self).__init__(**kwargs)

        self.value = value
        if format is not  None:
            self.format = format
        if digits is not None:
            self.digits = digits

        self.preference_init()

    @on_trait_change('value, format, digits')
    def float_format(self,name):
        if self.value is None:
            self.display = 'NaN'
        self.display =  ('{: 0.'+str(self.digits)+self.format+'}').format(self.value)

    @on_trait_change('display')
    def user(self,object,name,new):
        if float(new) != self.value:
            self.user_input = float(new)

    @on_trait_change('format_enum')
    def update_format(self):
        if self.format_enum == 'Auto':
            self.format = 'g'
        elif self.format_enum == 'Decimal':
            self.format = 'f'
        else:
            self.format = 'e'

if __name__ == "__main__":
    a = FloatDisplay(100,'f',6, 'readonly')
    a.digits = 5
    a.format = 'e'
    a.configure_traits()