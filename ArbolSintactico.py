from pyvis.network import Network
import networkx as nx

class Nodo:
    def __init__(self, etiqueta, simbolo_lexico=None):
        self.etiqueta = etiqueta
        self.simbolo_lexico = simbolo_lexico
        self.hijos = []

    def agregar_hijo(self, nodo):
        self.hijos.append(nodo)

    def __repr__(self):
        if self.simbolo_lexico is not None:
            return f"{self.simbolo_lexico}"
        return f"{self.etiqueta}"

def obtener_color_nodo(etiqueta):
    """
    Determina el color del nodo según el NO TERMINAL (regla gramatical):
    """
    colores_no_terminales = {
        # Estructura principal del programa
        'programa': '#FF6B6B',           # Rojo coral
        'Definiciones': '#4ECDC4',       # Turquesa
        'Definicion': '#45B7D1',         # Azul cielo
        
        # Definiciones de variables
        'DefVar': '#96CEB4',             # Verde menta
        'ListaVar': '#A8E6CF',           # Verde claro
        
        # Definiciones de funciones
        'DefFunc': '#FFD93D',            # Amarillo
        'Parametros': '#FFA07A',         # Salmón
        'ListaParam': '#FFDAB9',         # Durazno
        'BloqFunc': '#F4A460',           # Naranja arena
        
        # Definiciones locales
        'DefLocales': '#DDA0DD',         # Ciruela
        'DefLocal': '#E6B0E6',           # Orquídea
        
        # Sentencias
        'Sentencias': '#87CEEB',         # Azul cielo claro
        'Sentencia': '#6495ED',          # Azul aciano
        'SentenciaBloque': '#4169E1',    # Azul real
        'Bloque': '#1E90FF',             # Azul dodger
        
        # Estructuras de control
        'Otro': '#BA55D3',               # Orquídea medio
        'ValorRegresa': '#9370DB',       # Púrpura medio
        
        # Expresiones y términos
        'Expresion': '#FF69B4',          # Rosa fuerte
        'Termino': '#FFB6C1',            # Rosa claro
        
        # Llamadas a funciones y argumentos
        'LlamadaFunc': '#FFA500',        # Naranja
        'Argumentos': '#FFD700',         # Dorado
        'ListaArgumentos': '#F0E68C',    # Caqui
        
        # Epsilon
        'ε': '#CCCCCC'                   # Gris
    }
    
    # Si es un terminal (empieza con T_), color verde
    if etiqueta.startswith('T_'):
        return '#90EE90'  # Verde claro para terminales
    
    # Retornar color según el no terminal
    return colores_no_terminales.get(etiqueta, '#97C2FC')  # Azul por defecto

def exportar_arbol_pyvis(raiz, nombre_salida='arbol_interactivo.html'):
    """
    Genera un árbol interactivo con pyvis a partir de la raíz tipo Nodo.
    Colores según el NO TERMINAL (regla gramatical).
    """
    G = nx.DiGraph()
    info_nodos = {}  # Guardará (etiqueta, simbolo_lexico, color)
    contador = {'n': 0}

    def agregar_nodo(nodo, padre=None):
        contador['n'] += 1
        id_n = contador['n']
        label = nodo.etiqueta if nodo.simbolo_lexico is None else f"{nodo.simbolo_lexico}"
        color = obtener_color_nodo(nodo.etiqueta)
        
        G.add_node(id_n)
        info_nodos[id_n] = {
            'label': label,
            'etiqueta': nodo.etiqueta,
            'simbolo': nodo.simbolo_lexico,
            'color': color
        }
        
        if padre is not None:
            G.add_edge(padre, id_n)
        
        for hijo in nodo.hijos:
            agregar_nodo(hijo, id_n)
        
        return id_n

    agregar_nodo(raiz, None)

    # Crear red de pyvis con disposición jerárquica
    net = Network(height='1000px', width='100%', directed=True, layout=True)
    net.from_nx(G)

    # Asignar etiquetas y colores personalizados
    for n in net.nodes:
        node_id = int(n['id'])
        info = info_nodos[node_id]
        n['label'] = info['label']
        n['font'] = {'size': 16, 'color': '#000000'}
        n['color'] = info['color']
        n['size'] = 25
        
        # Agregar título (tooltip) con información adicional
        if info['simbolo']:
            n['title'] = f"Regla: {info['etiqueta']}\nValor: {info['simbolo']}"
        else:
            n['title'] = f"No Terminal: {info['etiqueta']}"

    # Configurar layout jerárquico (árbol)
    net.set_options("""
    {
        "layout": {
            "hierarchical": {
                "enabled": true,
                "direction": "UD",
                "sortMethod": "directed",
                "nodeSpacing": 150,
                "levelSeparation": 200,
                "treeSpacing": 200
            }
        },
        "physics": {
            "enabled": false,
            "hierarchicalRepulsion": {
                "nodeDistance": 150
            }
        },
        "edges": {
            "smooth": {
                "type": "cubicBezier",
                "forceDirection": "vertical"
            },
            "arrows": {
                "to": {
                    "enabled": true,
                    "scaleFactor": 0.5
                }
            }
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 100
        }
    }
    """)

    # Guardar el archivo HTML directamente
    net.save_graph(nombre_salida)
   