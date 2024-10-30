import time
from threading import Thread
import tkinter as tk
import time
# DAQSimulator class simulating the DAQ inputs using keyboard inputs
class DAQSimulator:
    def __init__(self, root):
        self.input_states = [False] * 8  # Simulate 8 DAQ input bits (boolean values)
        self.root = root
        self.setup_key_bindings()
        
        # Set Prendido (bit 0) to True by default
        self.input_states[0] = True  # Prendido ON by default
        #self.input_states[5] = True  # rodajas
    def setup_key_bindings(self):
        """Bind keys to DAQ input changes"""
        self.root.bind('0', lambda event: self.toggle_input(0))  # Prendido
        self.root.bind('1', lambda event: self.toggle_input(1))  # Rollo Maestro Sujetado
        self.root.bind('2', lambda event: self.toggle_input(2))  # Rollo Maestro Soltado
        self.root.bind('3', lambda event: self.toggle_input(3))  # Longitud Medida
        self.root.bind('4', lambda event: self.toggle_input(4))  # Tapa Rollos
        self.root.bind('5', lambda event: self.toggle_input(5))  # Hay Cartones
        self.root.bind('6', lambda event: self.toggle_input(6))  # Rollo Soltado
        self.root.bind('7', lambda event: self.toggle_input(7))  # Medido Largo

    def toggle_input(self, bit):
        """Toggle the state of the specified input bit"""
        self.input_states[bit] = not self.input_states[bit]
        print(f"Input {bit} toggled to {self.input_states[bit]}")  # Debugging output

    def get_input(self, bit):
        """Simulate reading the DAQ input"""
        return self.input_states[bit]

# Aliases for DAQ Inputs (simulated via keyboard events)
def Prendido(daq_simulator):
    return daq_simulator.get_input(0)

def Rollo_maestro_sujetado(daq_simulator):
    return daq_simulator.get_input(1)

def Rollo_maestro_soltado(daq_simulator):
    return daq_simulator.get_input(2)

def Longitud_medida(daq_simulator):
    return daq_simulator.get_input(3)

def Tapa_rollos(daq_simulator):
    return daq_simulator.get_input(4)

def Hay_cartones(daq_simulator):
    return daq_simulator.get_input(5)

def Rollo_soltado(daq_simulator):
    return daq_simulator.get_input(6)

def Medido_largo(daq_simulator):
    return daq_simulator.get_input(7)

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

# Base Thread Class
class BaseThread(Thread):
    def __init__(self, state, daq_simulator, dout_bit, sleep_entrada=5, sleep_salida=5):
        Thread.__init__(self)
        self.state = state
        self.daq = daq_simulator
        self.dout_bit = dout_bit
        self.sleep_entrada = sleep_entrada
        self.sleep_salida = sleep_salida
        self.daemon = True
        self.start_time = time.time()


    def check_on_conditions(self):
        """To be implemented by subclasses: Checks whether the 'on' conditions are met."""
        raise NotImplementedError

    def check_off_conditions(self):
        """To be implemented by subclasses: Checks whether the 'off' conditions are met."""
        raise NotImplementedError

    def run(self):
        try:
            while Prendido(self.daq):
                if self.check_on_conditions():
                    elapsed_time = time.time() - self.start_time
                    print(f"Output {self.dout_bit} turned ON at {elapsed_time:.2f} seconds")
                    time.sleep(self.sleep_entrada)
                    self.set_state(True)

                if self.check_off_conditions():
                    elapsed_time = time.time() - self.start_time
                    print(f"Output {self.dout_bit} turned OFF at {elapsed_time:.2f} seconds")
                    time.sleep(self.sleep_salida)
                    self.set_state(False)
                time.sleep(0.1)
        finally:
            if not Prendido(self.daq):
                print(f"Output {self.dout_bit} turned OFF (Prendido off) at {elapsed_time:.2f} seconds")

    def set_state(self, state_value):
        """Update the specific state variable. To be implemented by subclasses."""
        raise NotImplementedError

# Rodajas Thread
class RodajasThread(BaseThread):
    def check_on_conditions(self):

        return (
            Hay_cartones(self.daq)
            and not self.state.rodajas_cerradas
            and not self.state.brazos_acercados
            and not Medido_largo(self.daq)
        )

    def check_off_conditions(self):
        return (
            #Rollo_soltado(self.daq)
            self.state.rodajas_cerradas
            and not self.state.brazos_acercados
            and self.state.cortar
        )

    def set_state(self, state_value):
        self.state.rodajas_cerradas = state_value

# Brazos Thread
class BrazosThread(BaseThread):
    def check_on_conditions(self):
        return (
            self.state.rodajas_cerradas
            and not self.state.brazos_acercados
            and not self.state.motor_prendido
            and not Medido_largo(self.daq)
        )

    def check_off_conditions(self):
        return (
            Medido_largo(self.daq)
            and self.state.brazos_acercados
            and not self.state.motor_prendido
        )

    def set_state(self, state_value):
        self.state.brazos_acercados = state_value

# Motores Thread
class MotoresThread(BaseThread):
    def check_on_conditions(self):
        return (
            Tapa_rollos(self.daq)
            and not Medido_largo(self.daq)
            and self.state.brazos_acercados
            and not self.state.motor_prendido
            and self.state.rollo_maestro_acercado
            and self.state.espreas
        )

    def check_off_conditions(self):
        return Medido_largo(self.daq) and self.state.motor_prendido

    def set_state(self, state_value):
        self.state.motor_prendido = state_value

# Cortar Thread
class CortarThread(BaseThread):
    def check_on_conditions(self):
        return (
            #Rollo_soltado(self.daq)
            Medido_largo(self.daq)
            and not self.state.brazos_acercados
            and not self.state.motor_prendido
            and not self.state.cortar
        )

    def check_off_conditions(self):
        return self.state.cortar and not Medido_largo(self.daq)

    def set_state(self, state_value):
        self.state.cortar = state_value

# Espreas Thread
class Espreas(BaseThread):
    def check_on_conditions(self):
        return (
                not Medido_largo(self.daq)
                and self.state.rodajas_cerradas
                and not self.state.brazos_acercados
                and not self.state.motor_prendido
                and not self.state.espreas 
        )
    def check_off_conditions(self):
        return self.state.espreas

    def set_state(self, state_value):
        self.state.espreas = state_value

# Rodajas Rollo Maestro Thread
class Rodajas_Rollo_Maestro(BaseThread):
    def check_on_conditions(self):
        return Rollo_maestro_sujetado(self.daq) and not self.state.rollo_maestro_rodajas

    def check_off_conditions(self):
        return False

    def set_state(self, state_value):
        self.state.rollo_maestro_rodajas = state_value

# Acercar Rollo Maestro Thread
class Acercar_Rollo_Maestro(BaseThread):
    def check_on_conditions(self):
        return (
            Rollo_maestro_sujetado(self.daq)
            and Tapa_rollos(self.daq)
            and self.state.rollo_maestro_rodajas
            and not self.state.rollo_maestro_acercado
        )

    def check_off_conditions(self):
        return False
    def set_state(self, state_value):
        self.state.rollo_maestro_acercado = state_value

def main():
    global root
    root = tk.Tk()

    # Create the DAQ simulator
    daq_simulator = DAQSimulator(root)

    # Create the system state object
    state = SystemState()

    # Initialize the threads with the DAQ simulator
    threads = [
        RodajasThread(state, daq_simulator, dout_bit=0),
        BrazosThread(state, daq_simulator, dout_bit=1),
        MotoresThread(state, daq_simulator, dout_bit=2),
        CortarThread(state, daq_simulator, dout_bit=3),
        Espreas(state, daq_simulator, dout_bit=4),
        Rodajas_Rollo_Maestro(state, daq_simulator, dout_bit=5),
        Acercar_Rollo_Maestro(state, daq_simulator, dout_bit=6)
    ]

    # Start all threads
    for thread in threads:
        thread.start()

    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()
