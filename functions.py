'''
File che contiene le funzioni comuni usate:
- Classe Graph: creazione dei grafi
- draw_with_steiner_tree: disegnare il grafo con steiner tree sovrapposto
- create_graph: crea il grafico leggendo un file
- draw_row_graph: fa una riga con i 3 grafici di interesse
'''

import networkx as nx
import matplotlib.pyplot as plt
import heapq

class Graph:
    def __init__(self):
        self.vertices = {}
        self.steiner_vertices = []
        self.optimal_cost_steiner_tree = 0
    
    def set_optimal_cost_steiner_tree(self,cost):
        self.optimal_cost_steiner_tree = cost
    
    def get_optimal_cost_steiner_tree(self):
        return self.optimal_cost_steiner_tree

    def add_vertex(self, vertex):
        self.vertices[vertex] = {}
        
    def add_steiner(self,vertex):
        self.steiner_vertices.append(vertex)

    def add_edge(self, vertex1, vertex2, weight):
        if vertex1 not in self.vertices:
            self.add_vertex(vertex1)
        if vertex2 not in self.vertices:
            self.add_vertex(vertex2)

        self.vertices[vertex1][vertex2] = weight
        self.vertices[vertex2][vertex1] = weight

    def get_neighbors(self, vertex):
        return self.vertices[vertex]
    
    def get_vertices(self):
        return list(self.vertices.keys())
    
    def get_steiner_vertices(self):
        return self.steiner_vertices
    
    def get_num_vertices_steiner(self):
        return len(self.steiner_vertices)
    
    def get_edges(self):
        edges = []
        for vertex in self.vertices:
            neighbors = self.get_neighbors(vertex)
            for neighbor in neighbors:
                # Add edge to the list as a tuple
                edges.append((vertex, neighbor))
        return edges
    
    def get_num_vertices(self):
        return len(self.vertices)
    
    def get_num_edges(self):
        return len(self.get_edges())//2  #//2 perchè sono indiretti
    
    def get_weight(self, vertex1, vertex2):
        if vertex1 in self.vertices and vertex2 in self.vertices[vertex1]:
            return self.vertices[vertex1][vertex2]
        else:
            return None
    
    def calculate_cost(graph):
        cost = 0
        edges = graph.get_edges()
        visited = []
        
        for edge in edges:
            vertex1, vertex2 = edge
            if (vertex1,vertex2) in visited or (vertex2, vertex1) in visited:
                continue
            weight = graph.get_weight(vertex1, vertex2)
            if weight is not None:
                cost += weight
            visited.append(edge)
        return cost
    
    def draw_graph(self):
        nx_graph = nx.Graph()
        for vertex, neighbors in self.vertices.items():
            for neighbor, weight in neighbors.items():
                nx_graph.add_edge(vertex, neighbor, weight=weight)

        # Disegno del grafo
        pos = nx.circular_layout(nx_graph)
        # Draw the graph with terminals in red and Steiner tree edges in blue
        nx.draw_networkx(nx_graph, pos, with_labels=True, node_color='lightgray', node_size=500)
        nx.draw_networkx_labels(nx_graph, pos)
        nx.draw_networkx_nodes(nx_graph, pos, nodelist = self.steiner_vertices, node_color='#e3a5b0', node_size=500)
        edge_labels = nx.get_edge_attributes(nx_graph, 'weight')
        #nx.draw_networkx_edges(steiner_tree, pos, edge_color='blue', width=2)
        nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels = edge_labels, font_size=10)


        # Visualizzazione del grafo
        #plt.axis('off')
        #plt.show()
        
    #Trovo il percorso più breve tra due nodi
    def find_shortest_path(self, start_node, end_node):
        distances = {vertex: float('inf') for vertex in self.vertices}
        distances[start_node] = 0
        visited = set()
        previous = {}
        edge_weights = {}

        priority_queue = [(0, start_node)]

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_node == end_node:
                path = {}
                current_edge = (end_node, previous[end_node])
                while current_node in previous:
                    #Aggiungo al percorso l'arco con il peso corrispondente
                    path[current_edge] = edge_weights[current_edge]
                    current_node = previous[current_node]
                    if current_node in previous:
                        current_edge = (current_node, previous[current_node])
                return path
            visited.add(current_node)

            neighbors = self.get_neighbors(current_node)
            for neighbor, weight in neighbors.items():
                if neighbor in visited:
                    continue

                new_distance = current_distance + weight
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_node
                    edge_weights[(neighbor, current_node)] = weight
                    heapq.heappush(priority_queue, (new_distance, neighbor))
      
        #Se arrivo qui non sono riuscita a collegare il nodo finale
        return previous, edge_weights, distances
    
#Funzione per disegnare il grafo con il suo corrispondente steiner tree sovrapposto
def draw_with_steiner_tree(grafo_originale, steiner_tree):
    nx_graph = nx.Graph()
    for vertex, neighbors in grafo_originale.vertices.items():
        for neighbor, weight in neighbors.items():
            nx_graph.add_edge(vertex, neighbor, weight=weight)

    # Disegno del grafo -> layout circolare per poterlo vedere bene
    pos = nx.circular_layout(nx_graph)

    # Disegno dei nodi grigi ( non di steiner) con label nome
    nx.draw_networkx(nx_graph, pos, with_labels=True, node_color='lightgray', node_size=500)
    nx.draw_networkx_labels(nx_graph, pos)
    
    #Disegno degli archi presi nello steiner tree 
    steiner_edges = steiner_tree.get_edges()
    steiner_subgraph = nx_graph.edge_subgraph(steiner_edges)
    nx.draw_networkx_edges(steiner_subgraph, pos, edge_color='blue', width=2)
    
    #Disegno dei nodi terminals (in rosa) con label nome
    nx.draw_networkx_nodes(nx_graph, pos, nodelist = steiner_tree.get_steiner_vertices(), node_color='#e3a5b0', node_size=500)
    
    #Disegno dei pesi sugli archi
    edge_labels = nx.get_edge_attributes(nx_graph, 'weight')
    nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels = edge_labels, font_size=10)
    
    #Disegno dei pesi degli archi di steiner con colore diverso
    edge_labels_steiner = {}
    for edge in edge_labels:
        if edge in steiner_edges:
            edge_labels_steiner[edge] = edge_labels[edge]
    nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels = edge_labels_steiner, font_size=10, font_color = 'blue')

    # Visualizzazione del grafo
    #plt.axis('off')
    #plt.show()
    
    #Creo il grafo leggendo da file 
def create_graph(file_path):
    grafo = Graph()
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            line = ''
            i = 0
            #Prendo gli archi del grafo
            while True:
                line = lines[i].rstrip()
                if (line == 'END'):
                    i = i + 1
                    break
                i = i + 1
                valori = line.split()
                grafo.add_edge(valori[1], valori[2], int(valori[3]))
                
            #Prendo i vertici di steiner
            while True:
                line = lines[i].rstrip()
                if (line == 'END'):
                    i = i + 1
                    break
                i = i + 1
                valori = line.split()
                grafo.add_steiner(valori[1])
            
            #Prendo il costo ottimale del grafo
            line = lines[i].rstrip()
            grafo.set_optimal_cost_steiner_tree(line)
            
        return grafo
    except FileNotFoundError:
        print("File not found.")
    except IOError:
        print("Error reading the file.")
        
#Disegno su una riga i 3 risultati (grafo originale, grafo con steiner tree e solo lo steiner tree)
def draw_row_graph(nome_istanza, grafo, steiner_tree):
    fig = plt.figure(figsize=(20, 5))
    ax = fig.add_subplot(1, 3, 1)# 3 righe x 5 colonne, attualmente in posizione i+1
    #Imposto il titolo dell'immagine e rimuovo gli assi
    plt.suptitle(nome_istanza, fontsize=15)
    ax.title.set_text('Grafo Originale, costo: '+ str(grafo.calculate_cost()))
    ax.set_xticks([])
    ax.set_yticks([])
    grafo.draw_graph()

    ax = fig.add_subplot(1, 3, 2)# 3 righe x 5 colonne, attualmente in posizione i+1
    #Imposto il titolo dell'immagine e rimuovo gli assi
    ax.title.set_text('Grafo con Steiner Tree')
    ax.set_xticks([])
    ax.set_yticks([])
    draw_with_steiner_tree(grafo, steiner_tree)

    ax = fig.add_subplot(1, 3, 3)# 3 righe x 5 colonne, attualmente in posizione i+1
    #Imposto il titolo dell'immagine e rimuovo gli assi
    ax.title.set_text('Costo: '+str(steiner_tree.calculate_cost())+"\nCosto Ottimale: "+str(grafo.get_optimal_cost_steiner_tree()))
    ax.set_xticks([])
    ax.set_yticks([])
    steiner_tree.draw_graph()        
        
