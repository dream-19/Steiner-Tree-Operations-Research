from functions_grafo import *
import time
import sys
import heapq

'''
L'euristica naive funziona in questo modo:
- finché ci sono ancora terminali:
    -> estrai un nodo terminale
    -> collegalo con shortest path al nodo precedente, se durante il cammino ti ricolleghi ad un percorso che esiste già smetti di inserire archi (altrimenti si crea un ciclo)<br>

Osservazioni: in questo caso bisogna controllare se nell'aggiungere un nodo si sono inglobati altri nodi di steiner nel percorso
'''

'''
L'euristica shortest path funziona in questo modo:
- crea un albero con il primo nodo di steiner
- finchè ci sono nodi di steiner:<br>
    -> determina quale nodo è più vicino all'albero
    -> aggiungi questo nodo tramite shortest path
'''


#EURISTICA 0: naive
def naive(grafo):
    start_time = time.time()
    steiner_tree = Graph()
    terminals = (grafo.get_steiner_vertices()).copy()
    
    #Estraggo il primo dei terminali e lo inserisco nel risultato
    first_node = terminals.pop(0)
    steiner_tree.add_vertex(first_node)
    steiner_tree.add_steiner(first_node)
    
    #Finchè ho dei nodi terminali da inserire nell'albero
    while len(terminals) > 0:
        nuovo_terminal = terminals.pop(0) #estraggo il primo nodo terminale dalla lista
        steiner_tree.add_steiner(nuovo_terminal)

        path = grafo.find_shortest_path(first_node, nuovo_terminal)
        
        #Aggiungo il percorso al grafo di steiner
        for edge in path:
            #Controllo se sto inserendo anche altri nodi terminal per caso
            if edge[0] in terminals:
                terminals.remove(edge[0])
                steiner_tree.add_steiner(edge[0])
            if edge[1] in terminals:
                terminals.remove(edge[1])
                steiner_tree.add_steiner(edge[1])  
            
            ''' 
            Se a questo punto ho già un percorso, mi fermo altrimenti creo un ciclo
            Esempio: Ho l'albero 18 -- 4 -- 5 -- 8
            Per collegarmi al terminal 18 dal nodo 34 ho il percorso: 34 -- 10 -- 8 -- 3  -- 18 : questo creerebbe un ciclo
            Una volta raggiunto l'8 mi blocco e rimane: 34 -- 10 -- 8 
            '''
            if edge[1] in steiner_tree.get_vertices():
                steiner_tree.add_edge(edge[0],edge[1],path[edge]) #Aggiungo comunque l'ultimo arco per ricollegarmi al percorso già esistente
                break
            steiner_tree.add_edge(edge[0],edge[1],path[edge])
                 
        first_node = nuovo_terminal #Aggiorno il nodo a cui ricollegarci
        
    end_time = time.time()
    execution_time = end_time - start_time
    
    #Controllo ammissibilità:
    if not(check_admissibility(grafo, steiner_tree)):
        print("NON è STATO PASSATO IL CONTROLLO DELL'AMMISSIBILITA'")
        sys.exit(0)
        
    
    return steiner_tree, execution_time

#DIJKSTRA:CALCOLO DELLE DISTANZE - Grafo di partenza su cui calcolare le distanze, nodo di partenza, nodi rispetto a cui mi interessa calcolare la distanza
#COSTO COMPUTAZIONALE: O(|E| + |V| * log(|V|)) nel caso peggiore
#Uso come struttura dati una miniheap (modulo heapq)
def dijkstra(graph, start, nodi_di_interesse):
    distances = {node: float('inf') for node in graph.get_vertices()}  # Initialize distances to infinity
    distances[start] = 0  # Distance from start node to itself is 0
    priority_queue = [(0, start)]  # Use a priority queue to prioritize nodes with shorter distances
    visited = set()  # Set to track visited nodes
    found_nodes = set()  # Set to track found target nodes
    
    while priority_queue and found_nodes != set(nodi_di_interesse):
        current_distance, current_node = heapq.heappop(priority_queue)  # Get the node with the smallest distance
        
        # Skip if we have already found a shorter path to the current node
        if current_distance > distances[current_node]:
            continue
        
        visited.add(current_node)  # Mark current node as visited
        
        # Check if the current node is a target node
        if current_node in nodi_di_interesse:
            found_nodes.add(current_node)
        
        #Explore neighbors of the current node
        neighbors = graph.get_neighbors(current_node)
        for neighbor, weight in neighbors.items():
            if neighbor in visited:
                continue  # Skip already visited neighbors
            distance = current_distance + weight
            if distance < distances[neighbor]:  # If a shorter path is found, update the distance
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))  # Add the neighbor to the priority queue
    result_distances = {}
    for i in distances:
        if i in nodi_di_interesse:
            result_distances[i] = distances[i]
        
    #Restituisco: tutte le distanze, il nodo a distanza minima, il valore della distanza minima
    node, distance = min(result_distances.items(), key=lambda x: x[1])
    return result_distances, node, distance

#EURISTICA1: SHORTEST PATH
def shortest_path(grafo):
    start_time = time.time()
    steiner_tree = Graph()
    terminals = (grafo.get_steiner_vertices()).copy()
    
    #Estraggo il primo dei terminali e lo inserisco nel risultato
    first_node = terminals.pop(0)
    steiner_tree.add_vertex(first_node)
    steiner_tree.add_steiner(first_node)
    
    #Finchè ho dei nodi terminali da inserire nell'albero
    while len(terminals) > 0:
        #1) Trovo il nodo di steiner che ha la distanza minore dallo steiner tree attuale 
        # (Controllo Djikstra da ogni nodo terminal rispetto a tutti i nodi (dello steiner tree))
        terminals_distances = {}
        i = 0 
        #Controllo con dijkstra tutte le distanze
        for i in range(0, len(terminals)):
            result_dijkstra, minimum_key, minimum_distance = dijkstra(grafo, terminals[i], steiner_tree.get_vertices())
            #Trovo il nodo con cui il terminale ha la distanza minima
            terminals_distances[terminals[i]] = {minimum_key : minimum_distance}
        
        #Trovo quale terminale è più vicino all'albero
        minimum_value = min(terminals_distances.values(), key=lambda x: next(iter(x.values())))
        minimum_node = []
        for key, val in terminals_distances.items():
            if val == minimum_value:
                minimum_node.append(key)
        #Nodo a distanza minima, distanza dal nodo, terminals da attaccare
        nodo_di_attacco = list(minimum_value.items())[0][0]
        distanza_di_attacco = list(minimum_value.items())[0][1]
        nodo_terminal_da_aggiungere = minimum_node[0]
        
        #2) Attacco il nodo - Trovo il shortest path tra i il terminal e il nodo più vicino dell'albero
        path = grafo.find_shortest_path(nodo_di_attacco,nodo_terminal_da_aggiungere)
        #Aggiungo il percorso al grafo di steiner
        for edge in path:
            steiner_tree.add_edge(edge[0],edge[1],path[edge])
            
        #Rimuovo dalla lista il terminale aggiunto
        terminals.remove(nodo_terminal_da_aggiungere)
        steiner_tree.add_steiner(nodo_terminal_da_aggiungere)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    #Controllo ammissibilità:
    if not(check_admissibility(grafo, steiner_tree)):
        print("NON è STATO PASSATO IL CONTROLLO DELL'AMMISSIBILITà")
        sys.exit(0)
        
    
    return steiner_tree, execution_time
    
    