# Analizador Léxico

Este proyecto implementa un analizador léxico sencillo en Python, que toma una cadena de texto como entrada y devuelve una lista de tokens. Los tokens corresponden a diferentes tipos de elementos del lenguaje, como identificadores, operadores, palabras reservadas y constantes.

## Descripción

El analizador léxico está diseñado para reconocer y clasificar los siguientes elementos de un lenguaje simple de programación:

- **Palabras reservadas**: `if`, `while`, `return`, `else`, `int`, `float`, `void`
- **Operadores aritméticos**: `+`, `-`, `*`, `/`
- **Operadores relacionales**: `<=`, `>=`, `==`, `!=`, `<`, `>`
- **Operadores lógicos**: `&&`, `||`, `!`
- **Otros tokens**: Identificadores, números enteros, números reales, operadores de asignación (`=`), punto y coma (`;`), comas (`,`), paréntesis y llaves.

## Requisitos

- Python 3.x

## Uso

### Clase `AnalizadorLexico`

La clase principal es `AnalizadorLexico`, que recibe una cadena de texto y devuelve una lista de tokens clasificados según el tipo correspondiente mediante expresiones regulares.

### Métodos

- **`__init__(self, cadena)`**: Constructor de la clase que toma una cadena y la procesa para generar los tokens.
- **`siguiente_token(self)`**: Retorna el siguiente token disponible en la lista de tokens.
- **`ver_token(self)`**: Muestra el token actual sin avanzar en la lista.
- **`obtener_todos_tokens(self)`**: Devuelve todos los tokens procesados.
- **`obtener_nombre_tipo(self, tipo)`**: Devuelve el nombre descriptivo del tipo de un token dado.

### Ejemplo de salida

<img width="416" height="568" alt="image" src="https://github.com/user-attachments/assets/58bee728-ee2c-4572-860e-1156023fcff1" />
