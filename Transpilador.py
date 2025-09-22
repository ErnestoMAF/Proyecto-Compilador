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
    cadena = "int x=4;"

    analizador_lexico = AnalizadorLexico(cadena)
    
    if analizador_lexico.error:
        print(analizador_lexico.error)
    else:
        tokens = analizador_lexico.obtener_todos_tokens()
        simbolos = analizador_lexico.obtener_todos_simbolos()

        try:
            matriz = Matriz()
            matriz.llenar_desde_csv('rules.csv')
            print(f"✅ Matriz LR(1) cargada exitosamente: {matriz.filas} estados x {matriz.columnas} símbolos")

            analizador_sintactico = AnalizadorSintactico(matriz, tokens, simbolos)
            pasos = analizador_sintactico.analizar()
        except FileNotFoundError:
            print("ERROR: No se pudo encontrar el archivo 'rules.csv'")
        except Exception as error_inesperado:
            print(f"ERROR INESPERADO durante el análisis sintáctico:")
            print(f"   Tipo de error: {type(error_inesperado).__name__}")
            print(f"   Descripción: {str(error_inesperado)}")