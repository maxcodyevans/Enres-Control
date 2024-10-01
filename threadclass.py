import piplates.RELAYplate as Rly
import piplates.DAQCplate as Daq
import time
import threading
from threading import Thread


SLEEP = 5  # Sleep Default






def Espreas(brazos_acercados):
    if brazos_acercados:
        daq.setDOUTbit(1, 4)

    return


def Rodajas_rollo_maestro(rollo_maestro_sujetado, rollo_maestro_acercado, rollo_maestro_rodajas):
    if rollo_maestro_sujetado and not rollo_maestro_acercado:
        daq.setDOUTbit(1, 5)
        time.sleep(SLEEP)
        rollo_maestro_rodajas = True

    if not rollo_maestro_acercado:
        daq.clrDOUTbit(1, 5)
        time.sleep(SLEEP)
        rollo_maestro_rodajas = False

    return


def Acercar_rollo_maestro(rollo_maestro_soltado, tapa_rollos, rollo_maestro_rodajas, rollo_maestro_acercado):
    if rollo_maestro_soltado and tapa_rollos and rollo_maestro_rodajas:
        daq.setDOUTbit(1, 6)
        time.sleep(SLEEP)
        rollo_maestro_acercado = True
    return

def Prendido() :         return not bool(daq.getDINbit(1, 0))  # TRUE by default
def Hay_cartones() :     return not bool(daq.getDINbit(1, 1))  # TRUE by default
def Medido_largo() :     return not bool(daq.getDINbit(1, 2))
def Tapa_rollos() :      return not bool(daq.getDINbit(1, 3))
def Longitud_medida() :  return not bool(daq.getDINbit(1, 4))
def Rollo_soltado() :    return not bool(daq.getDINbit(1, 5))
def Rollo_maestro_sujetado() : return bool(daq.getDINbit(1, 6))
def Rollo_maestro_soltado() :  return bool(daq.getDINbit(1, 7))


class RodajasThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        while Prendido():

            global rodajas_cerradas

            # Condiciones Entrada
            if Prendido() and Hay_cartones():
                Daq.setDOUTbit(1, 0)
                time.sleep(SLEEP)
                rodajas_cerradas  = True

            # Condiciones Salida
            if (not Prendido()) or Rollo_soltado() or brazos_acercados:
                Daq.clrDOUTbit(1, 0)
                time.sleep(SLEEP)
                rodajas_cerradas  = False


class BrazosThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        while Prendido():
            global brazos_acercados

            if Prendido() and rodajas_cerradas and not motor_prendido:
                Daq.setDOUTbit(1, 1)
                time.sleep(SLEEP)
                brazos_acercados = True

            if (not medido_largo):
                Daq.clrDOUTbit(1, 1)
                time.sleep(SLEEP)
                brazos_acercados = False

class MotoresThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        while Prendido():
            global motor_prendido

            if brazos_acercados and Tapa_rollos() and Medido_largo() and rollo_maestro_acercado:
                Daq.setDOUTbit(1, 2)
                time.sleep(SLEEP)
                motor_prendido = True

            if (not medido_largo):
                Daq.clrDOUTbit(1, 2)
                time.sleep(SLEEP)
                motor_prendido = False

class CortarThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        while Prendido():
            if Rollo_soltado() and not brazos_acercados and not motor_prendido and not Medido_largo():
                Daq.setDOUTbit(1, 3)
                time.sleep(SLEEP)

def main():


    # estado de funciones
    rodajas_cerradas = False
    brazos_acercados = False
    motor_prendido = False
    rollo_maestro_rodajas = False
    rollo_maestro_acercado = False



    thread = RodajasThread()
    thread.start()

    #Acercar_brazos(prendido, rodajas_cerradas, motor_prendido, medido_largo, brazos_acercados)
    thread2 = BrazosThread()
    thread2.start()

    thread3 = MotoresThread()
    thread3.start()

    thread4 = CortarThread()
    thread4.start()
    
    Espreas(brazos_acercados)

        #Rodajas_rollo_maestro(rollo_maestro_sujetado, rollo_maestro_acercado, rollo_maestro_rodajas)
        #Acercar_rollo_maestro(rollo_maestro_soltado, tapa_rollos, rollo_maestro_rodajas, rollo_maestro_acercado)

