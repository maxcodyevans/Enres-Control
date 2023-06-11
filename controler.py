import piplates.RELAYplate as rly
import piplates.DAQCplate as daq
import time
import threading
from threading import Thread


# sample relay code, turn on K1
# rly.relayON(0,1)
# rly.relayOFF(0,1)

# daq.setDOUTbit(1,0)
# daq.clrDOUTbit(1,0)

# daq.getDINbit(1,0)
# daq.getDINbit(1,7)

# time.sleep(5)

SLEEP = 5  # Sleep Default


def Cerrar_rodajas(prendido, hay_cartones,lock):
    global rodajas_cerradas
    lock.acquire()

    # Condiciones Entrada
    if prendido and hay_cartones:

        daq.setDOUTbit(1, 0)
        time.sleep(SLEEP)
        rodajas_cerradas = True


    # Condiciones Salida
    if (not prendido) or rollo_soltado or brazos_acercados:
        daq.clrDOUTbit(1, 0)
        time.sleep(SLEEP)
        rodajas_cerradas = False

    lock.release()
    return


def Acercar_brazos(prendido, medido_largo, rodajas_cerradas, motor_prendido,lock):
    global brazos_acercados
    lock.acquire()

    if prendido and rodajas_cerradas and not motor_prendido:
        daq.setDOUTbit(1, 1)
        time.sleep(SLEEP)
        brazos_acercados = True

    if (not medido_largo):
        daq.clrDOUTbit(1, 1)
        time.sleep(SLEEP)
        brazos_acercados = False

    lock.release()
    return


def Prender_motor(tapa_rollos, medido_largo, brazos_acercados, acercar_rollo_maestro):
    global motor_prendido

    if brazos_acercados and tapa_rollos and medido_largo and acercar_rollo_maestro:
        daq.setDOUTbit(1, 2)
        time.sleep(SLEEP)
        motor_prendido = True

    if (not medido_largo):
        daq.clrDOUTbit(1, 2)
        time.sleep(SLEEP)
        motor_prendido = False

    return


def Cortar(rollo_soltado, brazos_acercados, motor_prendido, medido_largo):
    if rollo_soltado and not brazos_acercados and not motor_prendido and not medido_largo:
        daq.setDOUTbit(1, 3)
        time.sleep(SLEEP)

    return


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


def main():
    def prendido() :         return not bool(daq.getDINbit(1, 0))  # TRUE by default
    def hay_cartones() :     return not bool(daq.getDINbit(1, 1))  # TRUE by default
    def medido_largo() :     return not bool(daq.getDINbit(1, 2))
    def tapa_rollos() :      return not bool(daq.getDINbit(1, 3))
    def longitud_medida() :  return not bool(daq.getDINbit(1, 4))
    def rollo_soltado() :    return not bool(daq.getDINbit(1, 5))
    def rollo_maestro_sujetado() : return bool(daq.getDINbit(1, 6))
    def rollo_maestro_soltado() :  return bool(daq.getDINbit(1, 7))

    # estado de funciones
    rodajas_cerradas = False
    lock_rodajas = threading.Lock()
    brazos_acercados = False
    lock_brazos = threading.Lock()
    motor_prendido = False
    rollo_maestro_rodajas = False
    rollo_maestro_acercado = False


    while prendido():

        #Cerrar_rodajas(prendido, hay_cartones, rodajas_cerradas)
        thread = Thread(task=Cerrar_rodajas(), arg=(prendido(), hay_cartones(),lock_rodajas))
        thread.start()

        #Acercar_brazos(prendido, rodajas_cerradas, motor_prendido, medido_largo, brazos_acercados)
        thread2 = Thread(Acercar_brazos(), (prendido(), medido_largo(), rodajas_cerradas, motor_prendido,lock_brazos))
        thread2.start()

        Prender_motor(tapa_rollos(), medido_largo(), brazos_acercados, acercar_rollo_maestro)
        Cortar(rollo_soltado(), medido_largo(),brazos_acercados, motor_prendido)
        Espreas(brazos_acercados)

        #Rodajas_rollo_maestro(rollo_maestro_sujetado, rollo_maestro_acercado, rollo_maestro_rodajas)
        #Acercar_rollo_maestro(rollo_maestro_soltado, tapa_rollos, rollo_maestro_rodajas, rollo_maestro_acercado)

