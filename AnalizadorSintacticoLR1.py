from Pila import * 
from Matriz import *
from ArbolSintactico import exportar_arbol_pyvis, Nodo 

class AnalizadorSintactico:
    def __init__(self, matriz_lr1, lista_tokens, lista_simbolos):
        self.matriz_acciones = matriz_lr1
        self.cadena_tokens = list(lista_tokens) + [23] # token 23 = $
        self.cadena_simbolos = list(lista_simbolos) + ['$']
        self.indice_lectura = 0
        self.registro_pasos = []

        # Inicializar la pila con el estado 0
        self.pila_estados = Pila()
        self.pila_estados.push(Estado(0))

        # Pila semántica para construir el árbol
        self.pila_semantica = Pila()

        self.diccionario_no_terminales = {
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

        # Diccionario de reglas de producción (lado izquierdo, cantidad_simbolos_derecha)
        self.reglas_gramatica = {
            1:  (24, 1),  # programa -> Definiciones
            2:  (25, 0),  # Definiciones -> ε
            3:  (25, 2),  # Definiciones -> Definiciones Definicion
            4:  (26, 1),  # Definicion -> DefVar
            5:  (26, 1),  # Definicion -> DefFunc
            6:  (27, 4),  # DefVar -> tipo ID ListaVar ;
            7:  (28, 0),  # ListaVar -> ε
            8:  (28, 3),  # ListaVar -> , ID ListaVar
            9:  (29, 6),  # DefFunc -> tipo ID ( Parametros ) BloqFunc
            10: (30, 0),  # Parametros -> ε
            11: (30, 3),  # Parametros -> tipo ID ListaParam
            12: (31, 0),  # ListaParam -> ε
            13: (31, 4),  # ListaParam -> , tipo ID ListaParam
            14: (32, 3),  # BloqFunc -> { DefLocales Sentencias }
            15: (33, 0),  # DefLocales -> ε
            16: (33, 2),  # DefLocales -> DefLocales DefLocal
            17: (34, 1),  # DefLocal -> DefVar
            18: (34, 1),  # DefLocal -> DefFunc
            19: (35, 0),  # Sentencias -> ε
            20: (35, 2),  # Sentencias -> Sentencias Sentencia
            21: (36, 4),  # Sentencia -> if ( Expresion ) SentenciaBloque Otro
            22: (36, 6),  # Sentencia -> while ( Expresion ) SentenciaBloque
            23: (36, 5),  # Sentencia -> ID = Expresion ;
            24: (36, 3),  # Sentencia -> LlamadaFunc ;
            25: (36, 2),  # Sentencia -> return ValorRegresa ;
            26: (37, 0),  # Otro -> ε
            27: (37, 2),  # Otro -> else SentenciaBloque
            28: (38, 3),  # Bloque -> { Sentencias }
            29: (39, 0),  # ValorRegresa -> ε
            30: (39, 1),  # ValorRegresa -> Expresion
            31: (40, 0),  # Argumentos -> ε
            32: (40, 2),  # Argumentos -> Expresion ListaArgumentos
            33: (41, 0),  # ListaArgumentos -> ε
            34: (41, 3),  # ListaArgumentos -> , Expresion ListaArgumentos
            35: (42, 1),  # Termino -> ID
            36: (42, 1),  # Termino -> NUM
            37: (42, 1),  # Termino -> REAL
            38: (42, 1),  # Termino -> CADENA
            39: (42, 1),  # Termino -> LlamadaFunc
            40: (43, 4),  # LlamadaFunc -> ID ( Argumentos )
            41: (44, 1),  # SentenciaBloque -> Bloque
            42: (44, 1),  # SentenciaBloque -> Sentencia
            43: (45, 3),  # Expresion -> Expresion + Expresion
            44: (45, 2),  # Expresion -> ! Expresion
            45: (45, 2),  # Expresion -> - Expresion
            46: (45, 3),  # Expresion -> Expresion - Expresion
            47: (45, 3),  # Expresion -> Expresion * Expresion
            48: (45, 3),  # Expresion -> Expresion / Expresion
            49: (45, 3),  # Expresion -> Expresion opRelac Expresion
            50: (45, 3),  # Expresion -> Expresion opIgualdad Expresion
            51: (45, 3),  # Expresion -> ( Expresion )
            52: (45, 1)   # Expresion -> Termino
        }

        self.numero_paso = 0

    def obtener_representacion_pila(self):
        """Representación legible de la pila mostrando solo los elementos relevantes"""
        elementos_pila = []
        for elemento in self.pila_estados.items:
            if isinstance(elemento, Estado):
                elementos_pila.append(f"S{elemento.valor}")
            elif isinstance(elemento, Terminal):
                elementos_pila.append(str(elemento.valor))
            elif isinstance(elemento, NoTerminal):
                elementos_pila.append(str(elemento.valor))
        return "[" + " ".join(elementos_pila) + "]"

    def obtener_entrada_restante(self):
        """Entrada desde el índice actual hasta el final"""
        simbolos_restantes = self.cadena_simbolos[self.indice_lectura:]
        return " ".join(simbolos_restantes)

    def obtener_nombre_no_terminal(self, codigo_no_terminal):
        return self.diccionario_no_terminales.get(codigo_no_terminal, f"NoTerminal{codigo_no_terminal}")

    def imprimir_encabezado_tabla(self):
        print("\n" + "="*80)
        print("                     ANÁLISIS SINTÁCTICO LR(1)")
        print("="*80)

    def imprimir_paso_analisis(self, accion_descripcion):
        self.numero_paso += 1
        
        simbolo_actual = self.cadena_simbolos[self.indice_lectura]
        token_actual = self.cadena_tokens[self.indice_lectura]
        
        print(f"\n📍 PASO {self.numero_paso}")
        print("-" * 40)
        print(f"    PILA:      {self.obtener_representacion_pila()}")
        print(f"    ENTRADA:    {self.obtener_entrada_restante()}")
        print(f"    OBJETIVO: {simbolo_actual} (token: {token_actual})")
        print(f"    ACCIÓN:     {accion_descripcion}")

    def analizar(self, nombre_salida_arbol='arbol_sintactico', formato_salida='png'):
        self.imprimir_encabezado_tabla()

        while True:
            # Verificar que la cima de la pila sea un Estado
            elemento_cima = self.pila_estados.top()
            if not isinstance(elemento_cima, Estado):
                print(f"\n❌ ERROR INTERNO: la cima de la pila no es un Estado: {type(elemento_cima)}")
                return False
            
            estado_actual = elemento_cima.valor
            token_actual = self.cadena_tokens[self.indice_lectura]
            simbolo_actual = self.cadena_simbolos[self.indice_lectura]

            try:
                accion = self.matriz_acciones.consultar(estado_actual, token_actual)
            except IndexError as e:
                print(f"\n❌ ERROR: No se puede consultar matriz en posición ({estado_actual}, {token_actual}): {e}")
                return False

            # Caso: Error sintáctico
            if accion == 0:
                self.imprimir_paso_analisis("❌ ERROR SINTÁCTICO")
                print(f"\n DETALLES DEL ERROR:")
                print(f"        Estado actual: S{estado_actual}")
                print(f"        Token inesperado: '{simbolo_actual}' (tipo: {token_actual})")
                print(f"        No hay transición definida en la tabla LR(1)")
                print("="*80)
                return False

            # Caso: Desplazamiento
            elif accion > 0:
                estado_destino = accion
                descripcion_accion = f"🔄 DESPLAZAMIENTO → S{estado_destino}"
                self.imprimir_paso_analisis(descripcion_accion)
                
                # Realizar desplazamiento
                self.pila_estados.push(Terminal(simbolo_actual))
                self.pila_estados.push(Estado(estado_destino))
                self.indice_lectura += 1

                # En la pila semántica guardamos el nodo terminal correspondiente
                nodo_terminal = Nodo(etiqueta=f"T_{token_actual}", simbolo_lexico=simbolo_actual)
                self.pila_semantica.push(nodo_terminal)
                continue

            # Caso: Aceptación
            elif accion == -1:
                self.imprimir_paso_analisis("✅ ACEPTAR")
                print("="*80)
                print("\nANÁLISIS COMPLETADO")
                print("La cadena de entrada ES SINTÁCTICAMENTE VÁLIDA")
    
                if self.pila_semantica.is_empty():
                    print("La pila semántica está vacía — no se construyó árbol")
                    return True
                
                # Raíz esperada en la pila semántica
                raiz = self.pila_semantica.top()
                try:
                    exportar_arbol_pyvis(raiz, nombre_salida='arbol_interactivo.html')

                except Exception as e:
                    print(f"No se pudo generar HTML interactivo con pyvis: {e}")
                return True

            # Caso: Reducción
            else:
                numero_regla = -accion - 1
                
                if numero_regla not in self.reglas_gramatica:
                    print(f"\n❌ ERROR: Regla de reducción {numero_regla} no existe")
                    return False
                
                lado_izquierdo, cantidad_simbolos_derecha = self.reglas_gramatica[numero_regla]
                nombre_lado_izquierdo = self.obtener_nombre_no_terminal(lado_izquierdo)
                
                descripcion_accion = f"🔽 REDUCIR R{numero_regla}"
                self.imprimir_paso_analisis(descripcion_accion)
                
                # Imprimir detalles ANTES de hacer la reducción
                print(f"            *Regla aplicada: R{numero_regla} → {nombre_lado_izquierdo}({lado_izquierdo})")
                print(f"            *Elementos a eliminar: {cantidad_simbolos_derecha * 2} (símbolos y estados)")

                # Recolectar nodos semánticos ANTES de eliminar de la pila de estados
                hijos = []
                if cantidad_simbolos_derecha > 0:
                    # extraer en orden izquierdo a derecho: como la pila guarda en orden, extraemos en reversa y luego invertimos
                    for _ in range(cantidad_simbolos_derecha):
                        if self.pila_semantica.is_empty():
                            print(f"❌ ERROR: Intentando hacer pop en pila semántica vacía durante reducción")
                            return False
                        hijos.append(self.pila_semantica.pop())
                    # invertir una vez para obtener orden izquierdo->derecho
                    hijos.reverse()

                # Realizar reducción: eliminar 2 * cantidad_simbolos_derecha elementos
                for _ in range(2 * cantidad_simbolos_derecha):
                    if self.pila_estados.is_empty():
                        print(f"\n❌ ERROR: Intentando hacer pop en pila vacía durante reducción")
                        return False
                    self.pila_estados.pop()

                # Obtener el nuevo estado actual DESPUÉS de la reducción
                if self.pila_estados.is_empty():
                    print(f"\n❌ ERROR: Pila vacía después de la reducción")
                    return False
                
                estado_anterior = self.pila_estados.top().valor
                print(f"            *Estado tras reducir: S{estado_anterior}")

                # Consultar matriz
                try:
                    nuevo_estado = self.matriz_acciones.consultar(estado_anterior, lado_izquierdo)
                except IndexError as e:
                    print(f"\n❌ ERROR: No se puede consultar GOTO en posición ({estado_anterior}, {lado_izquierdo}): {e}")
                    return False

                if nuevo_estado == 0:
                    print(f"\n❌ ERROR: GOTO indefinido para {nombre_lado_izquierdo} desde estado {estado_anterior}")
                    return False
                
                # Crear nuevo nodo no-terminal y agregar los hijos recolectados
                nodo_nt = Nodo(etiqueta=nombre_lado_izquierdo)
                for h in hijos:
                    nodo_nt.agregar_hijo(h)
                
                # Si la producción fue epsilon (cant_rhs == 0), crear un hijo ε
                if cantidad_simbolos_derecha == 0:
                    nodo_nt.agregar_hijo(Nodo(etiqueta='ε'))

                # Apilar el nodo resultante en la pila semántica
                self.pila_semantica.push(nodo_nt)

                # Apilar el no terminal y el nuevo estado
                self.pila_estados.push(NoTerminal(nombre_lado_izquierdo))
                self.pila_estados.push(Estado(nuevo_estado))
                
                print(f"            * GOTO: Apilando '{nombre_lado_izquierdo}' y S{nuevo_estado}")
                print(f" * Nodo creado: {nodo_nt}")
