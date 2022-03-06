"""
PRACTICA 1 ISABEL BELTRÁ MERINO

@author: isabelbeltramerino
"""
from multiprocessing import Process, Semaphore, Lock, Value, Array
from time import sleep
import random

N = 100
NPROD = 2 #numero de productores que se desee
longMax = 4

def delay(factor = 3):
    sleep(random()/factor)

def anadir_almacen(almacen, pid, valor, mutex):
    """
    FUNCIÃN AUXILIAR DEL PRODUCTOR
    """
    mutex.acquire()
    try:
        almacen[pid] = valor 
    finally:
        mutex.release()

def posicion_del_minimo(almacen, mutex):
    """
    FUNCIÃN AUXILIAR DEL CONSUMIDOR
    """
    mutex.acquire()
    try:
        minimo = 10 ** 3
        i = 1
        pos_min = -1
        for i in range(NPROD):
            if (almacen[i] != -1) and (almacen[i] < minimo):
                minimo = almacen[i]
                pos_min = i
    finally:
        mutex.release()
    return pos_min

def anadir_numero(resultado, indice, numero, mutex):
    """ 
    FUNCIÃN AUXILIAR DEL CONSUMIDOR
    """
    mutex.acquire()
    try:
        resultado[indice.value] = numero
        indice.value += 1
    finally:
        mutex.release()
                    
def productor(pid, almacen, empty, nonEmpty, long, mutex):
    """
    FUNCIÃN PRODUCTOR
    """
    valor = 0
    for i in range(long):
        print (f"productor {pid} esta produciendo")
        empty.acquire()
        valor += random.randint(0,5)
        print (f"productor {pid} ha producido un {valor}")
        anadir_almacen(almacen, pid, valor, mutex)
        nonEmpty.release()
    empty.acquire()
    almacen[pid] = -1
    nonEmpty.release()

def consumidor(resultado, almacen, empty, non_empty, indice, mutex):
    """
    FUNCIÃN CONSUMIDOR
    resultado y almacen son arrays, empty y nonEmpty son listas de semaforos
    """
    
    for i in range(NPROD):
        non_empty[i].acquire()
    
    while (-1) in resultado:
        pos_min = posicion_del_minimo(almacen, mutex)
        anadir_numero(resultado, indice, almacen[pos_min], mutex)
        print(resultado[:])
        empty[pos_min].release()
        print (f"consumer  consumiendo {almacen[pos_min]}")
        non_empty[pos_min].acquire()

        

def main():
    K = NPROD * 4
    almacen = Array('i', NPROD)
    indice = Value('i', 0)
    resultado = Array('i', K)
    
    for i in range(NPROD):
        almacen[i] = -1
    
    for i in range(K):
        resultado[i] = -1
        
    non_empty = []
    empty = []
    mutex = Lock()
    
    for i in range(NPROD):
        empty.append(Semaphore())
        non_empty.append(Semaphore())
    
    prodlst = [ Process(target=productor,
                        name=f'prod_{i}',
                        args=(i, almacen, empty[i], non_empty[i], longMax, mutex))
                for i in range(NPROD) ]

    conslst = [ Process(target=consumidor,
                      name=f"cons_{i}",
                      args=(resultado, almacen, empty, non_empty, indice, mutex))]

    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()
       
if __name__ == '__main__':
    main()