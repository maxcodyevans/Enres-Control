import tkinter as tk

from control import (
    BrazosThread,
    Hay_cartones,
    Longitud_medida,
    Medido_largo,
    Prendido,
    RodajasThread,
    Rollo_maestro_soltado,
    Rollo_maestro_sujetado,
    Rollo_soltado,
    SystemState,
    Tapa_rollos,
)


class SimulatorGUI:
    def __init__(self, root, state):
        self.state = state

        # Main window title
        root.title("System State Simulator")

        # System state title
        self.label_title = tk.Label(
            root, text="System State", font=("Helvetica", 20, "bold")
        )
        self.label_title.pack(pady=10)

        # System state labels
        self.label_rodajas = tk.Label(
            root, text="Rodajas Cerradas: False", font=("Helvetica", 16)
        )
        self.label_rodajas.pack()

        self.label_brazos = tk.Label(
            root, text="Brazos Acercados: False", font=("Helvetica", 16)
        )
        self.label_brazos.pack()

        self.label_motor = tk.Label(
            root, text="Motor Prendido: False", font=("Helvetica", 16)
        )
        self.label_motor.pack()

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

        self.label_cartones = tk.Label(
            root, text="Hay Cartones: False", font=("Helvetica", 16)
        )
        self.label_cartones.pack()

        self.label_medido = tk.Label(
            root, text="Medido Largo: False", font=("Helvetica", 16)
        )
        self.label_medido.pack()

        self.label_tapa = tk.Label(
            root, text="Tapa Rollos: False", font=("Helvetica", 16)
        )
        self.label_tapa.pack()

        self.label_longitud = tk.Label(
            root, text="Longitud Medida: False", font=("Helvetica", 16)
        )
        self.label_longitud.pack()

        self.label_rollo_soltado = tk.Label(
            root, text="Rollo Soltado: False", font=("Helvetica", 16)
        )
        self.label_rollo_soltado.pack()

        self.label_maestro_sujetado = tk.Label(
            root, text="Rollo Maestro Sujetado: False", font=("Helvetica", 16)
        )
        self.label_maestro_sujetado.pack()

        self.label_maestro_soltado = tk.Label(
            root, text="Rollo Maestro Soltado: False", font=("Helvetica", 16)
        )
        self.label_maestro_soltado.pack()

        # Update the GUI continuously
        self.update_labels()

    def update_labels(self):
        """Update the labels to reflect the current system state and DAQ input states"""
        # Update system state
        self.label_rodajas.config(
            text=f"Rodajas Cerradas: {self.state.rodajas_cerradas}"
        )
        self.label_brazos.config(
            text=f"Brazos Acercados: {self.state.brazos_acercados}"
        )
        self.label_motor.config(text=f"Motor Prendido: {self.state.motor_prendido}")

        # Update DAQ input state
        self.label_prendido.config(text=f"Prendido: {Prendido()}")
        self.label_cartones.config(text=f"Hay Cartones: {Hay_cartones()}")
        self.label_medido.config(text=f"Medido Largo: {Medido_largo()}")
        self.label_tapa.config(text=f"Tapa Rollos: {Tapa_rollos()}")
        self.label_longitud.config(text=f"Longitud Medida: {Longitud_medida()}")
        self.label_rollo_soltado.config(text=f"Rollo Soltado: {Rollo_soltado()}")
        self.label_maestro_sujetado.config(
            text=f"Rollo Maestro Sujetado: {Rollo_maestro_sujetado()}"
        )
        self.label_maestro_soltado.config(
            text=f"Rollo Maestro Soltado: {Rollo_maestro_soltado()}"
        )

        # Re-run this method after a short delay (500ms)
        root.after(500, self.update_labels)


def main():
    global root
    root = tk.Tk()

    # Create the system state object
    state = SystemState()

    # Initialize the GUI
    gui = SimulatorGUI(root, state)

    threads = [
        RodajasThread(state),
        BrazosThread(state),
        MotoresThread(state),
        CortarThread(state),
    ]

    for thread in threads:
        thread.start()

    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()
