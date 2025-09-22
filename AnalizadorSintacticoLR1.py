# AnalizadorSintacticoLR1.py
from Pila import *   # Importa Pila, Estado, Terminal, NoTerminal
from Matriz import *

class AnalizadorSintactico:
    def __init__(self, matriz, tokens, simbolos):
        self.matriz = matriz
        self.tokens = list(tokens) + [23]   # token 23 = $
        self.simbolos = list(simbolos) + ['$']
        self.index = 0
        self.pasos = []  # para depuración

        # Inicializar la pila con el estado 0
        self.stack = Pila()
        self.stack.push(Estado(0))

        # Mapeo de no terminales
        self.no_terminales = {
            24: "programa",
            25: "Definiciones",
            26: "Definicion",
            27: "DefVar",
            28: "ListaVar",
            29: "DefFunc",
            30: "Parametros",
            31: "ListaParam",
            32: "BloqFunc",
            33: "DefLocales",
            34: "DefLocal",
            35: "Sentencias",
            36: "Sentencia",
            37: "Otro",
            38: "Bloque",
            39: "ValorRegresa",
            40: "Argumentos",
            41: "ListaArgumentos",
            42: "Termino",
            43: "LlamadaFunc",
            44: "SentenciaBloque",
            45: "Expresion"
        }

        # Reglas (igual que antes)
        self.reglas = {
            1:  (24, 1), 2:  (25, 0), 3:  (25, 2),
            4:  (26, 1), 5:  (26, 1), 6:  (27, 4),
            7:  (28, 0), 8:  (28, 3), 9:  (29, 6),
            10: (30, 0), 11: (30, 3), 12: (31, 0),
            13: (31, 4), 14: (32, 3), 15: (33, 0),
            16: (33, 2), 17: (34, 1), 18: (34, 1),
            19: (35, 0), 20: (35, 2), 21: (36, 4),
            22: (36, 6), 23: (36, 5), 24: (36, 3),
            25: (36, 2), 26: (37, 0), 27: (37, 2),
            28: (38, 3), 29: (39, 0), 30: (39, 1),
            31: (40, 0), 32: (40, 2), 33: (41, 0),
            34: (41, 3), 35: (42, 1), 36: (42, 1),
            37: (42, 1), 38: (42, 1), 39: (42, 1),
            40: (43, 4), 41: (44, 1), 42: (44, 1),
            43: (45, 3), 44: (45, 2), 45: (45, 2),
            46: (45, 3), 47: (45, 3), 48: (45, 3),
            49: (45, 3), 50: (45, 3), 51: (45, 3),
            52: (45, 1)
        }

    def stack_str(self):
        """Representación legible de la pila"""
        return "[" + " ".join(str(x) for x in self.stack.items) + "]"

    def entrada_restante(self):
        """Entrada desde el índice actual"""
        return " ".join(self.simbolos[self.index:])

    def analizar(self):
        print("=== INICIO ANALISIS LR(1) ===")

        while True:
            # La cima de la pila debe ser un Estado
            top_elem = self.stack.top()
            if not isinstance(top_elem, Estado):
                print("ERROR: la cima de la pila no es un Estado")
                return False
            s = top_elem.valor

            a_token = self.tokens[self.index]
            a_simbolo = self.simbolos[self.index]

            accion = self.matriz.consultar(s, a_token)

            print(f"PILA: {self.stack_str()}\tENTRADA: {self.entrada_restante()}\t"
                  f"LOOKAHEAD: {a_simbolo} ({a_token})")

            if accion == 0:
                print("ERROR sintáctico")
                return False

            if accion > 0:
                # shift
                destino = accion
                print(f"Acción: shift d{destino}")
                self.stack.push(Terminal(a_simbolo))
                self.stack.push(Estado(destino))
                self.index += 1
                continue

            if accion == -1:
                print("Acción: aceptar (cadena válida)")
                return True

            # reducción
            regla_num = -accion - 1
            lhs, rhs_len = self.reglas[regla_num]
            lhs_name = self.no_terminales.get(lhs, f"NT{lhs}")
            print(f"Acción: reduce r{regla_num} -> {lhs_name}")

            for _ in range(2 * rhs_len):
                self.stack.pop()

            s_prime = self.stack.top().valor
            t = self.matriz.consultar(s_prime, lhs)
            if t == 0:
                print(f"ERROR: GOTO indefinido para {lhs_name}")
                return False

            self.stack.push(NoTerminal(lhs_name))
            self.stack.push(Estado(t))
            print(f"Efecto: push {lhs_name}, S{t}")
