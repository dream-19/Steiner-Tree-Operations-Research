
from functions_grafo import *
from ricerca_locale import *
import copy
from itertools import islice
import random

'''
GRASP:
    - MaxIter = 10 (numero di volte in cui eseguo la grasp per ogni istanza -> greedy random + ricerca locale)
    - Per i da 1 a maxiIter:
        - costruisco una soluzione iniziale (randomizzata) -> greedy randomized construction
        - eseguo local search
        - Se la soluzione è migliore della precedente questa diventa l'ottimo candidato
        - se la soluzione ha già raggiunto l'ottimo -> interrompo la ricerca (tanto so qual è l'ottimo)
    - restituisco la migliore soluzione trovata nel corso delle MaxIter 
    
GREEDY RANDOMIZED CONSTRUCTION NAIVE:   
  Finché esistono nodi terminali da inserire nell'albero:
    - scelgo il nodo successivo nella lista
    - costruisco le migliori k shortest path tra i due nodi (k = 5) ->  the first $K$ paths requires $O(KN^3)$ operations.
    - scelgo a random una delle k shortest path e lo collego
    NB: dato che non è più detto che sia un albero, devo controllare che non ci siano cicli. 
GREEDY RANDOMIZED CONSTRUCTION:
    Finché esistono nodi terminali da inserire nell'albero:
    - scelgo il nodo con distanza minore da collegare all'albero già esistente (utilizzando Djikstra)
    - costruisco le migliori k shortest path tra i due nodi (k = 5) ->  the first $K$ paths requires $O(KN^3)$ operations.
    - scelgo a random una delle k shortest path e lo collego
    NB: dato che non è più detto che sia un albero, devo controllare che non ci siano cicli. Quindi se si formano cicli smetto di aggiungere il percorso

'''
#GREEDY randomizzata che si basa sulla naive
def greedy_randomized_construction_naive(grafo, k):
    steiner_tree = Graph()
    terminals = (grafo.get_steiner_vertices()).copy()
    
    #Estraggo il primo dei terminali e lo inserisco nel risultato
    first_node = terminals.pop(0)
    steiner_tree.add_vertex(first_node)
    steiner_tree.add_steiner(first_node)
    
    #Finchè ho dei nodi terminali da inserire nell'albero
    while len(terminals) > 0:
        #1) Trovo il nodo di steiner successivo da aggiungere
        nodo_terminal_da_aggiungere = terminals.pop(0) #estraggo il primo nodo terminale dalla lista
        steiner_tree.add_steiner(nodo_terminal_da_aggiungere)
        
        #2)  Trovo i k migliori shortest path tra il nodo di attacco e il nodo da aggiungere e ne scelgo uno random
        #print("Percorsi trovati tra: ", nodo_di_attacco, " e ", nodo_terminal_da_aggiungere)
        grafonx = grafo.convert_to_nx_graph()
        
        
        all_possible_paths = list(islice(nx.shortest_simple_paths(grafonx, first_node, nodo_terminal_da_aggiungere, weight="weight"), k))
        path_scelto = random.choice(all_possible_paths)
        #print("path scelto: ", path_scelto)
        
        
        #3) Aggiungo il percorso al grafo di steiner (tenendo conto della possibilità di inserire altri nodi terminal ed eliminando la possibilità di cicli)
        for l in range(0, len(path_scelto)-1):
            primo = path_scelto[l]
            secondo = path_scelto[l+1]
            peso = grafonx.get_edge_data(path_scelto[l], path_scelto[l+1])['weight']
            #print("Devo aggiungere questo arco:", primo, secondo, peso)
            
            #Controllo se sto inserendo anche altri nodi terminal per caso
            #(non ho più la certezza di usare il percorso più corto)
            if primo in terminals:
                terminals.remove(primo)
                steiner_tree.add_steiner(primo)
            if secondo in terminals:
                terminals.remove(secondo)
                steiner_tree.add_steiner(secondo) 
            
            #Se ho già un percorso mi fermo (altrimenti creo un ciclo)
            if secondo in steiner_tree.get_vertices():
                steiner_tree.add_edge(primo,secondo,peso) #Aggiungo comunque l'ultimo arco per ricollegarmi al percorso già esistente
                break
            steiner_tree.add_edge(primo, secondo, peso)
            
        first_node = nodo_terminal_da_aggiungere
            

    #Controllo ammissibilità:
    if not(check_admissibility(grafo, steiner_tree)):
        print("NON è STATO PASSATO IL CONTROLLO DELL'AMMISSIBILITà")
        plt.figure()
        steiner_tree.draw_graph()
        sys.exit(0)
        
    return steiner_tree
#GREEDY RANDOMIZZATA CHE SI BASA SULLA SHORTEST PATH
def greedy_randomized_construction(grafo, k):
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
        #Nodo a distanza minima, terminals da attaccare
        nodo_di_attacco = list(minimum_value.items())[0][0]
        nodo_terminal_da_aggiungere = minimum_node[0]
        
        #2)  Trovo i k migliori shortest path tra il nodo di attacco e il nodo da aggiungere e ne scelgo uno random
        #print("Percorsi trovati tra: ", nodo_di_attacco, " e ", nodo_terminal_da_aggiungere)
        grafonx = grafo.convert_to_nx_graph()
        
        
        all_possible_paths = list(islice(nx.shortest_simple_paths(grafonx, nodo_di_attacco, nodo_terminal_da_aggiungere, weight="weight"), k))
        path_scelto = random.choice(all_possible_paths)
        #print("path scelto: ", path_scelto)
        
        
        #3) Aggiungo il percorso al grafo di steiner (tenendo conto della possibilità di inserire altri nodi terminal ed eliminando la possibilità di cicli)
        for l in range(0, len(path_scelto)-1):
            primo = path_scelto[l]
            secondo = path_scelto[l+1]
            peso = grafonx.get_edge_data(path_scelto[l], path_scelto[l+1])['weight']
            #print("Devo aggiungere questo arco:", primo, secondo, peso)
            
            #Controllo se sto inserendo anche altri nodi terminal per caso
            #(non ho più la certezza di usare il percorso più corto)
            if primo in terminals:
                terminals.remove(primo)
                steiner_tree.add_steiner(primo)
            if secondo in terminals:
                terminals.remove(secondo)
                steiner_tree.add_steiner(secondo) 
            
            #Se ho già un percorso mi fermo (altrimenti creo un ciclo)
            if secondo in steiner_tree.get_vertices():
                #steiner_tree.add_edge(primo,secondo,peso) #Aggiungo comunque l'ultimo arco per ricollegarmi al percorso già esistente
                break
            steiner_tree.add_edge(primo, secondo, peso)
            
   
    
    #Controllo ammissibilità:
    if not(check_admissibility(grafo, steiner_tree)):
        print("NON è STATO PASSATO IL CONTROLLO DELL'AMMISSIBILITà")
        sys.exit(0)
        
    return steiner_tree

#APPLICAZIONE DELLA GRASP
                                                #tipo 0 =  si basa su naive, tipo 1 si basa su shortest path
def Grasp_with_best_improvment(MaxIter, grafo, tipo):
    start_time = time.time()
    costo_euristica_della_best = None
    euristica_con_costo_magg = - sys.maxsize
    euristica_con_costo_min = sys.maxsize
    best_cost = sys.maxsize
    best_solution = None
    

    for _ in range(0, MaxIter):
            #Costruisco la soluzione iniziale (greedy randomized construction dandogli il grafo e la dimensione dei k migliori candidati da considerare)
            #10 come numero di candidati da considerare è un valore che ho scelto io, con un valore maggiore ha delle performance peggiori
            if tipo == 1:
                initial_solution = greedy_randomized_construction(grafo, 10)
            else:
                initial_solution = greedy_randomized_construction_naive(grafo, 10)
             
            #Rimuovo, finché ci sono o si creano, tutti i nodi di grado 1 non di steiner (caso raro)
            while True:
                if not(initial_solution.remove_degree_one_nodes()):
                    break
            initial_solution_cost = initial_solution.calculate_cost()
            #print("la soluzione iniziale con euristica ha costo: ", initial_solution_cost)
            
            #Eseguo LocalSearch (best)
            new_solution, new_solution_cost, k, timeLS = local_search_best_improvment(grafo, initial_solution, initial_solution.calculate_cost())
            #print("LS sulla soluzione iniziale ottiene costo: ", new_solution_cost, " in ", timeLS, " secondi")
            
            #Valuto il risultato ottenuto
            if new_solution_cost < best_cost:
                best_cost = new_solution_cost
                best_solution = copy.deepcopy(new_solution)
                costo_euristica_della_best = initial_solution_cost
            
            #Considero le statistiche sui costi delle euistiche
            if initial_solution_cost > euristica_con_costo_magg:
                euristica_con_costo_magg = initial_solution_cost
            if initial_solution_cost < euristica_con_costo_min:
                euristica_con_costo_min = initial_solution_cost
            
            #Se ho già raggiungo l'ottimo non ha senso andare avanti:
            if int(best_cost) == int(grafo.get_optimal_cost_steiner_tree()):
                break
    end_time = time.time()
    #plt.figure()
    #best_solution.draw_graph()
            
    return best_solution, best_cost, costo_euristica_della_best, euristica_con_costo_magg, euristica_con_costo_min, end_time - start_time

