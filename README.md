# Analizador LR(1)

**Proyecto**: Analizador léxico y sintáctico LR(1)
**Lenguaje**: Python 3.x  
**Propósito**: Conjunto de módulos para tokenizar una entrada (analizador léxico), cargar una tabla LR(1) desde CSV, y ejecutar el análisis sintáctico LR(1) mostrando pasos detallados (shift/reduce/accept) en consola.

---

## Descripción rápida
Este proyecto contiene:
- **AnalizadorLexico**: tokeniza cadenas (identificadores, números, cadenas, operadores, etc.) y asigna códigos numéricos a cada token.
- **Matriz**: clase para cargar y consultar la tabla de acciones desde un CSV.
- **Pila** y elementos (`Estado`, `Terminal`, `NoTerminal`) para modelar la pila de análisis.
- **AnalizadorSintactico**: realiza el análisis LR(1) usando la matriz (acciones) y la lista de tokens producidos por el analizador léxico. Imprime paso a paso (pila, entrada restante, lookahead y acción).
- **Estructuras**: Pila y sus elementos (Estado, Terminal, NoTerminal).

---

## Requisitos
- Python 3.8+ (probado en 3.8/3.9)  
- Las librerías estándar (`re`, `csv`, etc.).  
- Archivo `rules.csv` con la tabla LR(1).
  
---

## Tokens / Palabras reservadas (resumen)
- IDs y palabras reservadas: `if, while, return, else, int, float, void`
- Números: enteros y reales
- Cadenas: `"..."` con escapes
- Operadores: `+ - * / < > <= >= == != && || !`
- Otros: `= ; , ( ) { } $`

---

## Comportamiento clave
- `AnalizadorLexico` produce `tokens` y `simbolos`; marca `error` en caso de carácter no reconocido.
- `Matriz.llenar_desde_csv` transforma entradas como `d6`, `r6`, `acc` a valores numéricos útiles.
- `AnalizadorSintactico`:
  - Inicia con S0 en pila.
  - Consulta acción: >0 = shift (S...), 0 = error sintáctico, -1 = accept, < -1 = reducción (rN).
  - Imprime pasos con PILA, ENTRADA, LOOKAHEAD y ACCIÓN.
  - Aplica reducciones consultando GOTO y apila NoTerminal + nuevo estado.

## Formato de Salida

El sistema proporciona salida formateada que incluye diferentes tipos de acciones:

### Desplazamiento (Shift)

```
PASO 1
----------------------------------------
    PILA:      [S0]
    ENTRADA:   int x ; float y , z ; int main ( ) { x = 10 ; if ( x ) { y = 3 ; } return x ; } $
    OBJETIVO: int (token: 4)
    ACCIÓN:     🔄 DESPLAZAMIENTO → S5
```

### Reducción (Reduce)

```
PASO 8
----------------------------------------
    PILA:      [S0 int S5 x S17]
    ENTRADA:   ; float y , z ; int main ( ) { x = 10 ; if ( x ) { y = 3 ; } return x ; } $
    OBJETIVO: ; (token: 12)
    ACCIÓN:     🔽 REDUCIR R35
            *Regla aplicada: R35 → Termino(42)
            *Elementos a eliminar: 2 (símbolos y estados)
            *Estado tras reducir: S5
            * GOTO: Apilando 'Termino' y S23
```

### Aceptación

```
PASO 47
----------------------------------------
    PILA:      [S0 programa S1]
    ENTRADA:   $
    OBJETIVO: $ (token: 23)
    ACCIÓN:     ✅ ACEPTAR
================================================================================
ANÁLISIS COMPLETADO
La cadena de entrada ES SINTÁCTICAMENTE VÁLIDA
```
---

## Uso rápido
1. Coloca `rules.csv` en la raíz.
2. Edita `cadena` en `main.py` o pásala por entrada.
3. Ejecuta:
   python main.py
4. Revisa la traza en consola para entender shift/reduce/errores.

