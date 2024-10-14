import time
from threading import Thread

import piplates.DAQCplate as Daq
import piplates.RELAYplate as Rly


# DAQ Inputs
def get_daq_input(bit,channel=1,invert=False):
    value = bool(Daq.getDINbit(channel, bit))
    return value


# DAQ Input Aliases
def Prendido(): return get_daq_input(bit=0)

def Rollo_maestro_sujetado(): return get_daq_input(bit=1)

def Rollo_maestro_soltado(): return get_daq_input(bit=2)

def Longitud_medida(): return get_daq_input(3)

def Tapa_rollos():  return get_daq_input(4)

def Hay_cartones(): return get_daq_input(5)

def Rollo_soltado(): return get_daq_input(6)

def Medido_largo(): return get_daq_input(7)


# State Class to Track Output State
class SystemState:
    def __init__(self):
        self.rodajas_cerradas = False
        self.brazos_acercados = False
        self.motor_prendido = False
        self.cortar = False
        self.espreas = False
        self.rollo_maestro_rodajas = False
        self.rollo_maestro_acercado = False


state = SystemState()  # Initialize the system state


# Base Thread Class
class BaseThread(Thread):
    def __init__(self, state, dout_bit, sleep_entrada=5,sleep_salida=5):
        Thread.__init__(self)
        self.state = state
        self.dout_bit = dout_bit  # The DAQ output bit to control
        self.daemon = True
        self.sleep_entrada=sleep_entrada
        self.sleep_salida=sleep_salida

    def check_on_conditions(self):
        """To be implemented by subclasses: Checks whether the 'on' conditions are met."""
        raise NotImplementedError

    def check_off_conditions(self):
        """To be implemented by subclasses: Checks whether the 'off' conditions are met."""
        raise NotImplementedError

    def run(self):
        try:
            while Prendido():
                if self.check_on_conditions():
                    Daq.setDOUTbit(1, self.dout_bit)
                    time.sleep(self.sleep_entrada)
                    self.set_state(True)

                if self.check_off_conditions():
                    Daq.clrDOUTbit(1, self.dout_bit)
                    time.sleep(self.sleep_salida)
                    self.set_state(False)
        finally:
            if not Prendido():
                Daq.clrDOUTbit(1, self.dout_bit)

    def set_state(self, state_value):
        """Update the specific state variable. To be implemented by subclasses."""
        raise NotImplementedError


# Rodajas Thread
class RodajasThread(BaseThread):
    def __init__(self, state,dout_bit=0, sleep_entrada=5, sleep_salida=5):
        super().__init__(state, dout_bit, sleep_entrada, sleep_salida)

    def check_on_conditions(self):
        return (
            Hay_cartones()
            and not self.state.rodajas_cerradas
            and not self.state.brazos_acercados
        )

    def check_off_conditions(self):
        return (
            Rollo_soltado()
            and self.state.rodajas_cerradas
            and not self.state.brazos_acercados
        )

    def set_state(self, state_value):
        self.state.rodajas_cerradas = state_value


# Brazos Thread
class BrazosThread(BaseThread):
    def __init__(self, state,dout_bit=1):
        super().__init__(state, dout_bit)

    def check_on_conditions(self):
        return (
            self.state.rodajas_cerradas
            and not self.state.brazos_acercados
            and not self.state.motor_prendido
        )

    def check_off_conditions(self):
        return (
            Rollo_soltado()
            and self.state.brazos_acercados 
            and not self.state.motor_prendido
        )

    def set_state(self, state_value):
        self.state.brazos_acercados = state_value


# Motores Thread
class MotoresThread(BaseThread):
    def __init__(self, state,dout_bit=2):
        super().__init__(state, dout_bit)

    def check_on_conditions(self):
        return (
            Tapa_rollos()
            and not Medido_largo()
            and self.state.brazos_acercados
            and not self.state.motor_prendido
            and self.state.rollo_maestro_acercado
        )

    def check_off_conditions(self):
        return (
            Medido_largo()
            and self.state.motor_prendido
        )

    def set_state(self, state_value):
        self.state.motor_prendido = state_value


# Cortar Thread
class CortarThread(BaseThread):
    def __init__(self, state,dout_bit=3):
        super().__init__(state, dout_bit)

    def check_on_conditions(self):
        return (
            Rollo_soltado()
            and Medido_largo()
            and not self.state.brazos_acercados
            and not self.state.motor_prendido
            and not self.state.cortar
        )

    def check_off_conditions(self):
        return self.state.cortar

    def set_state(self, state_value):
        self.state.cortar=state_value

class Espreas(BaseThread):
    def __init__(self, state,dout_bit=4):
        super().__init__(state, dout_bit)

    def check_on_conditions(self):
        return (
            self.state.rodajas_cerradas
            and not self.state.espreas
        )

    def check_off_conditions(self):
        return self.state.espreas

    def set_state(self, state_value):
        self.state.espreas=state_value
 
class Rodajas_Rollo_Maestro(BaseThread):
    def __init__(self, state,dout_bit=5):
        super().__init__(state, dout_bit)

    def check_on_conditions(self):
        return (
            Rollo_maestro_sujetado()
            and not self.state.rollo_maestro_rodajas
            and not self.state.rollo_maestro_acercado
        )

    def check_off_conditions(self):
        return (
            self.state.rollo_maestro_rodajas
            and not self.state.rollo_maestro_acercado
        )

    def set_state(self, state_value):
        self.state.rollo_maestro_rodajas=state_value

class Acercar_Rollo_Maestro(BaseThread):
    def __init__(self, state,dout_bit=6):
        super().__init__(state, dout_bit)

    def check_on_conditions(self):
        return (
            Rollo_maestro_sujetado()
        and Tapa_rollos()    
        and self.state.rollo_maestro_rodajas
        and not self.state.rollo_maestro_acercado
        )

    def check_off_conditions(self):
        return (
        Rollo_maestro_soltado()
        and not self.state.motor_prendido
        and self.state.rollo_maestro_acercado
        )
    def set_state(self, state_value):
        self.state.rollo_maestro_acercado=state_value

def main():
    state = SystemState()

    threads = [
        RodajasThread(state,dout_bit=0,sleep_entrada=1),
        BrazosThread(state,dout_bit=1),
        MotoresThread(state,dout_bit=2),
        CortarThread(state,dout_bit=3),
        Espreas(state,dout_bit=4),
        Rodajas_Rollo_Maestro(state,dout_bit=5),
        Acercar_Rollo_Maestro(state,dout_bit=6)
    ]

    for thread in threads:
        thread.start()


if __name__ == "__main__":
    main()
