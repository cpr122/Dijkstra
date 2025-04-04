import os
import networkx as nx
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, render_template
import io
import base64

app = Flask(__name__)

def dijkstra_shortest_path(edges, source, target):
    # Crear el grafo
    G = nx.Graph()
    G.add_weighted_edges_from(edges)

    # Calcular la ruta más corta
    path = nx.shortest_path(G, source=source, target=target, weight='weight')
    length = nx.shortest_path_length(G, source=source, target=target, weight='weight')

    return G, path, length

def draw_graph(G, path):
    pos = nx.spring_layout(G)

    # Dibujar el grafo
    plt.figure(figsize=(6,6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000)

    # Resaltar la ruta más corta
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2.5)

    # Mostrar pesos en las aristas
    edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title("Grafo con la Ruta Más Corta")

    # Guardar la imagen en un buffer para enviarla como respuesta
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
    plt.close()

    return img_base64

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dijkstra', methods=['POST'])
def dijkstra_api():
    data = request.get_json()

    # Obtener las aristas, origen y destino del JSON
    edges = data.get('edges', [])
    source = data.get('source')
    target = data.get('target')

    if not edges or not source or not target:
        return jsonify({"error": "Faltan parámetros en la solicitud."}), 400

    # Ejecutar Dijkstra
    G, path, length = dijkstra_shortest_path(edges, source, target)

    # Dibujar el grafo
    img_base64 = draw_graph(G, path)

    # Devolver la ruta y la imagen del grafo en formato JSON
    response = {
        "path": path,
        "length": length,
        "graph_image": img_base64
    }

    return jsonify(response)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

