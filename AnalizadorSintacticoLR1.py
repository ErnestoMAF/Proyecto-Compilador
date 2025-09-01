from Pila import *
from Matriz import *

class AnalizadorSintactico:
    def __init__(self, matriz, tokens, simbolos):
        self.matriz = matriz
        self.tokens = tokens + [23]  # Fin de cadena
        self.simbolos = simbolos + ['$']
        self.pasos = []  # Almacenará (pila, entrada, salida)
        self.pila = Pila()
        self.pila.push(Estado(0))
        self.index = 0

    def analizar(self):
        while self.index < len(self.tokens):
            estado_actual = self.pila.top()
            estado_valor = estado_actual.valor
            token_actual = self.tokens[self.index]
            simbolo_actual = self.simbolos[self.index]
            
            columna = self.obtener_indice_columna(token_actual)
            if columna is None:
                columna = obtener_indice_columna(simbolo_actual)
            
            accion = self.matriz.consultar(estado_valor, columna)
            
            # Registrar estado actual ANTES de la acción
            entrada_actual = ''.join(self.simbolos[self.index:])
            salida_actual = self.obtener_salida(accion)
            self.registrar_paso(entrada_actual, salida_actual)
            
            if accion > 0:  # Desplazamiento
                self.pila.push(Terminal(simbolo_actual))
                self.pila.push(Estado(accion))
                self.index += 1
            elif accion < 0:  # Reducción
                regla = abs(accion)
                if regla == 1:  # Aceptación
                    break
                elif regla == 2:  # E -> E + id
                    self.aplicar_reduccion_r2()
                elif regla == 3:  # E -> id
                    self.aplicar_reduccion_r3()
            else:
                raise SyntaxError("Error de sintaxis")
        return self.pasos
    
    def aplicar_reduccion_r2(self):
        # Reducción R2: E -> id + E
        for _ in range(6): self.pila.pop()
        
        estado_anterior = self.pila.top()
        if not isinstance(estado_anterior, Estado):
            raise SyntaxError("Se esperaba un estado en la pila")
            
        # Consultar transición para E
        nuevo_estado = self.matriz.consultar(estado_anterior.valor, 3)
        self.pila.push(NoTerminal('E'))
        self.pila.push(Estado(nuevo_estado))
    
    def aplicar_reduccion_r3(self):
        # Reducción R3: E -> id
        for _ in range(2): self.pila.pop()
        
        estado_anterior = self.pila.top()
        if not isinstance(estado_anterior, Estado):
            raise SyntaxError("Se esperaba un estado en la pila")
            
        # Consultar transición para E
        nuevo_estado = self.matriz.consultar(estado_anterior.valor, 3)
        self.pila.push(NoTerminal('E'))
        self.pila.push(Estado(nuevo_estado))

    def obtener_salida(self, accion):
        if accion > 0: return f"d{accion}"
        if accion < 0: return f"R{abs(accion)}"
        return "ERROR"

    def registrar_paso(self, entrada, salida):
        # Representación compacta de la pila
        elementos = []
        for item in self.pila.items:
            if isinstance(item, Estado):
                elementos.append(str(item.valor))
            elif isinstance(item, Terminal):
                elementos.append(item.valor)
            elif isinstance(item, NoTerminal):
                elementos.append(item.valor)
        pila_str = '$' + ''.join(elementos)
        
        self.pasos.append((pila_str, entrada, salida))

    def imprimir_pasos(self):
        print(f"{'Pila':<20} {'Entrada':<15} {'Salida':<10}")
        print('-' * 45)
        for pila, entrada, salida in self.pasos:
            print(f"{pila:<20} {entrada:<15} {salida:<10}")
    
    def obtener_indice_columna(self,simbolo):
        if simbolo == 'identificador' or simbolo == 0:
            return 0
        elif simbolo == '+' or simbolo == 5:
            return 1
        elif simbolo == '$' or simbolo == 23:
            return 2
        elif simbolo == 'E':
            return 3
        else:
            return None