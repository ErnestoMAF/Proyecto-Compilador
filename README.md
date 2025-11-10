# Compilador LR(1) Completo

**Proyecto:** Compilador completo con análisis léxico, sintáctico LR(1), semántico y generación de código NASM  
**Lenguaje:** Python 3.x  
**Propósito:** Sistema integral para tokenizar entrada, ejecutar análisis sintáctico LR(1) con tabla desde CSV, verificar semántica, y generar código ensamblador, con visualización interactiva del árbol sintáctico usando PyVis.

---

## Descripción General

Este proyecto implementa un **compilador completo** que procesa código fuente en 4 fases:

1. **Analizador Léxico** - Tokeniza la entrada
2. **Analizador Sintáctico LR(1)** - Valida estructura gramatical y genera árbol sintáctico
3. **Analizador Semántico** - Verifica tipos, declaraciones y uso de símbolos
4. **Generador de Código** - Produce código ensamblador NASM (x86-64)

### Componentes Principales

* **AnalizadorLexico**: Tokeniza cadenas (identificadores, números, cadenas, operadores, etc.) y asigna códigos numéricos a cada token.
* **Matriz**: Clase para cargar y consultar la tabla de acciones LR(1) desde un CSV.
* **Pila**: Estructura de datos con elementos `Estado`, `Terminal`, `NoTerminal` para modelar la pila de análisis.
* **AnalizadorSintactico**: Realiza el análisis LR(1) usando la matriz de acciones y la lista de tokens. Imprime paso a paso (pila, entrada restante, lookahead y acción). Construye el árbol sintáctico mediante una pila semántica.
* **ArbolSintactico**: Genera un árbol interactivo HTML con PyVis para visualizar la estructura sintáctica.
* **AnalizadorSemantico**: Construye tabla de símbolos, verifica tipos de datos, detecta variables no declaradas/no usadas y valida llamadas a funciones.
* **GeneradorCodigo**: Traduce el árbol sintáctico a código ensamblador NASM para arquitectura x86-64 Linux.

---

## Requisitos

### Software
* Python 3.8+
* pip

### Dependencias
```bash
pip install pyvis networkx flask flask-cors
```

### Archivos Necesarios
* `rules.csv` - Tabla LR(1) con las acciones y transiciones del autómata

---

## Tokens / Palabras Reservadas

### Palabras Reservadas
* **Tipos de datos:** `int`, `float`, `void`
* **Control de flujo:** `if`, `else`, `while`, `return`

### Literales
* **Identificadores:** `[A-Za-z][A-Za-z0-9]*`
* **Números enteros:** `\d+`
* **Números reales:** `\d+\.\d+`
* **Cadenas:** `"..."`

### Operadores
* **Aritméticos:** `+`, `-`, `*`, `/`
* **Relacionales:** `<`, `>`, `<=`, `>=`
* **Igualdad:** `==`, `!=`
* **Lógicos:** `&&`, `||`, `!`
* **Asignación:** `=`

### Delimitadores
* **Puntuación:** `;`, `,`
* **Agrupación:** `(`, `)`, `{`, `}`
* **Fin de entrada:** `$`

---

## Comportamiento del Sistema

### 1. Análisis Léxico
* `AnalizadorLexico` produce listas `tokens` y `simbolos`
* Marca `error` en caso de carácter no reconocido
* Asigna códigos numéricos a cada tipo de token

### 2. Análisis Sintáctico
* `Matriz.llenar_desde_csv` transforma entradas como `d6`, `r6`, `acc` a valores numéricos
* `AnalizadorSintactico`:
  * Inicia con S0 en la pila de estados
  * Usa dos pilas:
    * `pila_estados`: para manejar el autómata LR(1)
    * `pila_semantica`: para construir el árbol sintáctico
  * Consulta acción:
    * `> 0` → desplazamiento (shift)
    * `0` → error sintáctico
    * `-1` → aceptar
    * `< -1` → reducción (reduce R#)
  * Durante las reducciones:
    * Toma hijos de la pila semántica
    * Crea nodos `Nodo(etiqueta=NoTerminal)`
    * Forma el árbol sintáctico completo
  * Al final, genera archivo HTML con árbol sintáctico visual

### 3. Análisis Semántico
* **Primera pasada:** Construye tabla de símbolos
  * Registra variables globales/locales
  * Registra funciones con sus parámetros
  * Detecta redeclaraciones
* **Segunda pasada:** Verifica semántica
  * Valida uso de variables declaradas
  * Detecta variables no inicializadas
  * Verifica llamadas a funciones existentes
  * Marca símbolos como usados

### 4. Generación de Código
* Traduce el árbol sintáctico a NASM x86-64
* Genera secciones:
  * `.data` - Variables globales y constantes
  * `.bss` - Variables no inicializadas
  * `.text` - Código ejecutable
* Soporta:
  * Operaciones aritméticas (`+`, `-`, `*`, `/`)
  * Operaciones relacionales (`<`, `>`, `<=`, `>=`, `==`, `!=`)
  * Operaciones unarias (`-`, `!`)
  * Asignaciones de variables
  * Expresiones complejas

---

## Formato de Salida

### Terminal

#### Desplazamiento (Shift)
```
📍 PASO 1
----------------------------------------
    PILA:      [S0]
    ENTRADA:   int x ; float y , z ; int main ( ) { x = 10 ; if ( x ) { y = 3 ; } return x ; } $
    OBJETIVO: int (token: 4)
    ACCIÓN:     🔄 DESPLAZAMIENTO → S5
```

#### Reducción (Reduce)
```
📍 PASO 8
----------------------------------------
    PILA:      [S0 int S5 x S17]
    ENTRADA:   ; float y , z ; int main ( ) { x = 10 ; if ( x ) { y = 3 ; } return x ; } $
    OBJETIVO: ; (token: 12)
    ACCIÓN:     🔽 REDUCIR R35
            *Regla aplicada: R35 → Termino(42)
            *Elementos a eliminar: 2 (símbolos y estados)
            *Estado tras reducir: S5
            * GOTO: Apilando 'Termino' y S23
 * Nodo creado: Termino
```

#### Aceptación
```
📍 PASO 47
----------------------------------------
    PILA:      [S0 programa S1]
    ENTRADA:   $
    OBJETIVO: $ (token: 23)
    ACCIÓN:     ✅ ACEPTAR
================================================================================

ANÁLISIS COMPLETADO
La cadena de entrada ES SINTÁCTICAMENTE VÁLIDA
ÁRBOL SINTÁCTICO GENERADO EN: arbol_interactivo.html
```

### Análisis Semántico
```
================================================================================
                  ANÁLISIS SEMÁNTICO
================================================================================

Construyendo tabla de símbolos...
Verificando tipos y su uso...

--------------------------------------------------------------------------------
                    TABLA DE SÍMBOLOS

FUNCIONES:
--------------------------------------------------------------------------------
  • int main()

VARIABLES:
--------------------------------------------------------------------------------
  • int a [main] - ✓ usada
  • int b [main] - ✓ usada

                  RESULTADOS DEL ANÁLISIS
--------------------------------------------------------------------------------

✅ No se encontraron errores semánticos. El programa es semánticamente correcto
--------------------------------------------------------------------------------
```

### Código Generado
```nasm
section .data
    newline: db 10
    msg_result: db 'Resultado: '
    msg_result_len: equ $-msg_result
    
section .bss
    a: resq 1    ; int a (local de main)
    b: resq 1    ; int b (local de main)
    
section .text
    global _start
    
_start:
    ; Función main
    ; a = 5
    mov rax, 5    ; constante 5
    mov [a], rax
    
    ; a = a + 5
    mov rax, [a]    ; cargar a
    push rax    ; guardar primer operando
    mov rax, 5    ; constante 5
    mov rbx, rax    ; segundo operando en rbx
    pop rax    ; recuperar primer operando
    add rax, rbx    ; suma
    mov [a], rax
    
    ; Salir del programa
    mov rax, 60       ; sys_exit (64-bit)
    xor rdi, rdi      ; código de retorno 0
    syscall           ; llamada al kernel 64-bit
```

### Gráfico (Árbol Sintáctico)

El árbol sintáctico se genera en formato HTML interactivo con PyVis, mostrando:
* **Nodos de colores** según el tipo de símbolo no-terminal
* **Estructura jerárquica** del análisis
* **Información al pasar el mouse** sobre cada nodo
* **Navegación y zoom** interactivos

<img width="480" height="681" alt="image" src="https://github.com/user-attachments/assets/8f062337-5487-497d-8717-375ef2f415ca" />


---

## Uso Local (Terminal)

### 1. Preparación
```bash
# Clonar o descargar el repositorio
git clone https://github.com/tu-usuario/compilador-lr1.git
cd compilador-lr1

# Instalar dependencias
pip install pyvis networkx
```
### 2. Editar Código Fuente
En `Compilador.py`, modifica la variable `cadena`:

```python
cadena = """
int main(){
    int a;
    int b;
    a = 5;
    b = 10;
    a = a + b;
}
"""
```

### 3. Ejecutar
```bash
python Compilador.py
```

### 4. Revisar Resultados
* **Consola:** Traza completa del análisis (tokens, pasos sintácticos, tabla de símbolos, código NASM)
* **Archivo HTML:** `arbol_interactivo.html` con el árbol sintáctico visual
* **Archivo ASM:** `programa.asm` con el código ensamblador generado

---

## App Web

El proyecto incluye una **aplicación web completa** para usar el compilador desde el navegador.


### Componentes Web

#### Frontend
* **Ubicación:** `docs/index.html`
* **Tecnología:** HTML5, CSS3, JavaScript vanilla
* **Características:**
  * Editor de código integrado
  * Visualización de resultados en tiempo real
  * Árbol sintáctico interactivo embebido
    
#### Backend
* **Ubicación:** `backend/app.py`
* **Tecnología:** Flask + Flask-CORS
* **Endpoints:**
  * `POST /api/lexico` - Análisis léxico
  * `POST /api/sintactico` - Análisis sintáctico + árbol
  * `POST /api/semantico` - Análisis semántico
  * `POST /api/generar-codigo` - Generación de código NASM
* **Características:**
  * CORS habilitado para GitHub Pages
  * Serialización de árbol sintáctico

### Acceso Rápido
**🔗 Demo en vivo:** [App Compilador](https://ernestomaf.github.io/Proyecto-Compilador/)

---

## 📝 Ejemplo de Código Soportado

```c
int a;

int suma(int x, int y){
    return x + y;
}

int main(){
    int resultado;
    a = 10;
    resultado = suma(a, 5);
    
    if (resultado > 10) {
        resultado = resultado * 2;
    } else {
        resultado = resultado + 1;
    }
    
    while (a < 100) {
        a = a + 1;
    }
    
    return resultado;
}
```

---

## 👥 Autor
##### Ernesto Macias Flores


