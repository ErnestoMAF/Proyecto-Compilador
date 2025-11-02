from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import io
import sys

# Importar tus módulos existentes
from AnalizadorLexico import AnalizadorLexico
from AnalizadorSintacticoLR1 import AnalizadorSintactico
from AnalizadorSemantico import AnalizadorSemantico
from GeneradorCodigo import GeneradorCodigo
from Matriz import Matriz
from ArbolSintactico import exportar_arbol_pyvis

app = Flask(__name__)
CORS(app)  # Habilitar CORS para permitir peticiones desde GitHub Pages

# Cargar matriz LR(1) al iniciar
matriz_lr1 = None

try:
    matriz_lr1 = Matriz()
    matriz_lr1.llenar_desde_csv('rules.csv')
    print(f"✅ Matriz LR(1) cargada: {matriz_lr1.filas} estados x {matriz_lr1.columnas} símbolos")
except Exception as e:
    print(f"❌ Error cargando matriz LR(1): {e}")

def serializar_nodo(nodo):
    """Convierte un Nodo del árbol en un diccionario serializable"""
    if nodo is None:
        return None
    
    return {
        'etiqueta': nodo.etiqueta,
        'simbolo_lexico': nodo.simbolo_lexico,
        'hijos': [serializar_nodo(hijo) for hijo in nodo.hijos]
    }

def deserializar_nodo(data):
    """Reconstruye un Nodo desde un diccionario"""
    from ArbolSintactico import Nodo
    
    if data is None:
        return None
    
    nodo = Nodo(data['etiqueta'], data.get('simbolo_lexico'))
    for hijo_data in data.get('hijos', []):
        hijo = deserializar_nodo(hijo_data)
        if hijo:
            nodo.agregar_hijo(hijo)
    
    return nodo

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'mensaje': 'API del Compilador LR(1) funcionando',
        'endpoints': [
            '/api/lexico',
            '/api/sintactico',
            '/api/semantico',
            '/api/generar-codigo'
        ]
    })

@app.route('/api/lexico', methods=['POST'])
def analisis_lexico():
    """Endpoint para análisis léxico"""
    try:
        data = request.get_json()
        codigo = data.get('codigo', '')
        
        if not codigo:
            return jsonify({'error': 'No se proporcionó código'}), 400
        
        analizador = AnalizadorLexico(codigo)
        
        if analizador.error:
            return jsonify({
                'error': analizador.error,
                'tokens': [],
                'simbolos': []
            })
        
        tokens = analizador.obtener_todos_tokens()
        simbolos = analizador.obtener_todos_simbolos()
        
        return jsonify({
            'tokens': tokens,
            'simbolos': simbolos,
            'total_tokens': len(tokens)
        })
    
    except Exception as e:
        return jsonify({'error': f'Error en análisis léxico: {str(e)}'}), 500

@app.route('/api/sintactico', methods=['POST'])
def analisis_sintactico():
    """Endpoint para análisis sintáctico"""
    try:
        data = request.get_json()
        tokens = data.get('tokens', [])
        simbolos = data.get('simbolos', [])
        
        if not tokens or not simbolos:
            return jsonify({'error': 'Se requieren tokens y símbolos'}), 400
        
        if matriz_lr1 is None:
            return jsonify({'error': 'Matriz LR(1) no cargada'}), 500
        
        # Capturar salida del análisis
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        analizador = AnalizadorSintactico(matriz_lr1, tokens, simbolos)
        resultado = analizador.analizar()
        
        output = captured_output.getvalue()
        sys.stdout = old_stdout
        
        if not resultado:
            return jsonify({
                'error': 'Error sintáctico detectado',
                'pasos': output.split('\n'),
                'exito': False
            })
        
        # Obtener árbol sintáctico
        arbol_serializado = None
        arbol_html = None
        
        if not analizador.pila_semantica.is_empty():
            raiz = analizador.pila_semantica.top()
            arbol_serializado = serializar_nodo(raiz)
            
            # Generar HTML del árbol
            try:
                exportar_arbol_pyvis(raiz, 'temp_arbol.html')
                with open('temp_arbol.html', 'r', encoding='utf-8') as f:
                    arbol_html = f.read()
            except Exception as e:
                print(f"No se pudo generar HTML del árbol: {e}")
        
        return jsonify({
            'exito': True,
            'pasos': output.split('\n'),
            'arbol': arbol_serializado,
            'arbol_html': arbol_html
        })
    
    except Exception as e:
        return jsonify({'error': f'Error en análisis sintáctico: {str(e)}'}), 500

@app.route('/api/semantico', methods=['POST'])
def analisis_semantico():
    """Endpoint para análisis semántico"""
    try:
        data = request.get_json()
        arbol_data = data.get('arbol')
        
        if not arbol_data:
            return jsonify({'error': 'Se requiere el árbol sintáctico'}), 400
        
        # Reconstruir árbol
        raiz = deserializar_nodo(arbol_data)
        
        # Capturar salida
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        analizador = AnalizadorSemantico(raiz)
        resultado = analizador.analizar()
        
        output = captured_output.getvalue()
        sys.stdout = old_stdout
        
        # Serializar tabla de símbolos
        tabla_simbolos_dict = {}
        for nombre, lista_simbolos in analizador.tabla.simbolos.items():
            tabla_simbolos_dict[nombre] = [
                {
                    'nombre': s.nombre,
                    'tipo': s.tipo,
                    'categoria': s.categoria,
                    'ambito': s.ambito,
                    'parametros': s.parametros if hasattr(s, 'parametros') else [],
                    'usada': s.usada if hasattr(s, 'usada') else False
                }
                for s in lista_simbolos
            ]
        
        return jsonify({
            'exito': resultado,
            'errores': analizador.errores,
            'advertencias': analizador.advertencias,
            'tabla_simbolos': tabla_simbolos_dict,
            'salida': output.split('\n')
        })
    
    except Exception as e:
        return jsonify({'error': f'Error en análisis semántico: {str(e)}'}), 500

@app.route('/api/generar-codigo', methods=['POST'])
def generar_codigo():
    """Endpoint para generación de código"""
    try:
        data = request.get_json()
        arbol_data = data.get('arbol')
        tabla_data = data.get('tabla_simbolos')
        
        if not arbol_data:
            return jsonify({'error': 'Se requiere el árbol sintáctico'}), 400
        
        # Reconstruir árbol
        raiz = deserializar_nodo(arbol_data)
        
        # Reconstruir tabla de símbolos
        from AnalizadorSemantico import TablaSimbolos, Simbolo
        tabla = TablaSimbolos()
        
        if tabla_data:
            for nombre, lista_simbolos in tabla_data.items():
                for s_data in lista_simbolos:
                    simbolo = Simbolo(
                        nombre=s_data['nombre'],
                        tipo=s_data['tipo'],
                        categoria=s_data['categoria'],
                        ambito=s_data['ambito']
                    )
                    if 'parametros' in s_data:
                        simbolo.parametros = s_data['parametros']
                    tabla.agregar_simbolo(simbolo)
        
        # Generar código
        generador = GeneradorCodigo(raiz, tabla)
        codigo_nasm = generador.generar()
        
        return jsonify({
            'exito': True,
            'codigo': codigo_nasm
        })
    
    except Exception as e:
        return jsonify({'error': f'Error en generación de código: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud para Render"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Para desarrollo local
    app.run(debug=True, host='0.0.0.0', port=5000)
    
    # Para producción en Render, usa:
    # gunicorn app:app