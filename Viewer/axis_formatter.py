"""
"""
# Use qt toolkit rather than wxWidget if another backend has not been set
# first
from traits.etsconfig.etsconfig import ETSConfig
if ETSConfig is None:
    ETSConfig.toolkit = "qt4"

#Loading Traits and Traitsui modules
from traits.api import  Str, Range, Enum, on_trait_change

from has_preference_traits import HasPreferenceTraits

class AxisFormatter(HasPreferenceTraits):
    """Tool class for axis tick label formatting
    """

    display = Str('0.0')
    format = Str('g', preference = 'async')
    digits = Range(low = 0, high = 8, value = 4, mode = 'spinner',
                   preference = 'async')

    format_enum = Enum('Auto','Decimal','Scientific')

    def __init__(self, format = None,
                    digits = None, **kwargs):
        super(AxisFormatter, self).__init__(**kwargs)

        if format is not  None:
            self.format = format
        if digits is not None:
            self.digits = digits

        self.preference_init()

    def float_format(self, value):
        """
        """
        return ('{: 0.'+str(self.digits)+self.format+'}').format(value)

    @on_trait_change('format_enum')
    def update_format(self):
        """
        """
        if self.format_enum == 'Auto':
            self.format = 'g'
        elif self.format_enum == 'Decimal':
            self.format = 'f'
        else:
            self.format = 'e'