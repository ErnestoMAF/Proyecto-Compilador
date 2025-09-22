from AnalizadorLexico import *
from AnalizadorSintacticoLR1 import *
from Matriz import *

if __name__ == "__main__":
    #cadena = input("Dame la cadena: ")
    cadena = """    int x;
                    float y, z;
                    int main() {
                        x = 10;
                        if (x) { y = 3; }
                        return x;
                    }
            """

    analizador_lexico = AnalizadorLexico(cadena)
    
    if analizador_lexico.error:
        print(analizador_lexico.error)
    else:
        # Configurar matriz (igual que antes)
        matriz = Matriz()
        matriz.llenar_desde_csv('rules.csv')

        tokens = analizador_lexico.obtener_todos_tokens()
        simbolos = analizador_lexico.obtener_todos_simbolos()

        analizador_sintactico = AnalizadorSintactico(matriz, tokens, simbolos)
        try:
            pasos = analizador_sintactico.analizar()
            analizador_sintactico.imprimir_pasos()
            print("Cadena aceptada")
        except SyntaxError as e:
            print("Error de sintaxis:", e)
