from AnalizadorLexico import *
from AnalizadorSintacticoLR1 import *
from Matriz import *

if __name__ == "__main__":
    cadena = input("Dame la cadena: ")
    analizador_lexico = AnalizadorLexico(cadena)
    
    if analizador_lexico.error:
        print(analizador_lexico.error)
    else:
        # Configurar matriz (igual que antes)
        matriz = Matriz(5, 4)
        valores = [ [2,0,0,1], 
                    [0,0,-1,0],
                    [0,3,-3,0],
                    [2,0,0,4],
                    [0,0,-2,0]]
        matriz.llenar(valores)
        
        tokens = analizador_lexico.obtener_todos_tokens()
        simbolos = analizador_lexico.obtener_todos_simbolos()

        analizador_sintactico = AnalizadorSintactico(matriz, tokens, simbolos)
        try:
            pasos = analizador_sintactico.analizar()
            analizador_sintactico.imprimir_pasos()
            print("Cadena aceptada")
        except SyntaxError as e:
            print("Error de sintaxis:", e)