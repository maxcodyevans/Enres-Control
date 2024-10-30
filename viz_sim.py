import tkinter as tk
from control_sim import (
    SystemState,
    DAQSimulator,
    RodajasThread,
    BrazosThread,
    MotoresThread,
    CortarThread,
    Espreas,
    Rodajas_Rollo_Maestro,
    Acercar_Rollo_Maestro
)

class SimulatorGUI:
    def __init__(self, root, state, daq):
        self.state = state
        self.daq = daq

        # Main window title
        root.title("System State Simulator")

        # System state title
        self.label_title = tk.Label(
            root, text="System State", font=("Helvetica", 20, "bold")
        )
        self.label_title.pack(pady=10)

        # System state labels
        self.label_rodajas = tk.Label(
            root, text="Rodajas Cerradas 0: False", font=("Helvetica", 16)
        )
        self.label_rodajas.pack()

        self.label_brazos = tk.Label(
            root, text="Brazos Acercados 1: False", font=("Helvetica", 16)
        )
        self.label_brazos.pack()

        self.label_motor = tk.Label(
            root, text="Motor Prendido 2: False", font=("Helvetica", 16)
        )
        self.label_motor.pack()

        self.label_cortar = tk.Label(
            root, text="Cortar 3: False", font=("Helvetica", 16)
        )
        self.label_cortar.pack()

        self.label_espreas = tk.Label(
            root, text="Espreas 4: False", font=("Helvetica", 16)
        )
        self.label_espreas.pack()

        self.label_rollo_maestro_rodajas = tk.Label(
            root, text="Rollo Maestro Rodajas 5: False", font=("Helvetica", 16)
        )
        self.label_rollo_maestro_rodajas.pack()

        self.label_rollo_maestro_acercado = tk.Label(
            root, text="Rollo Maestro Acercado 6: False", font=("Helvetica", 16)
        )
        self.label_rollo_maestro_acercado.pack()

        # DAQ Input state title
        self.label_input_title = tk.Label(
            root, text="DAQ Input States", font=("Helvetica", 20, "bold")
        )
        self.label_input_title.pack(pady=10)

        # DAQ Input state labels
        self.label_prendido = tk.Label(
            root, text="Prendido: False", font=("Helvetica", 16)
        )
        self.label_prendido.pack()

        self.label_maestro_sujetado = tk.Label(
            root, text="Rollo Maestro Sujetado: False", font=("Helvetica", 16)
        )
        self.label_maestro_sujetado.pack()

        self.label_maestro_soltado = tk.Label(
            root, text="Rollo Maestro Soltado: False", font=("Helvetica", 16)
        )
        self.label_maestro_soltado.pack()

        self.label_longitud = tk.Label(
            root, text="Longitud Medida 3: False", font=("Helvetica", 16)
        )
        self.label_longitud.pack()
        self.label_tapa = tk.Label(
            root, text="Tapa Rollos 4: False", font=("Helvetica", 16)
        )
        self.label_tapa.pack()

        self.label_cartones = tk.Label(
            root, text="Hay Cartones: False", font=("Helvetica", 16)
        )
        self.label_cartones.pack()

        self.label_medido = tk.Label(
            root, text="Medido Largo: False", font=("Helvetica", 16)
        )
        self.label_medido.pack()




        self.label_rollo_soltado = tk.Label(
            root, text="Rollo Soltado: False", font=("Helvetica", 16)
        )
        self.label_rollo_soltado.pack()



        # Update the GUI continuously
        self.update_labels()

    def update_labels(self):
        """Update the labels to reflect the current system state and DAQ input states"""
        # Update system state
        self.label_rodajas.config(
            text=f"Rodajas Cerradas 0: {self.state.rodajas_cerradas}"
        )
        self.label_brazos.config(
            text=f"Brazos Acercados 1: {self.state.brazos_acercados}"
        )
        self.label_motor.config(text=f"Motor Prendido 2: {self.state.motor_prendido}")
        self.label_cortar.config(text=f"Cortar 3: {self.state.cortar}")
        self.label_espreas.config(text=f"Espreas 4: {self.state.espreas}")
        self.label_rollo_maestro_rodajas.config(
            text=f"Rollo Maestro Rodajas 5: {self.state.rollo_maestro_rodajas}"
        )
        self.label_rollo_maestro_acercado.config(
            text=f"Rollo Maestro Acercado 6: {self.state.rollo_maestro_acercado}"
        )

        # Update DAQ input state
        self.label_prendido.config(text=f"Prendido 0: {self.daq.get_input(0)}")
        self.label_maestro_sujetado.config(
            text=f"Rollo Maestro Sujetado 1: {self.daq.get_input(1)}"
        )
        self.label_maestro_soltado.config(
            text=f"Rollo Maestro Soltado 2: {self.daq.get_input(2)}"
        )
        self.label_longitud.config(text=f"Longitud Medida 3: {self.daq.get_input(3)}")

        self.label_tapa.config(text=f"Tapa Rollos 4: {self.daq.get_input(4)}")
        self.label_cartones.config(text=f"Hay Cartones 5: {self.daq.get_input(5)}")
        self.label_rollo_soltado.config(text=f"Rollo Soltado 6: {self.daq.get_input(6)}")
        self.label_medido.config(text=f"Medido Largo 7: {self.daq.get_input(7)}")


        # Re-run this method after a short delay (500ms)
        root.after(1000, self.update_labels)


def main():
    global root
    root = tk.Tk()

    # Create the DAQ simulator
    daq_simulator = DAQSimulator(root)

    # Create the system state object
    state = SystemState()

    # Initialize the GUI
    gui = SimulatorGUI(root, state, daq_simulator)

    # Initialize the threads with the DAQ simulator passed to each one
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
