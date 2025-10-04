# Analizador LR(1)

**Proyecto**: Analizador léxico y sintáctico LR(1)
**Lenguaje**: Python 3.x  
**Propósito**: Conjunto de módulos para tokenizar una entrada (analizador léxico), cargar una tabla LR(1) desde CSV, ejecutar el análisis sintáctico LR(1) mostrando pasos detallados (shift/reduce/accept) en consola, y generar un árbol sintáctico interactivo con PyVis.

---

## Descripción rápida
Este proyecto contiene:
- **AnalizadorLexico**: tokeniza cadenas (identificadores, números, cadenas, operadores, etc.) y asigna códigos numéricos a cada token.
- **Matriz**: clase para cargar y consultar la tabla de acciones desde un CSV.
- **Pila** y elementos (`Estado`, `Terminal`, `NoTerminal`) para modelar la pila de análisis.
- **AnalizadorSintactico**: realiza el análisis LR(1) usando la matriz (acciones) y la lista de tokens producidos por el analizador léxico. Imprime paso a paso (pila, entrada restante, lookahead y acción).  
  Además, construye el **árbol sintáctico** mediante una pila semántica.
- **ArbolSintactico**: genera un **árbol interactivo HTML** con la librería PyVis para visualizar la estructura sintáctica generada.

---

## Requisitos
- Python 3.8+ (probado en 3.8/3.9)  
- Las librerías estándar (`re`, `csv`, etc.).  
- Archivo `rules.csv` con la tabla LR(1).
- pip install pyvis networkx
  
---

## Tokens / Palabras reservadas
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
  - Inicia con **S0** en la pila de estados.
  - Usa **dos pilas**:
    - `pila_estados`: para manejar el autómata LR(1).
    - `pila_semantica`: para construir el árbol sintáctico.
  - Consulta acción:  
    - >0 → *shift (desplazamiento)*  
    - 0 → *error sintáctico*  
    - -1 → *aceptar*  
    - <-1 → *reducción (R#)*  
  - Durante las reducciones, toma los hijos de la pila semántica y crea nodos `Nodo(etiqueta=NoTerminal)` para formar el árbol.
  - Al final, genera automáticamente **`arbol_interactivo.html`** con el árbol sintáctico visual.

---

## Formato de Salida

### Terminal
El sistema proporciona salida formateada que incluye diferentes tipos de acciones:

#### Desplazamiento (Shift)

```
PASO 1
----------------------------------------
    PILA:      [S0]
    ENTRADA:   int x ; float y , z ; int main ( ) { x = 10 ; if ( x ) { y = 3 ; } return x ; } $
    OBJETIVO: int (token: 4)
    ACCIÓN:     🔄 DESPLAZAMIENTO → S5
```

#### Reducción (Reduce)

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

#### Aceptación

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

### Gráfico (Árbol Sintáctico)
<img width="480" height="681" alt="image" src="https://github.com/user-attachments/assets/08a92864-ad22-49bf-b0e0-198bd285abd0" />

<img width="954" height="830" alt="image" src="https://github.com/user-attachments/assets/b9c35d1a-b2d4-4a03-9c33-3cdccf1fead3" />


---

## Uso rápido
1. Coloca `rules.csv` en la raíz.
2. Instala las bibliotecas externas con ```pip install pyvis networkx```
3. Edita o utiliza el valor de `cadena` en Transpilador.py.
4. Ejecuta:
   python Transpilador.py
5. Revisa la traza en consola para entender shift/reduce/errores.
6. Abre el archivo .html generado con tu navegador preferido para ver el gráfico.

