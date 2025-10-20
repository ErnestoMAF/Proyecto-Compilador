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
    colores_no_terminales = {
        # Estructura principal del programa
        'programa': '#FF6B6B',          
        'Definiciones': '#4ECDC4',       
        'Definicion': '#45B7D1',         
        
        # Definiciones de variables
        'DefVar': '#96CEB4',             
        'ListaVar': '#A8E6CF',           
        
        # Definiciones de funciones
        'DefFunc': '#FFD93D',            
        'Parametros': '#FFA07A',         
        'ListaParam': '#FFDAB9',         
        'BloqFunc': '#F4A460',          
        
        # Definiciones locales
        'DefLocales': '#DDA0DD',        
        'DefLocal': '#E6B0E6',           
        
        # Sentencias
        'Sentencias': '#87CEEB',         
        'Sentencia': '#6495ED',          
        'SentenciaBloque': '#4169E1',    
        'Bloque': '#1E90FF',             
        
        # Estructuras de control
        'Otro': '#BA55D3',               
        'ValorRegresa': '#9370DB',       
        
        # Expresiones y términos
        'Expresion': '#FF69B4',          
        'Termino': '#FFB6C1',            
        
        # Llamadas a funciones y argumentos
        'LlamadaFunc': '#FFA500',        
        'Argumentos': '#FFD700',         
        'ListaArgumentos': '#F0E68C',   
        
        # Epsilon
        'ε': '#CCCCCC'                  
    }
    
    if etiqueta.startswith('T_'):
        return '#90EE90'
    
    return colores_no_terminales.get(etiqueta, '#97C2FC')  

def exportar_arbol_pyvis(raiz, nombre_salida='arbol_interactivo.html'):
    """
    Genera un árbol interactivo con pyvis a partir de la raíz tipo Nodo.
    """
    G = nx.DiGraph()
    info_nodos = {}
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
    net = Network(height='1200px', width='100%', directed=True, layout=True)
    net.from_nx(G)

    # Asignar etiquetas y colores personalizados
    for n in net.nodes:
        node_id = int(n['id'])
        info = info_nodos[node_id]
        n['label'] = info['label']
        n['font'] = {'size': 16, 'color': '#000000'}
        n['color'] = info['color']
        n['size'] = 25
        
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
   