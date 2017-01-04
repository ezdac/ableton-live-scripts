from _Framework.ButtonElement import Color
from _Framework.Skin import Skin

from Colors import *

class Colors:
    class Background:
        Default = ColorEx(Rgb.BLUE)
        Device = ColorEx(Rgb.BLUE)
        Sends = ColorEx(Rgb.ORANGE)
        Volume = ColorEx(Rgb.PINK)

    class ModeButton:
        Main = ColorEx(Rgb.BLUE)

    class DefaultButton:
        On = ColorEx(Rgb.GREEN)
        Disabled = ColorEx(Rgb.GREEN, Brightness.LOW)
        Off = ColorEx(Rgb.OFF, Brightness.OFF)

    class Device:
        NotLocked = ColorEx(Rgb.GREEN)
        Locked = ColorEx(Rgb.PURPLE, Animation.GATE_HALF_BEAT)
        CanBank = ColorEx(Rgb.TEAL, Animation.PULSE_HALF_BEAT)
        CantBank = ColorEx(Rgb.TEAL)

def make_default_skin():
    return Skin(Colors)

