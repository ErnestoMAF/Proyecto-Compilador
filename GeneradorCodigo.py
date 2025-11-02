from ArbolSintactico import Nodo
from AnalizadorSemantico import TablaSimbolos, Simbolo

class GeneradorCodigo:

    def __init__(self, raiz, tabla_simbolos):
        self.raiz = raiz
        self.tabla = tabla_simbolos
        self.codigo = []
        self.datos = []
        self.label_count = 0
        self.temp_count = 0
        self.ambito_actual = 'global'
        self.mapa_variables = {}
        
    def nueva_etiqueta(self, prefijo="L"):
        """Genera una nueva etiqueta"""
        etiqueta = f"{prefijo}{self.label_count}"
        self.label_count += 1
        return etiqueta
    
    def nuevo_temporal(self):
        """Genera nombre de variable temporal"""
        temp = f"temp{self.temp_count}"
        self.temp_count += 1
        return temp
    
    def generar(self):
        """Genera el código completo en NASM para 64-bit"""
        print("\n" + "="*80)
        print("        GENERACIÓN DE CÓDIGO ENSAMBLADOR NASM (Linux 64-bit)")
        print("="*80)
        
        self.codigo.append("")
        self.codigo.append("section .data")
        self._generar_seccion_datos()
        
        # Sección BSS (variables no inicializadas)
        self.codigo.append("")
        self.codigo.append("section .bss")
        self._generar_seccion_bss()
        
        # Sección de código
        self.codigo.append("")
        self.codigo.append("section .text")
        self.codigo.append("    global _start")
        self.codigo.append("")
        self.codigo.append("_start:")
        
        # Generar código del programa
        self._generar_codigo(self.raiz)
        
        # Salir del programa (64-bit syscall)
        self.codigo.append("")
        self.codigo.append("    ; Salir del programa")
        self.codigo.append("    mov rax, 60       ; sys_exit (64-bit)")
        self.codigo.append("    xor rdi, rdi      ; código de retorno 0")
        self.codigo.append("    syscall           ; llamada al kernel 64-bit")
        
        return '\n'.join(self.codigo)
    
    def _generar_seccion_datos(self):
        """Genera la sección .data con constantes"""
        self.codigo.append("    newline: db 10")
        self.codigo.append("    msg_result: db 'Resultado: '")
        self.codigo.append("    msg_result_len: equ $-msg_result")
        
        # Variables globales inicializadas
        hay_globales = False
        for nombre, lista_simbolos in self.tabla.simbolos.items():
            for simbolo in lista_simbolos:
                if simbolo.categoria == 'variable' and simbolo.ambito == 'global':
                    hay_globales = True
                    if simbolo.tipo == 'int':
                        self.codigo.append(f"    {nombre}: dq 0    ; int {nombre}")
                        self.mapa_variables[nombre] = nombre
                    elif simbolo.tipo == 'float':
                        self.codigo.append(f"    {nombre}: dq 0    ; float {nombre}")
                        self.mapa_variables[nombre] = nombre
    
    def _generar_seccion_bss(self):
        """Genera la sección .bss para variables no inicializadas"""
        self.codigo.append("    buffer: resb 32   ; buffer para conversiones")
        
        # Buscar TODAS las variables locales de funciones
        for nombre, lista_simbolos in self.tabla.simbolos.items():
            for simbolo in lista_simbolos:
                # Variables locales (no globales)
                if simbolo.categoria == 'variable' and simbolo.ambito != 'global':
                    if nombre not in self.mapa_variables:
                        self.codigo.append(f"    {nombre}: resq 1    ; {simbolo.tipo} {nombre} (local de {simbolo.ambito})")
                        self.mapa_variables[nombre] = nombre
    
    def _generar_codigo(self, nodo):
        """Genera código recursivamente del árbol sintáctico"""
        if nodo is None:
            return
        
        # Función principal: main
        if nodo.etiqueta == 'DefFunc' and len(nodo.hijos) >= 6:
            nombre_func = nodo.hijos[1].simbolo_lexico
            
            if nombre_func.lower() == 'main':
                self.codigo.append("    ; Función main")
                self.ambito_actual = 'main'
                
                # Generar código del bloque
                bloque = nodo.hijos[5]
                self._generar_codigo(bloque)
                
                self.ambito_actual = 'global'
            return
        
        # Definición de variable local
        elif nodo.etiqueta == 'DefVar' and len(nodo.hijos) >= 4:
            tipo = nodo.hijos[0].simbolo_lexico
            nombre = nodo.hijos[1].simbolo_lexico
            
            if self.ambito_actual != 'global':
                # Agregar a mapa de variables locales (simplificado)
                self.mapa_variables[nombre] = nombre
            return
        
        # Asignación: ID = Expresion ;
        elif nodo.etiqueta == 'Sentencia' and len(nodo.hijos) >= 4:
            if nodo.hijos[1].simbolo_lexico == '=':
                nombre_var = nodo.hijos[0].simbolo_lexico
                expresion = nodo.hijos[2]
                
                self.codigo.append(f"    ; {nombre_var} = ...")
                
                # Evaluar expresión (resultado en rax)
                self._generar_expresion(expresion)
                
                # Guardar en variable
                if nombre_var in self.mapa_variables:
                    self.codigo.append(f"    mov [{self.mapa_variables[nombre_var]}], rax")
                
                return
        
        # Procesar hijos
        for hijo in nodo.hijos:
            self._generar_codigo(hijo)
    
    def _generar_expresion(self, nodo):
        """Genera código para una expresión, resultado en rax (64-bit)"""
        if nodo is None:
            return
        
        # Término simple
        if nodo.etiqueta == 'Termino':
            if len(nodo.hijos) == 1:
                hijo = nodo.hijos[0]
                
                # Identificador
                if hijo.etiqueta.startswith('T_0'):
                    nombre = hijo.simbolo_lexico
                    if nombre in self.mapa_variables:
                        self.codigo.append(f"    mov rax, [{self.mapa_variables[nombre]}]    ; cargar {nombre}")
                    return
                
                # Número entero
                elif hijo.etiqueta.startswith('T_1'):
                    valor = hijo.simbolo_lexico
                    self.codigo.append(f"    mov rax, {valor}    ; constante {valor}")
                    return
                
                # Número real (como entero)
                elif hijo.etiqueta.startswith('T_2'):
                    valor = hijo.simbolo_lexico
                    valor_int = int(float(valor))
                    self.codigo.append(f"    mov rax, {valor_int}    ; float {valor}")
                    return
        
        # Operación binaria: Expresion op Expresion
        if nodo.etiqueta == 'Expresion' and len(nodo.hijos) == 3:
            operador = nodo.hijos[1].simbolo_lexico
            
            # Evaluar primer operando
            self._generar_expresion(nodo.hijos[0])
            self.codigo.append("    push rax    ; guardar primer operando")
            
            # Evaluar segundo operando
            self._generar_expresion(nodo.hijos[2])
            self.codigo.append("    mov rbx, rax    ; segundo operando en rbx")
            self.codigo.append("    pop rax    ; recuperar primer operando")
            
            # Realizar operación
            if operador == '+':
                self.codigo.append("    add rax, rbx    ; suma")
            elif operador == '-':
                self.codigo.append("    sub rax, rbx    ; resta")
            elif operador == '*':
                self.codigo.append("    imul rbx    ; multiplicación")
            elif operador == '/':
                self.codigo.append("    cqo    ; extender signo")
                self.codigo.append("    idiv rbx    ; división")
            
            # Operaciones relacionales
            elif operador in ['<', '>', '<=', '>=', '==', '!=']:
                self.codigo.append("    cmp rax, rbx    ; comparar")
                etiqueta_true = self.nueva_etiqueta("CMP_TRUE")
                etiqueta_end = self.nueva_etiqueta("CMP_END")
                
                if operador == '<':
                    self.codigo.append(f"    jl {etiqueta_true}")
                elif operador == '>':
                    self.codigo.append(f"    jg {etiqueta_true}")
                elif operador == '<=':
                    self.codigo.append(f"    jle {etiqueta_true}")
                elif operador == '>=':
                    self.codigo.append(f"    jge {etiqueta_true}")
                elif operador == '==':
                    self.codigo.append(f"    je {etiqueta_true}")
                elif operador == '!=':
                    self.codigo.append(f"    jne {etiqueta_true}")
                
                self.codigo.append("    mov rax, 0    ; falso")
                self.codigo.append(f"    jmp {etiqueta_end}")
                self.codigo.append(f"{etiqueta_true}:")
                self.codigo.append("    mov rax, 1    ; verdadero")
                self.codigo.append(f"{etiqueta_end}:")
            
            return
        
        # Operación unaria
        if nodo.etiqueta == 'Expresion' and len(nodo.hijos) == 2:
            operador = nodo.hijos[0].simbolo_lexico
            
            if operador == '-':
                self._generar_expresion(nodo.hijos[1])
                self.codigo.append("    neg rax    ; negación")
                return
            elif operador == '!':
                self._generar_expresion(nodo.hijos[1])
                self.codigo.append("    cmp rax, 0")
                etiqueta_true = self.nueva_etiqueta("NOT_TRUE")
                etiqueta_end = self.nueva_etiqueta("NOT_END")
                self.codigo.append(f"    je {etiqueta_true}")
                self.codigo.append("    mov rax, 0")
                self.codigo.append(f"    jmp {etiqueta_end}")
                self.codigo.append(f"{etiqueta_true}:")
                self.codigo.append("    mov rax, 1")
                self.codigo.append(f"{etiqueta_end}:")
                return
        
        # Expresión entre paréntesis
        if nodo.etiqueta == 'Expresion' and len(nodo.hijos) == 3:
            if nodo.hijos[0].simbolo_lexico == '(':
                self._generar_expresion(nodo.hijos[1])
                return
        
        # Procesar primer hijo
        for hijo in nodo.hijos:
            self._generar_expresion(hijo)
            return
    
    def guardar_archivo(self, nombre_archivo="programa.asm"):
        """Guarda el código generado"""
        codigo_completo = self.generar()
        
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write(codigo_completo)
        
        print(f"\n✅ Código NASM generado en: {nombre_archivo}")
        print("\n" + "="*80)
        print("CÓDIGO GENERADO:")
        print(codigo_completo)
        print("-"*80)
        
        return codigo_completo