import copy
import math
import sys
from time import time
import numpy as np
from tqdm.auto import tqdm


# Elige un paso para una hormiga, teniendo en cuenta los valores
# las feromonas y descartando los nodos ya visitados.
def eligeNodo(distancias, ferom, visitados):
    # Se calcula la tabla de pesos de cada ciudad
    listaValores = []
    disponibles = []
    actual = visitados[-1]

    # Influencia de cada valor (alfa: feromonas; beta: valor)
    alfa = 1.0
    beta = 0.5

    # El parámetro beta (peso de los valores) es 0.5 y alfa=1.0
    for i in range(len(distancias)):
        if i not in visitados:
            fer = math.pow((ferom[actual][i]), alfa)
            peso = math.pow(1.0 / distancias[actual][i], beta) * fer
            disponibles.append(i)
            listaValores.append(peso)

    # Se elige aleatoriamente una de los nodos disponibles,
    # teniendo en cuenta su peso relativo.

    # normalizo las probabilidades
    sumaProb = sum(listaValores)
    for i in range(len(listaValores)):
        listaValores[i] = listaValores[i] / sumaProb
    valor = np.random.rand()
    i = 0
    acumulado = listaValores[i]
    while (i < len(listaValores)) and (valor > acumulado):
        i += 1
        acumulado += listaValores[i]

    # valor = random.random() * sum(listaValores)
    # acumulado = 0.0
    # i = -1
    # while valor > acumulado:
    #     i += 1
    #     acumulado += listaValores[i]

    return disponibles[i]


# Genera una "hormiga" , que eligirá un camino (nodos que visita) teniendo en cuenta
# los valores y los rastros de feromonas. Devuelve una tupla
# con el camino (nodos visitados) y su longCamino (Suma de valores).
def eligeCamino(matriz, feromonas):
    origen = 11#np.random.randint(len(matriz))
    camino = [origen]
    longCamino = 0

    # Elegir cada paso según los valores y las feromonas
    while len(camino) < len(matriz):
        nodo = eligeNodo(matriz, feromonas, camino)
        longCamino += matriz[camino[-1]][nodo]
        camino.append(nodo)

    # Para terminar hay que volver al nodo de origen
    longCamino += matriz[camino[-1]][origen]
    camino.append(origen)

    return (camino, longCamino)


# Actualiza la matriz de feromonas siguiendo el camino recibido
def rastroFeromonas(feromonas, caminos, tau, metodo, matriz, longCaminos):
    # hago la deposición de acuerdo al método, respetando la fórmula
    if (metodo == "global"):
        for k in (range(len(caminos))):
            camino = caminos[k]
            for i in range(len(camino) - 1):
                feromonas[camino[i]][camino[i + 1]] += tau / longCaminos[k]
    elif (metodo == "uniforme"):
        for k in (range(len(caminos))):
            camino = caminos[k]
            for i in range(len(camino) - 1):
                feromonas[camino[i]][camino[i + 1]] += tau
    elif (metodo == "local"):
        for k in (range(len(caminos))):
            camino = caminos[k]
            for i in range(len(camino) - 1):
                feromonas[camino[i]][camino[i + 1]] += tau / matriz[camino[i]][camino[i + 1]]


# Evapora todas las feromonas multiplicándolas por una constante
# = 0.9 ( en otras palabras, el coefienciente de evaporación es 0.1)
def evaporaFeromonas(Feromonas):
    Feromonas *= (1 - 0.1)

def contarCaminosIguales(cant, caminosHormigas):
    #cuento máximo caminos iguales y guardo índice k del más repetido
    maximoRepeticiones = caminosHormigas.count(caminosHormigas[0])
    masRepetido = 0
    for k in range(cant):
        repeticionesk = caminosHormigas.count(caminosHormigas[k])
        if(maximoRepeticiones < repeticionesk):
            maximoRepeticiones = repeticionesk
            masRepetido = k
    return maximoRepeticiones, masRepetido



# Resuelve el problema del viajante de comercio mediante el
# algoritmo de la colonia de hormigas. Recibe una matriz de
# distancias y devuelve una tupla con el mejor camino que ha
# obtenido (lista de índices) y su longitud
def hormigas(cant, matriz, iteraciones, tau, metodo):

    t0 = time()
    # Primero se crea una matriz de feromonas vacía
    n = len(matriz)
    Feromonas = copy.deepcopy(matriz)
    for i in range(Feromonas.shape[0]):
        for j in range(i + 1, Feromonas.shape[1]):
            Feromonas[i, j] = Feromonas[j, i] = np.random.rand()

    # El mejor camino y su longitud (inicialmente "infinita")
    mejorCamino = []
    longMejorCamino = sys.maxsize

    # En cada iteración se genera una hormiga, que elige un camino,
    # y si es mejor que el mejor que teníamos, deja su rastro de
    # feromonas (mayor cuanto más corto sea el camino)

    exito = 0
    for iter in tqdm(range(iteraciones), desc="Metodo "+metodo+" - Hormigas caminando: "):
            caminosHormigas = []
            longitudHormigas = []

            for k in range(cant):
                (camino, longCamino) = eligeCamino(matriz, Feromonas)
                caminosHormigas.append(camino)
                longitudHormigas.append(longCamino)

                if longCamino <= longMejorCamino:
                    mejorCamino = camino
                    longMejorCamino = longCamino

            (maximoRepeticiones, masRepetido)=contarCaminosIguales(cant, caminosHormigas)
            if (maximoRepeticiones == cant):
                #print("EXITO")
                exito += 1

            evaporaFeromonas(Feromonas)

            rastroFeromonas(Feromonas, caminosHormigas, tau, metodo, matriz, longitudHormigas)

            if(exito==5):
                print("Corta ciclo en iter: ",iter)
                break

    # Se devuelve el mejor camino que se haya encontrado
    t1 = time()
    tiempo=t1-t0
    return (mejorCamino, longMejorCamino, tiempo)


Caminos=np.loadtxt("gr17.csv",delimiter=",")
# numCiudades = len(Caminos[0])
# distanciaMaxima = max(max(fila) for fila in Caminos)
# Obtención del mejor camino
iteraciones = 2000
numeroHormigas = 10
tau = 0.1
# distMedia = numCiudades * distanciaMaxima / 2
CaminoOptimo = [11,3,15,14,17,6,8,7,13,4,1,16,12,9,5,2,10,11]

(camino, longCamino,tiempo) = hormigas(numeroHormigas, Caminos, iteraciones, tau, "uniforme")
print("Camino con metodo uniforme: ", camino)
print("Longitud del camino: ", longCamino)
print("Tiempo: ",tiempo)


(camino2, longCamino2,tiempo2) = hormigas(numeroHormigas, Caminos, iteraciones, tau, "global")
print("Camino con metodo global:   ", camino2)
print("Longitud del camino: ", longCamino2)
print("Tiempo: ",tiempo2)


(camino3, longCamino3,tiempo3) = hormigas(numeroHormigas, Caminos, iteraciones, tau, "local")
print("Camino con metodo local:    ", camino3)
print("Longitud del camino: ", longCamino3)
print("Tiempo: ",tiempo3)


print("--------------------------------------------------------------------------------------------")
print("Camino Optimo:              ", CaminoOptimo)
print("Longitud del Camino Optimo: 2085 km")