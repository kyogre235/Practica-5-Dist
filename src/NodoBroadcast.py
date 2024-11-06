import simpy
from Nodo import *
from Canales.CanalRecorridos import *
from random import randint

class NodoBroadcast(Nodo):
    def __init__(self, id_nodo: int, vecinos: list, canal_entrada: simpy.Store,
                 canal_salida: simpy.Store):
        super().__init__(id_nodo,vecinos,canal_entrada,canal_salida)
        self.mensaje = None
        self.reloj = 0
        self.eventos = []

    def broadcast(self, env: simpy.Environment, data="Mensaje"):
        """
        Realiza la difusión de un mensaje a los nodos vecinos y gestiona la recepción de mensajes.
        
        Args:
            env (simpy.Environment): Entorno de simulación de `simpy`.
            data (str, optional): El mensaje que se va a transmitir; por defecto es "Mensaje".
        """
        if self.id_nodo == 0:
            self.mensaje = data
            yield env.timeout(randint(1,5))
        
            for k in self.vecinos:
                self.reloj += 1
                self.eventos.append([self.reloj, 'E', data, self.id_nodo, k])
                self.canal_salida.envia((data, self.reloj, self.id_nodo),[k])

        yield env.timeout(randint(1,5))

        while True:
            yield env.timeout(randint(1,5))
            (data, reloj, j) = yield self.canal_entrada.get()
            self.reloj = max(self.reloj, reloj) + 1
            self.eventos.append([self.reloj,'R',data,j,self.id_nodo])
            self.mensaje = data
            yield env.timeout(randint(1,5))

            for k in self.vecinos:
                self.reloj += 1
                self.eventos.append([self.reloj,'E',data,self.id_nodo,k])
                self.canal_salida.envia((data,self.reloj,self.id_nodo),[k])
