
from functions_grafo import *
from euristiche import *
import copy
import time
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
            
