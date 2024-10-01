import piplates.RELAYplate as Rly
import piplates.DAQCplate as Daq
import time
from threading import Thread

# Constants
SLEEP = 5  # Sleep duration for actions

# DAQ Inputs
def get_daq_input(channel, bit, invert=False):
    value = bool(Daq.getDINbit(channel, bit))
    return not value if invert else value

# DAQ Input Aliases
def Prendido(): return get_daq_input(1, 0, invert=True)
def Hay_cartones(): return get_daq_input(1, 1, invert=True)
def Medido_largo(): return get_daq_input(1, 2, invert=True)
def Tapa_rollos(): return get_daq_input(1, 3, invert=True)
def Longitud_medida(): return get_daq_input(1, 4, invert=True)
def Rollo_soltado(): return get_daq_input(1, 5, invert=True)
def Rollo_maestro_sujetado(): return get_daq_input(1, 6)
def Rollo_maestro_soltado(): return get_daq_input(1, 7)

# State Class to Track Output State
class SystemState:
    def __init__(self):
        self.rodajas_cerradas = False
        self.brazos_acercados = False
        self.motor_prendido = False
        self.rollo_maestro_rodajas = False
        self.rollo_maestro_acercado = False

state = SystemState()  # Initialize the system state

# Base Thread Class
class BaseThread(Thread):
    def __init__(self, state, dout_bit):
        Thread.__init__(self)
        self.state = state
        self.dout_bit = dout_bit  # The DAQ output bit to control
        self.daemon = True

    def check_on_conditions(self):
        """To be implemented by subclasses: Checks whether the 'on' conditions are met."""
        raise NotImplementedError

    def check_off_conditions(self):
        """To be implemented by subclasses: Checks whether the 'off' conditions are met."""
        raise NotImplementedError

    def run(self):
        while Prendido():
            if self.check_on_conditions():
                Daq.setDOUTbit(1, self.dout_bit)
                time.sleep(SLEEP)
                self.set_state(True)

            if self.check_off_conditions():
                Daq.clrDOUTbit(1, self.dout_bit)
                time.sleep(SLEEP)
                self.set_state(False)

    def set_state(self, state_value):
        """Update the specific state variable. To be implemented by subclasses."""
        raise NotImplementedError

# Rodajas Thread
class RodajasThread(BaseThread):
    def __init__(self, state):
        super().__init__(state, dout_bit=0)

    def check_on_conditions(self):
        return Prendido() and Hay_cartones()

    def check_off_conditions(self):
        return not Prendido() or Rollo_soltado() or self.state.brazos_acercados

    def set_state(self, state_value):
        self.state.rodajas_cerradas = state_value

# Brazos Thread
class BrazosThread(BaseThread):
    def __init__(self, state):
        super().__init__(state, dout_bit=1)

    def check_on_conditions(self):
        return Prendido() and self.state.rodajas_cerradas and not self.state.motor_prendido

    def check_off_conditions(self):
        return not Medido_largo()

    def set_state(self, state_value):
        self.state.brazos_acercados = state_value

# Motores Thread
class MotoresThread(BaseThread):
    def __init__(self, state):
        super().__init__(state, dout_bit=2)

    def check_on_conditions(self):
        return (self.state.brazos_acercados and Tapa_rollos() and Medido_largo() 
                and self.state.rollo_maestro_acercado)

    def check_off_conditions(self):
        return not Medido_largo()

    def set_state(self, state_value):
        self.state.motor_prendido = state_value

# Cortar Thread
class CortarThread(BaseThread):
    def __init__(self, state):
        super().__init__(state, dout_bit=3)

    def check_on_conditions(self):
        return (Rollo_soltado() and not self.state.brazos_acercados 
                and not self.state.motor_prendido and not Medido_largo())

    def check_off_conditions(self):
        # No specific off conditions for the cortar thread based on provided logic
        return False

    def set_state(self, state_value):
        # This thread doesn't modify a specific state variable
        pass

def main():
    state = SystemState()

    threads = [
        RodajasThread(state),
        BrazosThread(state),
        MotoresThread(state),
        CortarThread(state)
    ]

    for thread in threads:
        thread.start()

if __name__ == "__main__":
    main()

