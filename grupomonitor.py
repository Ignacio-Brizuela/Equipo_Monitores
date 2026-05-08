# Archivo: grupomonitores.py
# Integrantes: Francisco Seura, Ignacio Brizuela, Mauricio Hernandez Raul Muñoz
# Técnica utilizada: Monitores
# Profesor: Rodrigo Ledezma

import multiprocessing
import time
import random
import math


class MonitorSincronizado:
    def __init__(self):
        """ El monitor utiliza un Lock interno y una Condición
        garantizan exclusion mutua y permitan dormir / despertar procesos"""
        self.lock = multiprocessing.Lock() #este es nuestro candado
        self.condicion = multiprocessing.Condition(self.lock) #permite que los procesos duerman y despierten
        self.hay_nuevo_dato = multiprocessing.Value('b', False) #verifica que haya un dato nuevo

    """pide entrar al monitor. Si otro proceso ya esta dentro, espera. Al entrar, queda con exclusion mutua."""
    def escribir_dato(self, nombre_archivo, valor):
        with self.condicion: 
            # Sección Crítica: El monitor garantiza exclusión mutua
            with open(nombre_archivo, 'a') as f:
                f.write(f"Dato generado: {valor}\n")

            # Cambia el estado y avisa a los que esperan (notify)
            self.hay_nuevo_dato.value = True
            self.condicion.notify_all() #comunicacion entre el productor y consumidor sin gastar cpu

    def procesar_dato(self, nombre_archivo):
        # bloque que adquiere el candado al entrar y lo libera al salir, garantizando exlusión mutua automáticamente
        with self.condicion: #aqui agarramos el candado
            while not self.hay_nuevo_dato.value: #lo dormimos para no usar cpu
                self.condicion.wait()
            
            # El monitor permite el acceso al archivo para procesar
            lineas = []
            with open(nombre_archivo, 'r') as f:
                lineas = f.readlines()
            
            if lineas:
                ultima_linea = lineas[-1]
                if "Dato generado:" in ultima_linea:
                    num = int(ultima_linea.split(":")[1].strip())
                    resultado = math.factorial(num)
                    
                    with open(nombre_archivo, 'a') as f:
                        f.write(f"El factorial de: {num} es {resultado}\n")
            
            # Resetear estado para la siguiente iteración
            self.hay_nuevo_dato.value = False

# Funciones que ejecutarán los procesos independientes
def productor(monitor, archivo):
    for _ in range(3):
        n = random.randint(1, 6)
        print(f"[Productor] Generando: {n}")
        monitor.escribir_dato(archivo, n)
        time.sleep(1)

def consumidor(monitor, archivo):
    for _ in range(3):
        monitor.procesar_dato(archivo)
        print(f"[Consumidor] Factorial calculado y guardado.")
        time.sleep(1)

if __name__ == '__main__':
    nombre_archivo = "resultados.txt"
    # Limpiar archivo previo
    with open(nombre_archivo, 'w') as f:
        f.write("--- Inicio de Laboratorio: Sincronización ---\n")

    # Instancia única del Monitor
    mi_monitor = MonitorSincronizado()

    # Creación de procesos, aqui los lanzamos de forma paralela
    p_gen = multiprocessing.Process(target=productor, args=(mi_monitor, nombre_archivo))
    p_calc = multiprocessing.Process(target=consumidor, args=(mi_monitor, nombre_archivo))

    p_gen.start()
    p_calc.start()

    p_gen.join()
    p_calc.join()

    print("\nProceso completado. Revisa resultados.txt")

"""

a) ¿Qué es la sincronización de procesos? 
La sincronización de procesos es un conjunto de mecanismos y técnicas destinados a asegurar la ejecución ordenada de procesos cooperativos. Su objetivo principal es mantener la consistencia de los datos, ya que el acceso concurrente a datos compartidos sin un control adecuado puede derivar en inconsistencias. Es fundamental para prevenir condiciones de carrera, situaciones donde varios procesos manipulan datos compartidos simultáneamente y el resultado final depende del orden de ejecución 

b) ¿Qué es un semáforo? 
Un semáforo es una herramienta de sincronización que se define como una variable de tipo entero. Se utiliza para controlar el acceso a recursos compartidos y garantizar la ejecución ordenada de procesos cooperativos sin necesidad de recurrir a la espera activa.
Operaciones Atómicas
Un semáforo solo puede ser manipulado a través de dos operaciones estándar e indivisibles (atómicas):
wait() (originalmente llamada P): Si el valor del semáforo es mayor a cero, lo decrementa. Si es cero o menor, el proceso que la invoca debe esperar (se suspende o bloquea).
signal() (originalmente llamada V): Incrementa el valor del semáforo. Si hay procesos esperando, permite que uno de ellos continúe su ejecución.
Tipos de Semáforos
Existen dos categorías según el rango de valores que pueden tomar:
Semáforo Binario: Su valor solo puede oscilar entre 0 y 1. Es utilizado principalmente para lograr la exclusión mutua (mutex), asegurando que solo un proceso entre en su sección crítica a la vez.
Semáforo de Cuenta (Contador): Su valor entero puede variar sobre un dominio sin restricciones. Se emplea para controlar el acceso a un recurso que tiene múltiples instancias disponibles.
Implementación sin Espera Activa
Para mejorar la eficiencia del sistema, las implementaciones modernas asocian cada semáforo a una cola de espera. En lugar de consumir ciclos de CPU revisando una condición (espera activa), el proceso se bloquea (block) y es ubicado en dicha cola hasta que otro proceso lo despierte (wakeup).
 Riesgos de Uso
Un uso incorrecto de los semáforos puede derivar en problemas graves de concurrencia:
Interbloqueo (Deadlock): Cuando dos o más procesos esperan indefinidamente por un evento que solo puede ser causado por otro de los procesos que también están esperando.
Inanición (Starvation): Bloqueo indefinido donde un proceso nunca es removido de la cola del semáforo en la que fue suspendido.

c) ¿Qué es un mutex?
Es un mecanismo o herramienta de sincronización de software diseñado específicamente para garantizar la exclusión mutua.
Se utiliza para evitar que más de un proceso o hilo acceda a una sección crítica al mismo tiempo, protegiendo así la integridad de los datos compartidos.
Su función principal es poner un "candado" antes de entrar a la sección crítica y "abrirlo" al salir.
Naturaleza Binaria: Se identifica como un semáforo binario, ya que su valor entero solo puede oscilar entre 0 y 1.
Operaciones: Funciona mediante dos operaciones principales:
Acquire (Adquirir): El proceso solicita el candado; si no está disponible, el proceso debe esperar.
Release (Liberar): El proceso libera el candado al terminar su sección crítica para que otros puedan usarlo.
Spin-locks: Son un tipo de mutex que utiliza espera activa (busy wait), donde el proceso consume ciclos de CPU verificando continuamente si el candado está disponible.
Adaptivos: En sistemas como Solaris, se utilizan mutexes adaptivos para proteger datos en segmentos de código pequeños.
Disponibilidad en APIs: Están integrados en las APIs de los sistemas operativos modernos, como Windows (donde son parte de los dispatcher objects), Linux y Pthreads.
Diferencia con Semáforos Contadores
Mientras que un semáforo contador puede permitir el acceso a múltiples instancias de un recurso, el mutex es estrictamente para exclusión mutua (acceso de uno en uno)

d) ¿Qué es un monitor? 
Un monitor es una abstracción o constructor de sincronización de alto nivel que permite compartir de forma segura tipos de datos abstractos entre procesos concurrentes. Se caracteriza por lo siguiente: 
Exclusión mutua automática: Solo un proceso puede estar activo dentro del monitor a la vez. 
Estructura: Contiene la declaración de variables compartidas, procedimientos (métodos) y código de inicialización. 
Implementación: Puede implementarse internamente utilizando semáforos para garantizar que los procesos esperen su turno para entrar. 
 
e) ¿Qué es una variable condicional?  
Es un mecanismo de sincronización utilizado dentro de los monitores para permitir que los procesos esperen a que se cumplan condiciones específicas. Poseen dos operaciones principales: 
wait(): El proceso que invoca esta operación es suspendido y colocado en una cola asociada a esa condición. 
signal(): Reinicia la ejecución de uno de los procesos que estaba suspendido por un previo wait() en esa variable. 
A diferencia de los semáforos, no tienen un valor entero asociado; solo sirven para suspender o reanudar procesos. """

"""f) Señale que concluye del método que aplicó a la sincronización de procesos comparado con los demás métodos. 


Complejidad

Los métodos básicos, como el Algoritmo de Peterson o el Algoritmo del Panadero, se basan en lecturas y escrituras atómicas manuales 
Esos algoritmos son sumamente complejos y propensos a errores porque el programador debe escribir el protocolo de entrada y salida manualmente."""

"""Monitores vs. Semáforos
Aunque ambos pueden evitar la espera activa, la diferencia es quién controla la lógica.
El Monitor garantiza que solo un proceso esté activo dentro del monitor a la vez de forma automática. El programador del proceso solo llama a la función (ej. procesar_dato), y el monitor se encarga de la seguridad internamente.
El uso de multiprocessing.Value asegura que la lectura y escritura de esta variable sea segura entre procesos.
La teoría advierte que omitir un signal o un uso incorrecto de las operaciones puede llevar a un interbloqueo (deadlock) o inanición (starvation) 
sin self.condicion.notify_all(), el consumidor se quedaría en un estado de espera indefinida (bloqueo), lo cual es la base del deadlock """

"""La función de despertar (wakeup). Reinicia los procesos que invocaron el wait(), permitiendo que el sistema aproveche el procesador solo cuando hay trabajo real que hacer 
Con self.condicion.wait(), el proceso se suspende y deja de consumir CPU por completo hasta que es despertado por el productor"""

"""Aunque en Python es una abstracción, internamente el Monitor depende de instrucciones de hardware como TestAndSet o Swap. 
Estas instrucciones aseguran que el chequeo y la asignación del candado (lock) ocurran de forma indivisible para que dos procesos no asuman que tienen el candado al mismo tiempo.
Al usar un Monitor, pasamos a una herramienta de alto nivel donde la sincronización es "invisible" para el resto del programa, ya que está encapsulada dentro de la clase."""
