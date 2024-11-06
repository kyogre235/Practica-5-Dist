import simpy
from Nodo import *
from Canales.CanalRecorridos import *
from random import randint

TICK = 1
class NodoDFS(Nodo):
    ''' Implementa la interfaz de Nodo para el algoritmo de Broadcast.'''

    def __init__(self, id_nodo, vecinos, canal_entrada, canal_salida, num_nodos):
        ''' Constructor de nodo que implemente el algoritmo DFS. '''
        super().__init__(id_nodo, vecinos, canal_entrada, canal_salida)
        self.padre = self.id_nodo
        self.hijos = []
        self.eventos = []
        self.reloj = [0] * num_nodos

    def dfs(self, env):
        """
        Ejecuta el algoritmo de recorrido en profundidad (DFS).

        Args:
            env (simpy.Environment): Entorno de simulación de `simpy`.
        """
        if self.id_nodo == 0:
            self.hijos = [self.vecinos[0]]
            self.reloj[self.id_nodo] += 1
            vistos = frozenset({self.id_nodo})
            self.eventos.append((self.reloj.copy(), 'E', self.id_nodo, self.vecinos[0], vistos))
            self.canal_salida.envia(("GO", vistos, self.id_nodo, self.reloj.copy()), [self.vecinos[0]])
        
        while True:
            yield env.timeout(TICK)
            msj = yield self.canal_entrada.get()
            (tipo, vistos, j, reloj) = msj
            for i in range(len(self.reloj)):
                self.reloj[i] = max(reloj[i], self.reloj[i])
            self.reloj[self.id_nodo] += 1
            self.eventos.append((self.reloj.copy(), 'R', j, self.id_nodo, vistos))

            if tipo == "GO":
                self.padre = j
                
                if set(self.vecinos) <= set(vistos):
                    self.reloj[self.id_nodo] += 1
                    new_vistos = frozenset(vistos | {self.id_nodo})
                    self.eventos.append((self.reloj.copy(), 'E', self.id_nodo, j, new_vistos))
                    self.canal_salida.envia(("BACK", new_vistos, self.id_nodo, self.reloj.copy()), [j])
                
                else:
                    no_visitado = min(v for v in self.vecinos if v not in vistos)
                    self.hijos = [no_visitado]
                    self.reloj[self.id_nodo] += 1
                    new_vistos = frozenset(vistos | {self.id_nodo})
                    self.eventos.append((self.reloj.copy(), 'E', self.id_nodo, no_visitado, new_vistos))
                    yield env.timeout(randint(1, 5))
                    self.canal_salida.envia(("GO", new_vistos, self.id_nodo, self.reloj.copy()), [no_visitado])
            else:  
                
                if set(self.vecinos) <= set(vistos):
                    if self.padre == self.id_nodo:  
                        return 
            
                    self.reloj[self.id_nodo] += 1
                    self.eventos.append((self.reloj.copy(), 'E', self.id_nodo, self.padre, vistos))
                    yield env.timeout(TICK)
                    self.canal_salida.envia(("BACK", vistos, self.id_nodo, self.reloj.copy()), [self.padre])
                
                else:
                    no_visitado = min(v for v in self.vecinos if v not in vistos)
                    self.hijos.append(no_visitado)
                    self.reloj[self.id_nodo] += 1
                    self.eventos.append((self.reloj.copy(), 'E', self.id_nodo, no_visitado, vistos))
                    yield env.timeout(TICK)
                    self.canal_salida.envia(("GO", vistos, self.id_nodo, self.reloj.copy()),[no_visitado]) 
