from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.Layer import Layer
from _Framework.MixerComponent import MixerComponent
from _Framework.ModesComponent import LayerMode
from _Framework.SubjectSlot import subject_slot, subject_slot_group

from consts import *
from Colors import *

from bvalosek_common.MetronomeComponent import MetronomeComponent

from BackgroundComponent import BackgroundComponent
from ButtonElementEx import ButtonElementEx
from DeviceComponentEx import DeviceComponentEx
from MixerComponentEx import MixerComponentEx, ChannelStripComponentEx
from ModesComponentEx import ModesComponentEx
from SendsComponent import SendsComponent
from SkinDefault import make_default_skin
from SliderElementEx import SliderElementEx

def to_matrix(buttons):
    return ButtonMatrixElement(rows = [buttons])

class TwisterControlSurface(ControlSurface):

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)

        self._handle_track_change.subject = self.song().view

        with self.component_guard():
            self._skin = make_default_skin()
            self._setup_controls()
            self._setup_background()
            self._setup_device()
            self._setup_mixer()
            self._setup_modes()
            self._handle_track_change()

    @subject_slot('selected_track')
    def _handle_track_change(self):
        track = self.song().view.selected_track
        self._select_device_on_track(track)

        # only change sends if the device isnt locked -- keeps strip in sync
        # with the locked device
        if not self._device._locked_to_device:
            self._strip.set_track(track)

    def _select_device_on_track(self, track):
        if not track or not len(track.devices):
            return
        device = track.devices[0]

        # if its a drum rack without macros, try to set the device to chain
        # instead in order to have the focus be on the selected / last played
        # pad's chain
        rack = device.can_have_drum_pads
        if rack and not device.has_macro_mappings and len(device.chains) > 0:
            chain = device.view.selected_chain or device.chains[0]
            if len(chain.devices):
                device = chain.devices[0]
        self._device.set_device(device)

    def _setup_background(self):
        background = BackgroundComponent()
        background.layer = Layer(priority = -100, knobs = self._knobs, lights = self._buttons)

    def _setup_device(self):
        self._device = DeviceComponentEx()
        self._device.log = self.log_message
        self.set_device_component(self._device)

    def _setup_mixer(self):
        self._strip = ChannelStripComponentEx()
        self._mixer = MixerComponentEx(num_returns = 8)

    def _setup_controls(self):
        knobs = [ [ self._make_knob(row, col) for col in range(4) ] for row in range(4) ]
        buttons = [ [ self._make_button(row, col) for col in range(4) ] for row in range(4) ]
        self._knobs = ButtonMatrixElement(knobs)
        self._buttons = ButtonMatrixElement(buttons)

    def _make_knob(self, row, col):
        return SliderElementEx(
            msg_type = MIDI_CC_TYPE,
            channel = KNOB_CHANNEL,
            identifier = row * 4 + col)

    def _make_button(self, row, col):
        return ButtonElementEx(
            msg_type = MIDI_CC_TYPE,
            channel = BUTTON_CHANNEL,
            identifier = row * 4 + col,
            is_momentary = True,
            skin = self._skin)

    def _setup_modes(self):
        self._modes = ModesComponentEx()
        self._setup_main_mode()
        self._setup_sixteen_param_mode()
        self._setup_mixer_mode()
        self._modes.layer = Layer(priority = 10,
            main_mode_button = self._buttons.get_button(0, 0),
            sixteen_param_mode_button = self._buttons.get_button(1, 0),
            mixer_mode_button = self._buttons.get_button(2, 0))
        self._modes.selected_mode = 'main_mode'

    def _setup_main_mode(self):
        strip_layer = Layer(
            volume_control = self._knobs.get_button(3, 0),
            arm_button = self._buttons.get_button(3, 0),
            send_controls = self._knobs.submatrix[:, 1])

        mixer_layer = Layer(
            prehear_volume_control = self._knobs.get_button(0, 0),
            return_track_select_buttons = self._buttons.submatrix[:, 1])

        device_layer = Layer(
            on_off_button = self._buttons.get_button(3, 3),
            parameter_controls = self._knobs.submatrix[:, 2:],
            lock_button = self._buttons.get_button(2, 3))

        metronome_layer = Layer(lights = self._buttons.submatrix[:, 2])
        metronome = MetronomeComponent()
        metronome.log = self.log_message

        device_bg_layer = Layer(priority = -10,
            lights = self._buttons.submatrix[:, 2:])
        device_bg = BackgroundComponent(color = 'Device.Background')

        strip_mode = LayerMode(self._strip, strip_layer)
        metronome_mode = LayerMode(metronome, metronome_layer)
        device_bg_mode = LayerMode(device_bg, device_bg_layer)
        device_mode = LayerMode(self._device, device_layer)
        mixer_mode = LayerMode(self._mixer, mixer_layer)

        self._modes.add_mode('main_mode', [
            strip_mode,
            mixer_mode,
            metronome_mode,
            device_bg_mode,
            device_mode ])

    def _setup_sixteen_param_mode(self):
        device_layer = Layer(
            parameter_controls = self._knobs,
            on_off_button = self._buttons.get_button(3, 3),
            bank_buttons = self._buttons.submatrix[:3, 2:],
            bank_prev_button = self._buttons.get_button(1, 1),
            bank_next_button = self._buttons.get_button(2, 1),
            lock_button = self._buttons.get_button(3, 2))

        device_mode = LayerMode(self._device, device_layer)

        self._modes.add_mode('sixteen_param_mode', device_mode)

    def _setup_mixer_mode(self):
        strip_layer = Layer(
            volume_control = self._knobs.get_button(3, 0),
            arm_button = self._buttons.get_button(3, 0),
            send_controls = self._knobs.submatrix[:, 2:])

        mixer_layer = Layer(
            return_track_select_buttons = self._buttons.submatrix[:, 2:])

        strip_mode = LayerMode(self._strip, strip_layer)
        mixer_mode = LayerMode(self._mixer, mixer_layer)

        self._modes.add_mode('mixer_mode', [ strip_mode, mixer_mode ])

