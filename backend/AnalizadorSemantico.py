from ArbolSintactico import Nodo

class Simbolo:
    def __init__(self, nombre, tipo, categoria, ambito, linea=0):
        self.nombre = nombre
        self.tipo = tipo  # 'int', 'float', 'void'
        self.categoria = categoria  # 'variable', 'funcion', 'parametro'
        self.ambito = ambito  # 'global', nombre de función
        self.linea = linea
        self.parametros = [] 
        self.inicializada = False
        self.usada = False
        
    def __repr__(self):
        if self.categoria == 'funcion':
            params = ', '.join([f"{p['tipo']} {p['nombre']}" for p in self.parametros])
            return f"{self.tipo} {self.nombre}({params}) [{self.ambito}]"
        return f"{self.tipo} {self.nombre} [{self.categoria}, {self.ambito}]"

class TablaSimbolos:
    def __init__(self):
        self.simbolos = {}
        self.ambito_actual = 'global'
        self.pila_ambitos = ['global']
        
    def entrar_ambito(self, nombre_ambito):
        self.pila_ambitos.append(nombre_ambito)
        self.ambito_actual = nombre_ambito
        
    def salir_ambito(self):
        if len(self.pila_ambitos) > 1:
            self.pila_ambitos.pop()
            self.ambito_actual = self.pila_ambitos[-1]
            
    def agregar_simbolo(self, simbolo):
        if simbolo.nombre not in self.simbolos:
            self.simbolos[simbolo.nombre] = []
        
        # Verificar si existe en el ámbito actual
        for s in self.simbolos[simbolo.nombre]:
            if s.ambito == simbolo.ambito:
                return False
        
        self.simbolos[simbolo.nombre].append(simbolo)
        return True
        
    def buscar_simbolo(self, nombre):
        if nombre not in self.simbolos:
            return None
            
        #ámbito actual
        for simbolo in self.simbolos[nombre]:
            if simbolo.ambito == self.ambito_actual:
                return simbolo
        
        for simbolo in self.simbolos[nombre]:
            if simbolo.ambito == 'global':
                return simbolo
                
        return None
    
    def buscar_funcion(self, nombre):
        if nombre not in self.simbolos:
            return None
        
        for simbolo in self.simbolos[nombre]:
            if simbolo.categoria == 'funcion':
                return simbolo
        return None
    
    def mostrar_tabla(self):
        print("\n")
        print("-"*80)
        print("                    TABLA DE SÍMBOLOS")
        
        funciones = []
        variables = []
        
        for nombre, lista_simbolos in self.simbolos.items():
            for simbolo in lista_simbolos:
                if simbolo.categoria == 'funcion':
                    funciones.append(simbolo)
                else:
                    variables.append(simbolo)
        
        if funciones:
            print("\nFUNCIONES:")
            print("-"*80)
            for func in funciones:
                params = ', '.join([f"{p['tipo']} {p['nombre']}" for p in func.parametros])
                print(f"  • {func.tipo} {func.nombre}({params})")
        
        if variables:
            print("\nVARIABLES:")
            print("-"*80)
            for var in variables:
                estado = "✓ usada" if var.usada else "❌ NO usada"
                print(f"  • {var.tipo} {var.nombre} [{var.ambito}] - {estado}")

class AnalizadorSemantico:
    """Analiza semánticamente el árbol sintáctico"""
    def __init__(self, raiz):
        self.raiz = raiz
        self.tabla = TablaSimbolos()
        self.errores = []
        self.advertencias = []
        self.tipo_actual = None
        self.funcion_actual = None
        
    def analizar(self):
        print("\n" + "="*80)
        print("                  ANÁLISIS SEMÁNTICO")
        print("="*80)
        
        # Primera pasada: construir tabla de símbolos
        print("\nConstruyendo tabla de símbolos...")
        self._construir_tabla_simbolos(self.raiz)
        
        # Segunda pasada: verificar tipos y uso
        print("Verificando tipos y su uso...")
        self._verificar_semantica(self.raiz)
        
        self.tabla.mostrar_tabla()
        
        self._mostrar_resultados()
        
        return len(self.errores) == 0
    
    def _construir_tabla_simbolos(self, nodo):
        if nodo is None:
            return
            
        # Definición de variable: tipo ID ListaVar ;
        if nodo.etiqueta == 'DefVar' and len(nodo.hijos) >= 4:
            tipo_nodo = nodo.hijos[0]
            id_nodo = nodo.hijos[1]
            
            if tipo_nodo.simbolo_lexico:
                tipo = tipo_nodo.simbolo_lexico
                nombre = id_nodo.simbolo_lexico
                
                simbolo = Simbolo(
                    nombre=nombre,
                    tipo=tipo,
                    categoria='variable',
                    ambito=self.tabla.ambito_actual
                )
                
                if not self.tabla.agregar_simbolo(simbolo):
                    self.errores.append(
                        f"Error. Variable '{nombre}' ya declarada en ámbito '{self.tabla.ambito_actual}'"
                    )
                
                self._procesar_lista_var(nodo.hijos[2], tipo)
        
        # Definición de función: tipo ID ( Parametros ) BloqFunc
        elif nodo.etiqueta == 'DefFunc' and len(nodo.hijos) >= 6:
            tipo_nodo = nodo.hijos[0]
            id_nodo = nodo.hijos[1]
            parametros_nodo = nodo.hijos[3]
            
            if tipo_nodo.simbolo_lexico:
                tipo = tipo_nodo.simbolo_lexico
                nombre = id_nodo.simbolo_lexico
                
                simbolo_func = Simbolo(
                    nombre=nombre,
                    tipo=tipo,
                    categoria='funcion',
                    ambito='global'
                )
                
                self._procesar_parametros(parametros_nodo, simbolo_func)
                
                if not self.tabla.agregar_simbolo(simbolo_func):
                    self.errores.append(f"Error. Función '{nombre}' ya declarada")
                
                self.tabla.entrar_ambito(nombre)
                self.funcion_actual = nombre
                
                for param in simbolo_func.parametros:
                    param_simbolo = Simbolo(
                        nombre=param['nombre'],
                        tipo=param['tipo'],
                        categoria='parametro',
                        ambito=nombre
                    )
                    self.tabla.agregar_simbolo(param_simbolo)
                
                # Procesar cuerpo de la función
                bloque_nodo = nodo.hijos[5]
                self._construir_tabla_simbolos(bloque_nodo)
                
                self.tabla.salir_ambito()
                self.funcion_actual = None
                return
        
        # BloqFunc: { DefLocales Sentencias }
        elif nodo.etiqueta == 'BloqFunc' and len(nodo.hijos) >= 3:
            # Procesar definiciones locales y sentencias dentro del ámbito actual
            for hijo in nodo.hijos:
                self._construir_tabla_simbolos(hijo)
            return
        
        # Procesar hijos recursivamente
        for hijo in nodo.hijos:
            self._construir_tabla_simbolos(hijo)
    
    def _procesar_lista_var(self, nodo, tipo):
        #lista de variables: , ID ListaVar
        if nodo.etiqueta == 'ListaVar' and len(nodo.hijos) >= 3:
            if nodo.hijos[0].simbolo_lexico == ',':
                nombre = nodo.hijos[1].simbolo_lexico
                simbolo = Simbolo(
                    nombre=nombre,
                    tipo=tipo,
                    categoria='variable',
                    ambito=self.tabla.ambito_actual
                )
                
                if not self.tabla.agregar_simbolo(simbolo):
                    self.errores.append(
                        f"❌ Variable '{nombre}' ya declarada en ámbito '{self.tabla.ambito_actual}'"
                    )
                
                self._procesar_lista_var(nodo.hijos[2], tipo)
    
    def _procesar_parametros(self, nodo, simbolo_func):
        if nodo.etiqueta == 'Parametros' and len(nodo.hijos) >= 3:
            tipo = nodo.hijos[0].simbolo_lexico
            nombre = nodo.hijos[1].simbolo_lexico
            
            simbolo_func.parametros.append({
                'tipo': tipo,
                'nombre': nombre
            })
            
            self._procesar_lista_param(nodo.hijos[2], simbolo_func)
    
    def _procesar_lista_param(self, nodo, simbolo_func):
        if nodo.etiqueta == 'ListaParam' and len(nodo.hijos) >= 4:
            if nodo.hijos[0].simbolo_lexico == ',':
                tipo = nodo.hijos[1].simbolo_lexico
                nombre = nodo.hijos[2].simbolo_lexico
                
                simbolo_func.parametros.append({
                    'tipo': tipo,
                    'nombre': nombre
                })
                
                self._procesar_lista_param(nodo.hijos[3], simbolo_func)
    
    def _verificar_semantica(self, nodo):
        if nodo is None:
            return
        
        if nodo.etiqueta == 'DefFunc' and len(nodo.hijos) >= 6:
            id_nodo = nodo.hijos[1]
            nombre_func = id_nodo.simbolo_lexico
            
            self.tabla.entrar_ambito(nombre_func)
            
            # Procesar el cuerpo de la función
            bloque_nodo = nodo.hijos[5]
            self._verificar_semantica(bloque_nodo)
            
            self.tabla.salir_ambito()
            return
        
        # Verificar asignación: ID = Expresion ;
        if nodo.etiqueta == 'Sentencia' and len(nodo.hijos) >= 4:
            if nodo.hijos[1].simbolo_lexico == '=':
                nombre_var = nodo.hijos[0].simbolo_lexico
                simbolo = self.tabla.buscar_simbolo(nombre_var)
                
                if simbolo is None:
                    self.errores.append(f"Error. Variable '{nombre_var}' no declarada")
                else:
                    simbolo.usada = True
                    simbolo.inicializada = True
                    
                # Verificar la expresión del lado derecho
                self._verificar_semantica(nodo.hijos[2])
                return
        
        elif nodo.etiqueta == 'LlamadaFunc' and len(nodo.hijos) >= 4:
            nombre_func = nodo.hijos[0].simbolo_lexico
            simbolo_func = self.tabla.buscar_funcion(nombre_func)
            
            if simbolo_func is None:
                self.errores.append(f"Error. Función '{nombre_func}' no declarada")
            else:
                simbolo_func.usada = True
        
        # Verificar uso de identificadores en expresiones
        elif nodo.etiqueta == 'Termino' and len(nodo.hijos) == 1:
            hijo = nodo.hijos[0]
            if hijo.etiqueta.startswith('T_0'):
                nombre = hijo.simbolo_lexico
                simbolo = self.tabla.buscar_simbolo(nombre)
                
                if simbolo is None:
                    self.errores.append(f"Error. Identificador '{nombre}' no declarado")
                else:
                    simbolo.usada = True
                    if not simbolo.inicializada and simbolo.categoria == 'variable':
                        self.advertencias.append(
                            f"Advertencia.  Variable '{nombre}' usada sin inicializar"
                        )
        
        # Procesar hijos recursivamente
        for hijo in nodo.hijos:
            self._verificar_semantica(hijo)
    
    def _mostrar_resultados(self):
        print("\n                  RESULTADOS DEL ANÁLISIS")
        print("-"*80)
        
        if self.errores:
            print("\n❌ ERRORES SEMÁNTICOS:")
            print("-"*80)
            for i, error in enumerate(self.errores, 1):
                print(f"  {i}. {error}")
        
        if self.advertencias:
            print("\n⚠️  ADVERTENCIAS:")
            print("-"*80)
            for i, adv in enumerate(self.advertencias, 1):
                print(f"  {i}. {adv}")
        
        if not self.errores and not self.advertencias:
            print("\n✅ No se encontraron errores semánticos. El programa es semánticamente correcto")
        elif not self.errores:
            print(f"\nNo hay errores semánticos (hay {len(self.advertencias)} advertencias)")
        else:
            print(f"\nSe encontraron {len(self.errores)} errores semánticos")
        
        print("-"*80)