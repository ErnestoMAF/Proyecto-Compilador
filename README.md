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

---

## Uso rápido
1. Coloca `rules.csv` en la raíz.
2. Edita `cadena` en `main.py` o pásala por entrada.
3. Ejecuta:
   python main.py
4. Revisa la traza en consola para entender shift/reduce/errores.

