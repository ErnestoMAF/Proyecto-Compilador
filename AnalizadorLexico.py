import re

class AnalizadorLexico:
    def __init__(self, cadena):
        self.tokens = []
        self.error = False
        
        # Palabras reservadas con sus tipos
        self.palabras_reservadas = {
            'if': 19,
            'while': 20, 
            'return': 21,
            'else': 22,
            'int': 4,
            'float': 4,
            'void': 4
        }
        
        # Expresión regular para todos los tokens
        regex = re.compile(
            r"""
            (<=|>=|==|!=) |           # Operadores relacionales/igualdad de 2 caracteres
            (&&) |                    # Operador And
            (\|\|) |                  # Operador Or  
            ([A-Za-z][A-Za-z0-9]*) |  # Identificadores y palabras reservadas
            (\d+\.\d+) |              # Números reales
            (\d+) |                   # Números enteros
            ([+\-]) |                 # Operadores de suma
            ([*/]) |                  # Operadores de multiplicación
            ([<>]) |                  # Operadores relacionales simples
            (!) |                     # Operador Not
            (=) |                     # Operador de asignación
            (;) |                     # Punto y coma
            (,) |                     # Coma
            (\() |                    # Paréntesis izquierdo
            (\)) |                    # Paréntesis derecho
            (\{) |                    # Llave izquierda
            (\}) |                    # Llave derecha
            (\$) |                    # Símbolo $
            (\S)                      # Cualquier otro carácter (error)
            """,
            re.VERBOSE,
        )

        for match in regex.finditer(cadena):
            grupos = match.groups()
            
            if grupos[0]:  # Operadores relacionales/igualdad de 2 caracteres
                if grupos[0] in ['<=', '>=']:
                    self.tokens.append(7)  # opRelac
                elif grupos[0] in ['==', '!=']:
                    self.tokens.append(11)  # opIgualdad
                    
            elif grupos[1]:  # Operador And
                self.tokens.append(9)
                
            elif grupos[2]:  # Operador Or
                self.tokens.append(8)
                
            elif grupos[3]:  # Identificadores y palabras reservadas
                palabra = grupos[3]
                if palabra in self.palabras_reservadas:
                    self.tokens.append(self.palabras_reservadas[palabra])
                else:
                    self.tokens.append(0)  # Identificador
                    
            elif grupos[4]:  # Número real
                self.tokens.append(2)
                
            elif grupos[5]:  # Número entero
                self.tokens.append(1)
                
            elif grupos[6]:  # Operadores de suma
                self.tokens.append(5)
                
            elif grupos[7]:  # Operadores de multiplicación
                self.tokens.append(6)
                
            elif grupos[8]:  # Operadores relacionales simples
                self.tokens.append(7)
                
            elif grupos[9]:  # Operador Not
                self.tokens.append(10)
                
            elif grupos[10]:  # Operador de asignación
                self.tokens.append(18)
                
            elif grupos[11]:  # Punto y coma
                self.tokens.append(12)
                
            elif grupos[12]:  # Coma
                self.tokens.append(13)
                
            elif grupos[13]:  # Paréntesis izquierdo
                self.tokens.append(14)
                
            elif grupos[14]:  # Paréntesis derecho
                self.tokens.append(15)
                
            elif grupos[15]:  # Llave izquierda
                self.tokens.append(16)
                
            elif grupos[16]:  # Llave derecha
                self.tokens.append(17)
                
            elif grupos[17]:  # Símbolo $
                self.tokens.append(23)
                
            elif grupos[18] and not grupos[18].isspace():  # Error
                self.error ="ERROR LÉXICO: " + grupos[18]
                self.tokens.clear()

    def ver_token(self, pos):
        return self.tokens[pos] if pos < len(self.tokens) else None
    
    def obtener_todos_tokens(self):
        return self.tokens

# Ejemplos de prueba
if __name__ == "__main__":
    cadena = """ x = 5;
            y = 20;
            if (x == y || z > 0){ 
                a = !b; 
            }
        """
    analizador = AnalizadorLexico(cadena)
    
    if not analizador.error:
        print("CADENA: ",cadena)
        print(analizador.obtener_todos_tokens())
    else:
        print(analizador.error)
