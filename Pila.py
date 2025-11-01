class Pila:
    def __init__(self):
        self.items = []

    def push(self, item):
        """Añadir un elemento al final de la lista"""
        self.items.append(item)

    def pop(self):
        """Eliminar y devolver el último elemento de la pila"""
        if not self.is_empty():
            return self.items.pop()
        else:
            raise IndexError("Pila vacía")

    def top(self):
        """Obtener el último elemento sin eliminarlo"""
        if not self.is_empty():
            return self.items[-1]
        else:
            raise IndexError("Pila vacía")

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

class ElementoPila:
    def __init__(self, valor):
        self.valor = valor
    
    def __str__(self):
        return str(self.valor)

class Terminal(ElementoPila):
    def __init__(self, valor):
        super().__init__(valor)

class NoTerminal(ElementoPila):
    def __init__(self, valor):
        super().__init__(valor)

class Estado(ElementoPila):
    def __init__(self, valor):
        super().__init__(valor)

if __name__ == "__main__":
    pila = Pila()

    # Operaciones de pila
    pila.push(10)
    pila.push(20)
    pila.push(30)

    print("Último elemento (top):", pila.top())  # 30
    print("Tamaño de la pila:", pila.size())  # 3

    print("Elemento eliminado (pop):", pila.pop())  # 30
    print("Tamaño de la pila después del pop:", pila.size())  # 2

    print("¿La pila está vacía?", pila.is_empty())  # False

