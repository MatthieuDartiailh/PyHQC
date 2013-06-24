"""Basic test of PyVisa with 64bits visa
"""

from visa import *

yoko = instrument("USB::0xB21::0x39::91N326143::INSTR")
yoko.write("*IDN?")
print yoko.read()