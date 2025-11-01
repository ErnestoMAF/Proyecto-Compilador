import csv

class Matriz:
    def __init__(self):
        self.matriz = []
        self.filas = 0
        self.columnas = 0
    
    def llenar(self, valores):
        if len(valores) != self.filas or any(len(fila) != self.columnas for fila in valores):
            raise ValueError(f"Las dimensiones de los valores no coinciden con el tamaño de la matriz ({self.filas}x{self.columnas})")
        self.matriz = valores

    def llenar_desde_csv(self, file_path):
        """
        Lee un archivo CSV y llena la matriz manteniendo la correspondencia correcta:
        - Token 4 (tipo) debe buscar en columna 5
        - Token 0 (identificador) debe buscar en columna 1  
        - No terminal 'programa' (24) debe buscar en columna 25
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Almacenamos los datos temporalmente
                temp_data = [row for row in reader]

            # Ignorar la primera fila (encabezados)
            if len(temp_data) > 0:
                temp_data = temp_data[1:]

            # Procesar las filas manteniendo la estructura correcta
            self.matriz = []
            for fila in temp_data:
                nueva_fila = []
                # Procesar TODAS las columnas desde la 1 (ignorar solo la columna 0 de numeración)
                for i in range(1, len(fila)):
                    valor = fila[i]
                    if valor == '':
                        nueva_fila.append(0)
                    else:
                        try:
                            # Manejar valores como 'd6', 'r6', 'acc', etc.
                            if valor.startswith('d'):
                                nueva_fila.append(int(valor[1:]))
                            elif valor.startswith('r'):
                                regla_num = int(valor[1:])
                                nueva_fila.append(-(regla_num + 1))  # r0 -> -1, etc.
                            elif valor == 'acc':
                                nueva_fila.append(-1)  # Aceptación
                            else:
                                nueva_fila.append(int(valor))
                        except ValueError:
                            nueva_fila.append(0)
                self.matriz.append(nueva_fila)

            self.filas = len(self.matriz)
            if self.filas > 0:
                self.columnas = len(self.matriz[0])
            else:
                self.columnas = 0

        except FileNotFoundError:
            raise FileNotFoundError(f"El archivo '{file_path}' no fue encontrado.")
        except IndexError:
            raise IndexError("El archivo CSV está vacío o tiene un formato incorrecto.")

    def consultar(self, x, y):
        """
        Consulta la matriz usando las coordenadas EXACTAS como vienen.
        x = fila (estado)
        y = columna (token o no terminal)
        """
        if x < 0 or x >= self.filas or y < 0 or y >= self.columnas:
            raise IndexError(f"Coordenadas fuera de rango. La matriz es de {self.filas}x{self.columnas}")
        return self.matriz[x][y]  # Ya está en el formato correcto después del procesamiento en llenar_desde_csv
        
    def __str__(self):
        """Representación en string de la matriz para facilitar la visualización"""
        return '\n'.join([' '.join(map(str, fila)) for fila in self.matriz])
