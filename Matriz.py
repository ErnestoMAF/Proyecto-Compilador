class Matriz:
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        self.matriz = [[None] * columnas for _ in range(filas)]
    
    def llenar(self, valores):
        if len(valores) != self.filas or any(len(fila) != self.columnas for fila in valores):
            raise ValueError(f"Las dimensiones de los valores no coinciden con el tamaño de la matriz ({self.filas}x{self.columnas})")
        self.matriz = valores
    
    def consultar(self, x, y):
        if x < 0 or x >= self.filas or y < 0 or y >= self.columnas:
            raise IndexError(f"Coordenadas fuera de rango. La matriz es de {self.filas}x{self.columnas}")
        return self.matriz[x][y]
    
    def __str__(self):
        """Representación en string de la matriz para facilitar la visualización"""
        return '\n'.join([' '.join(map(str, fila)) for fila in self.matriz])

# Ejemplo de uso
if __name__ == "__main__":
    matriz = Matriz(4, 3)
    
    valores = [
        [0, 23, 'E'],
        [2, 0, 1],
        [0, -1, 0],
        [0, -2, 0],
    ]
    
    matriz.llenar(valores)
    
    # Consultar algunas coordenadas
    print("Matriz completa:")
    print(matriz)
    print("\nConsultas:")
    print(f"Posición (0,0): {matriz.consultar(0, 0)}")  # Output: 1
    print(f"Posición (1,2): {matriz.consultar(1, 2)}")  # Output: 6
