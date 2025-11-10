from AnalizadorLexico import *
from AnalizadorSintacticoLR1 import *
from AnalizadorSemantico import *
from Matriz import *
from GeneradorCodigo import *

if __name__ == "__main__":
    #cadena = input("Dame la cadena: ")
    cadena = """
                int a;
                int suma(int a, int b){
                return a+b;
                }

                int main(){
                float a;
                int b;
                int c;
                c = a+b;
                c = suma(8,9);
                }
            """
    print(f"CADENA: {cadena}")
    analizador_lexico = AnalizadorLexico(cadena)
    
    if analizador_lexico.error:
        print(analizador_lexico.error)
    else:
        tokens = analizador_lexico.obtener_todos_tokens()
        simbolos = analizador_lexico.obtener_todos_simbolos()
        print(f"\nTOKENS IDENTIFICADOS: {len(tokens)} tokens")
        print("-"*80)
        for i, (token, simbolo) in enumerate(zip(tokens, simbolos)):
            print(f"  {i+1:2d}. Token: {token:2d} → '{simbolo}'")

        try:
            matriz = Matriz()
            matriz.llenar_desde_csv('rules.csv')
            print(f"\nMatriz LR(1) cargada: {matriz.filas} estados x {matriz.columnas} símbolos")

            analizador_sintactico = AnalizadorSintactico(matriz, tokens, simbolos)
            pasos = analizador_sintactico.analizar()
        except FileNotFoundError:
            print("ERROR: No se pudo encontrar el archivo 'rules.csv'")
        except Exception as error_inesperado:
            print(f"ERROR durante el análisis sintáctico:")
            print(f"   Tipo de error: {type(error_inesperado).__name__}")
            print(f"   Descripción: {str(error_inesperado)}")
        
        if not analizador_sintactico.pila_semantica.is_empty():
            raiz_arbol = analizador_sintactico.pila_semantica.top()
            
            analizador_semantico = AnalizadorSemantico(raiz_arbol)
            resultado_semantico = analizador_semantico.analizar()

            if not resultado_semantico:
                    print("\nERROR: Compilación terminada con errores semánticos")
                    exit(1)
            else:
                    generador = GeneradorCodigo(raiz_arbol, analizador_semantico.tabla)
                    codigo_mips = generador.guardar_archivo("programa.asm")
                    print("\n" + "="*80)
                    print("                    COMPILACIÓN EXITOSA ")
                    print("="*80)
                    print("\nTodas las fases completadas correctamente:")
                    print("   • Análisis Léxico: OK")
                    print("   • Análisis Sintáctico: OK")
                    print("   • Análisis Semántico: OK")
                    print("   • Árbol Sintáctico: arbol_interactivo.html")
                    print("   • Código NASM estándar generado en: programa.asm")
                    print("="*80)
        else:
            print("\nERROR: No se construyó árbol sintáctico")