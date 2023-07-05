
from functions_grafo import *
from euristiche import *
import copy
import time
import heapq
#Implementare ricerca locale: con first improvment
''' 
Input: soluzione ammissibile di partenza, costo soluzione di partenza
k = 1 (prima iterazione)
x* = x1

Esplorazione intorno:
- preparo una lista di tutti gli archi in soluzione
- Elimino un arco (pop)
- Elimino anche tutti i nodi non terminali e archi di grado 1
- Ricollego i due alberi che si sono formati tramite shortest path:
    > controllo per ogni possibile nodo dei due alberi quale ha il percorso minore e li collego
- Calcolo il costo  della nuova soluzione
    > se è migliore accetto la soluzione e itero sul nuovo intorno
    > se è uguale accetto solo se è diversa dalla precedente (controllo che gli archi siano diversi): ATTENZIONE POSSIBILE LOOP
    
Se ho esplorato tutto l'intorno ma non c'è una soluzione migliore:
> stop e restituisci x*


MIGLIORIE POSSIBILI:
- aggiornare shortest path in modo che con costi uguali tra i vari percorsi non scelga sempre lo stesso
- aggiornare in modo tale che accetti anche soluzioni con costo uguale ma con archi diversi -> va gestita la possibile creazione di loop (magari fare un numero massimo di iterazioni o simili però MAH)
- prendere casualmente l'arco da rimuovere invece di prendere sempre lo stesso dall'elenco (?)
'''


#Funzione di ricerca Locale
#Intorno = elimino un arco (e di conseguenza i nodi di grado 1 non di steiner:), poi ricollego tramite shortest path
def local_search(original, solution, cost):
    start_time = time.time()
    k = 1 #numero di esplorazioni 
    best_solution = solution #migliore soluzione trovata fino a questo momento
    best_solution_cost = cost #costo della migliore soluzione trovata fino a questo momento
    all_edges = solution.get_edges()
    edges_unique = remove_duplicate(all_edges)
    
    ''' plt.figure()
    best_solution.draw_graph()
    plt.title("Grafo iniziale")'''
    #print("Archi iniziali: ", edges_unique)
    #print("Costo iniziale: ", cost)
    
    #Finché trovo una soluzione migliore
    while True:
        #Se ho esplorato tutto l'intorno mi fermo e restituisco la soluzione migliore trovata fino a quel momento
        if (len(edges_unique) == 0):
            end_time = time.time()
            execution_time = end_time - start_time
            return best_solution, best_solution_cost, k, execution_time
        
        ##############################################################################################################
        #1) Fase di rimozione dell'arco 
        # Prendo un arco dall'elenco degli archi
        removed_edge = edges_unique.pop() #FORSE è MEGLIO PROCEDERE CASUALMENTE INVECE DI MANTENERE L'ORDINE
        first_node_tree1 = removed_edge[0]
        first_node_tree2 = removed_edge[1]
        #print("\n\nRimuovo questo arco: ", removed_edge, first_node_tree1, first_node_tree2)
        
        #Inizio a creare la nuova soluzione
        new_solution = copy.deepcopy(best_solution) #deep copy dell'oggetto iniziale
        new_solution.remove_edge(removed_edge)
        new_solution_edges = remove_duplicate(new_solution.get_edges())
        new_solution_vertices = new_solution.get_vertices()
        
        #Definizione dei vertici dei due sottografi creati dal taglio
        grafo1 = []
        grafo2 = []
        grafo1.append(first_node_tree1) 
        grafo2.append(first_node_tree2)
        
        #Inserisco quali nodi sono del sottoalbero 1 e quali del sottoalbero2
        while len(new_solution_edges) > 0:
            for el in new_solution_edges:
                found = False
                if el[0] in grafo1 and el[1] not in grafo1:
                    grafo1.append(el[1])
                    found = True
                    
                if el[1] in grafo1 and el[0] not in grafo1:
                    grafo1.append(el[0])
                    found = True
                
                if el[0] in grafo2 and el[1] not in grafo2:
                    grafo2.append(el[1])
                    found = True
                if el[1] in grafo2 and el[0] not in grafo2:
                    grafo2.append(el[0])
                    found = True
                    
                if found:
                    new_solution_edges.remove(el)
                    
        #print("Vertici Sottografo 1: ", grafo1)
        #print("Vertici Sottografo 2: ", grafo2)
        
        #Rimuovo, finché ci sono o si creano, tutti i nodi di grado 1 non di steiner
        while True:
            if not(new_solution.remove_degree_one_nodes()):
                break
        #Aggiorno di conseguenza i due sottografi
        insieme1 = set(new_solution.get_vertices())
        grafo1 = [elemento for elemento in grafo1 if elemento in insieme1]
        grafo2 = [elemento for elemento in grafo2 if elemento in insieme1]
        #print("Vertici sottografo 1 aggiornati: ", grafo1)
        #print("Vertici sottografo 2 aggiornati: ", grafo2)
        
        
        ##############################################################################################################
        #2) Shortest Path tra tutti i nodi del grafo1 e tutti i nodi del grafo2 (djkstra)
        
        #Cerco di chiamare djkstra il minor numero di volte possibile
        if len(grafo1) > len(grafo2):
            grafo2, grafo1 = grafo1, grafo2
            
        #Calcolo delle distanze
        possible_paths = {}
        for nodo in grafo1:
            _ , nodo_arrivo, distanza = dijkstra(original, nodo, grafo2)
            possible_paths[nodo] = {distanza: nodo_arrivo}
        #print("Ho calcolato questi possibili collegamenti tra i due sottografi: ", possible_paths)
        
        # Calcolo qual è il percoso minore, tra quelli possibili, che devo seguire per ricollegare i due grafi
        key_func = lambda item: min(item[1].keys())
        partenza = min(possible_paths.items(), key=key_func)[0]
        distanza, arrivo = next(iter(possible_paths[partenza].items()))
        #print("percorso minore, partenza, arrivo e distanza: ",partenza, arrivo, distanza)
        
        #Trovo il collegamento e lo aggiungo formando la nuova soluzione
        collegamento = original.find_shortest_path(partenza, arrivo)
        #print("collegamento aggiunto: ", collegamento)
        #Aggiungo il percorso al grafo di steiner
        for edge in collegamento:
            new_solution.add_edge(edge[0],edge[1],collegamento[edge])
        
        ##############################################################################################################
        #3) Calcolo il costo della nuova soluzione e vedo se è una soluzione migliore
        # Non accetto soluzioni di costo equivalente, rischio di creare loop
        new_cost = new_solution.calculate_cost()
        #print("new_cost: ", new_cost)
        if new_cost < best_solution_cost and check_admissibility(original, new_solution):
            best_solution = copy.deepcopy(new_solution)
            best_solution_cost = new_cost
            all_edges = new_solution.get_edges()
            edges_unique = remove_duplicate(all_edges)
            k = k + 1
            '''plt.figure()
            best_solution.draw_graph()
            plt.title("Ho trovato una soluzione migliore!")'''
            
'''
Esploro tutto l'intorno, una volta che ho esplorato tutto l'intorno mi fermo solo se la soluzione migliore
trovata fino a quel momento è uguale a quella iniziale

'''
def local_search_best_improvment(original, solution, cost):
    start_time = time.time()
    k = 1 #numero di esplorazioni 
    best_solution = solution #migliore soluzione trovata fino a questo momento
    best_solution_cost = cost #costo della migliore soluzione trovata fino a questo momento
    all_edges = solution.get_edges()
    edges_unique = remove_duplicate(all_edges)
    found_a_best_solution = False #Se nell'intorno ho trovato una soluzione migliore
    
    #Durante l'esplorazione dello stesso intorno ho bisogno di operare sempre sullo stesso grafo (non come prima che ogni volta aggiornavo con il best)
    grafo_su_cui_operare = copy.deepcopy(solution)
    #Finché trovo una soluzione migliore
    while True:

        #Se ho esplorato tutto l'intorno senza trovare una soluzione migliore mi fermo
        if len(edges_unique) == 0 and found_a_best_solution == False :
            end_time = time.time()
            execution_time = end_time - start_time
            return best_solution, best_solution_cost, k, execution_time
        
        #Se ho trovato una soluzione migliore in tutto l'intorno allora mi sposto e continuo la ricerca
        if len(edges_unique) == 0 and found_a_best_solution == True :
            all_edges = best_solution.get_edges()
            edges_unique = remove_duplicate(all_edges)
            k = k + 1
            found_a_best_solution = False #Ripristino il valore
            grafo_su_cui_operare = copy.deepcopy(best_solution) #Nuovo grafo su cui esplorare l'intorno
        
        ##############################################################################################################
        #1) Fase di rimozione dell'arco 
        # Prendo un arco dall'elenco degli archi
        removed_edge = edges_unique.pop() 
        first_node_tree1 = removed_edge[0]
        first_node_tree2 = removed_edge[1]
        #print("\n\nIterazione:",k,"Rimuovo questo arco: ", removed_edge, first_node_tree1, first_node_tree2)
        
        #Inizio a creare la nuova soluzione
        new_solution = copy.deepcopy(grafo_su_cui_operare) #deep copy dell'oggetto iniziale
        new_solution.remove_edge(removed_edge)
        new_solution_edges = remove_duplicate(new_solution.get_edges())
        
        #Definizione dei vertici dei due sottografi creati dal taglio
        grafo1 = []
        grafo2 = []
        grafo1.append(first_node_tree1) 
        grafo2.append(first_node_tree2)
        
        #Inserisco quali nodi sono del sottoalbero 1 e quali del sottoalbero2
        while len(new_solution_edges) > 0:
            for el in new_solution_edges:
                found = False
                if el[0] in grafo1 and el[1] not in grafo1:
                    grafo1.append(el[1])
                    found = True
                    
                if el[1] in grafo1 and el[0] not in grafo1:
                    grafo1.append(el[0])
                    found = True
                
                if el[0] in grafo2 and el[1] not in grafo2:
                    grafo2.append(el[1])
                    found = True
                if el[1] in grafo2 and el[0] not in grafo2:
                    grafo2.append(el[0])
                    found = True
                    
                if found:
                    new_solution_edges.remove(el)
                    
        #print("Vertici Sottografo 1: ", grafo1)
        #print("Vertici Sottografo 2: ", grafo2)
       
        
        #Rimuovo, finché ci sono o si creano, tutti i nodi di grado 1 non di steiner
        while True:
            if not(new_solution.remove_degree_one_nodes()):
                break

        #Aggiorno di conseguenza i due sottografi
        insieme1 = set(new_solution.get_vertices())
        grafo1 = [elemento for elemento in grafo1 if elemento in insieme1]
        grafo2 = [elemento for elemento in grafo2 if elemento in insieme1]
        #print("Vertici sottografo 1 aggiornati: ", grafo1)
        #print("Vertici sottografo 2 aggiornati: ", grafo2)
        
        
        ##############################################################################################################
        #2) Shortest Path tra tutti i nodi del grafo1 e tutti i nodi del grafo2 (djkstra)
        
        #Cerco di chiamare djkstra il minor numero di volte possibile
        if len(grafo1) > len(grafo2):
            grafo2, grafo1 = grafo1, grafo2
            
        #Calcolo delle distanze
        possible_paths = {}
        for nodo in grafo1:
            _ , nodo_arrivo, distanza = dijkstra(original, nodo, grafo2)
            possible_paths[nodo] = {distanza: nodo_arrivo}
        #print("Ho calcolato questi possibili collegamenti tra i due sottografi: ", possible_paths)
        
        # Calcolo qual è il percoso minore, tra quelli possibili, che devo seguire per ricollegare i due grafi
        key_func = lambda item: min(item[1].keys())
        partenza = min(possible_paths.items(), key=key_func)[0]
        distanza, arrivo = next(iter(possible_paths[partenza].items()))
        #print("percorso minore, partenza, arrivo e distanza: ",partenza, arrivo, distanza)
        
        #Trovo il collegamento e lo aggiungo formando la nuova soluzione
        collegamento = original.find_shortest_path(partenza, arrivo)
        #print("collegamento aggiunto: ", collegamento)
        #Aggiungo il percorso al grafo di steiner
        for edge in collegamento:
            new_solution.add_edge(edge[0],edge[1],collegamento[edge])
        
        ##############################################################################################################
        #3) Calcolo il costo della nuova soluzione e vedo se è una soluzione migliore
        # Non accetto soluzioni di costo equivalente, rischio di creare loop
        new_cost = new_solution.calculate_cost()
        #print("new_cost: ", new_cost)
        if new_cost < best_solution_cost and check_admissibility(original, new_solution):
            found_a_best_solution = True
            best_solution = copy.deepcopy(new_solution)
            best_solution_cost = new_cost
            

def prim_mst(graph, subset_nodes, steiner_nodes):
    # Create a new graph for the MST
    mst_graph = Graph()

    # Add subset nodes to the new graph
    for node in subset_nodes:
        mst_graph.add_vertex(node)
        if node in steiner_nodes:
            mst_graph.add_steiner(node)

    # Initialize the priority queue with the first node
    priority_queue = [(0, subset_nodes[0], None)]

    # Track the visited nodes
    visited = set()

    while priority_queue:
        weight, current_node, parent = heapq.heappop(priority_queue)

        if current_node in visited:
            continue

        # Add the current node to the MST graph
        if parent is not None:
            mst_graph.add_edge(parent, current_node, weight)

        visited.add(current_node)

        # Add the neighboring nodes to the priority queue
        neighbors = graph.get_neighbors(current_node)
        for neighbor, edge_weight in neighbors.items():
            if neighbor not in visited and neighbor in subset_nodes:
                heapq.heappush(priority_queue, (edge_weight, neighbor, current_node))

    return mst_graph


# Funzione di ricerca locale che valuta anche l'albero MST generato per vedere se c'è un miglioramento con quello
#restituisce il risultato migliore (o mst o ricerca locale)
def local_search_best_improvment_mst(original, solution, cost):
    start_time = time.time()
    k = 1 #numero di esplorazioni 
    #Preparo la soluzione MST:
    best_mst_solution = solution
    best_mst_cost = cost
    
    #Soluzione di ricerca locale:
    best_solution = solution #migliore soluzione trovata fino a questo momento
    best_solution_cost = cost #costo della migliore soluzione trovata fino a questo momento
    all_edges = solution.get_edges()
    edges_unique = remove_duplicate(all_edges)
    found_a_best_solution = False #Se nell'intorno ho trovato una soluzione migliore
    
    #Durante l'esplorazione dello stesso intorno ho bisogno di operare sempre sullo stesso grafo (non come prima che ogni volta aggiornavo con il best)
    grafo_su_cui_operare = copy.deepcopy(solution)
    #Finché trovo una soluzione migliore
    while True:
        #Se ho esplorato tutto l'intorno senza trovare una soluzione migliore mi fermo
        if len(edges_unique) == 0 and found_a_best_solution == False :
            end_time = time.time()
            execution_time = end_time - start_time
            
            #Decido se restituire la soluzione del MST oppure quella della ricerca locale normale
            if best_mst_cost < best_solution_cost:
                return best_mst_solution, best_mst_cost, k, execution_time, True
            else:
                return best_solution, best_solution_cost, k, execution_time, False
        
        #Se ho trovato una soluzione migliore in tutto l'intorno allora mi sposto e continuo la ricerca
        if len(edges_unique) == 0 and found_a_best_solution == True :
            all_edges = best_solution.get_edges()
            edges_unique = remove_duplicate(all_edges)
            k = k + 1
            found_a_best_solution = False #Ripristino il valore
            grafo_su_cui_operare = copy.deepcopy(best_solution) #Nuovo grafo su cui esplorare l'intorno
        
        ##############################################################################################################
        #1) Fase di rimozione dell'arco 
        # Prendo un arco dall'elenco degli archi
        removed_edge = edges_unique.pop() 
        first_node_tree1 = removed_edge[0]
        first_node_tree2 = removed_edge[1]
        #print("\n\nIterazione:",k,"Rimuovo questo arco: ", removed_edge, first_node_tree1, first_node_tree2)
        
        #Inizio a creare la nuova soluzione
        new_solution = copy.deepcopy(grafo_su_cui_operare) #deep copy dell'oggetto iniziale
        new_solution.remove_edge(removed_edge)
        new_solution_edges = remove_duplicate(new_solution.get_edges())
        
        #Definizione dei vertici dei due sottografi creati dal taglio
        grafo1 = []
        grafo2 = []
        grafo1.append(first_node_tree1) 
        grafo2.append(first_node_tree2)
        
        #Inserisco quali nodi sono del sottoalbero 1 e quali del sottoalbero2
        while len(new_solution_edges) > 0:
            for el in new_solution_edges:
                found = False
                if el[0] in grafo1 and el[1] not in grafo1:
                    grafo1.append(el[1])
                    found = True
                    
                if el[1] in grafo1 and el[0] not in grafo1:
                    grafo1.append(el[0])
                    found = True
                
                if el[0] in grafo2 and el[1] not in grafo2:
                    grafo2.append(el[1])
                    found = True
                if el[1] in grafo2 and el[0] not in grafo2:
                    grafo2.append(el[0])
                    found = True
                    
                if found:
                    new_solution_edges.remove(el)
                    
        #print("Vertici Sottografo 1: ", grafo1)
        #print("Vertici Sottografo 2: ", grafo2)
       
        
        #Rimuovo, finché ci sono o si creano, tutti i nodi di grado 1 non di steiner
        while True:
            if not(new_solution.remove_degree_one_nodes()):
                break

        #Aggiorno di conseguenza i due sottografi
        insieme1 = set(new_solution.get_vertices())
        grafo1 = [elemento for elemento in grafo1 if elemento in insieme1]
        grafo2 = [elemento for elemento in grafo2 if elemento in insieme1]
        #print("Vertici sottografo 1 aggiornati: ", grafo1)
        #print("Vertici sottografo 2 aggiornati: ", grafo2)
        
        
        ##############################################################################################################
        #2) Shortest Path tra tutti i nodi del grafo1 e tutti i nodi del grafo2 (djkstra)
        
        #Cerco di chiamare djkstra il minor numero di volte possibile
        if len(grafo1) > len(grafo2):
            grafo2, grafo1 = grafo1, grafo2
            
        #Calcolo delle distanze
        possible_paths = {}
        for nodo in grafo1:
            _ , nodo_arrivo, distanza = dijkstra(original, nodo, grafo2)
            possible_paths[nodo] = {distanza: nodo_arrivo}
        #print("Ho calcolato questi possibili collegamenti tra i due sottografi: ", possible_paths)
        
        # Calcolo qual è il percoso minore, tra quelli possibili, che devo seguire per ricollegare i due grafi
        key_func = lambda item: min(item[1].keys())
        partenza = min(possible_paths.items(), key=key_func)[0]
        distanza, arrivo = next(iter(possible_paths[partenza].items()))
        #print("percorso minore, partenza, arrivo e distanza: ",partenza, arrivo, distanza)
        
        #Trovo il collegamento e lo aggiungo formando la nuova soluzione
        collegamento = original.find_shortest_path(partenza, arrivo)
        #print("collegamento aggiunto: ", collegamento)
        #Aggiungo il percorso al grafo di steiner
        for edge in collegamento:
            new_solution.add_edge(edge[0],edge[1],collegamento[edge])
        
        ##############################################################################################################
        #3) Calcolo il costo della nuova soluzione e vedo se è una soluzione migliore
        # Non accetto soluzioni di costo equivalente, rischio di creare loop
        new_cost = new_solution.calculate_cost()
       
        if new_cost < best_solution_cost and check_admissibility(original, new_solution):
            found_a_best_solution = True
            best_solution = copy.deepcopy(new_solution)
            best_solution_cost = new_cost
            #print("Soluzione normale migliore trovata: ", new_cost)
            
            #4) Verifico se applicando MST ottengo una soluzione migliore
            mst_solution = prim_mst(original, best_solution.get_vertices(), best_solution.get_steiner_vertices()) #Applico MST su un sottoinsieme di nodi del grafo iniziali (quelli trovati tramite ricerca locale)
            mst_cost = mst_solution.calculate_cost()
            #print("Il costo della soluzione MST:", mst_cost)
            if check_admissibility(original, mst_solution) and mst_cost < best_mst_cost:
                best_mst_cost = mst_cost
                best_mst_solution = copy.deepcopy(mst_solution)
                
                      

            
