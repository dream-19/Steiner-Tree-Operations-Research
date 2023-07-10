import math
from ricerca_locale import *
import random

#Simulated annealing a partire da shortest path
def campionamento_casuale(original, current):
    #1) ottengo una soluzione random dell'Intorno 
        edges = current.get_edges()
        #print("\n\nedges iniziali:", remove_duplicate(edges))
        removed_edge = random.choice(edges)
        first_node_tree1 = removed_edge[0]
        first_node_tree2 = removed_edge[1]
        #print("Rimuovo questo arco: ", removed_edge, first_node_tree1, first_node_tree2)
        
        #Inizio a creare la nuova soluzione
        new_solution = copy.deepcopy(current) #deep copy dell'oggetto iniziale
        new_solution.remove_edge(removed_edge)
        new_solution_edges = remove_duplicate(new_solution.get_edges())
        new_solution_vertices = new_solution.get_vertices()
        
        #Definizione dei vertici dei due sottografi creati dal taglio
        grafo1 = []
        grafo2 = []
        grafo1.append(first_node_tree1) 
        grafo2.append(first_node_tree2)
        
        #print("Inizio a inserire i nodi del sottoalbero, new sol edges:", new_solution_edges)
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
        
        # Calcolo qual è il percorso minore, tra quelli possibili, che devo seguire per ricollegare i due grafi
        key_func = lambda item: min(item[1].keys())
        partenza = min(possible_paths.items(), key=key_func)[0]
        distanza, arrivo = next(iter(possible_paths[partenza].items()))
        #print("percorso minore, partenza, arrivo e distanza: ",partenza, arrivo, distanza)
        
        #Trovo la migliore soluzione differente da quella corrente (altrimenti non posso passare per dei peggioramenti)
        #Il SA può comunque tornare su una soluzione già visitata:es  migliore -> peggiore -> torna alla migliore
        grafo_senza_arco = copy.deepcopy(original)
        grafo_senza_arco.remove_edge(removed_edge)
        #print("grafo senza arco:", remove_duplicate(grafo_senza_arco.get_edges()))
        collegamento = grafo_senza_arco.find_shortest_path(partenza, arrivo)
        check_collegamento = True
        if collegamento is not None:
            #Rimuovo eventuali archi già presenti nella soluzione (non ho bisogno di riaggiungerli)
            for edge in list(collegamento.keys()):
                if edge in new_solution.get_edges():
                    collegamento.pop(edge)
                    
            #Se passa per dei vertici già presenti in soluzione significa che non è riuscito a trovare un percorso che colleghi i nodi,
            # uso semplicemente l'arco originale che avevo rimosso
            collegamento3 = [elem for tupla in collegamento.keys() for elem in tupla]
            collegamento3.pop(0)
            collegamento3.pop()
            for el in collegamento3:
                if el in new_solution.get_vertices():
                    check_collegamento = False
                    break
        else:
            check_collegamento = False
            
        if check_collegamento == False:
            #print("Devo riusare l'originale")
            collegamento = original.find_shortest_path(partenza,arrivo)
      
        for edge in collegamento:
            new_solution.add_edge(edge[0],edge[1],collegamento[edge])
     
        return new_solution
            
def simulated_annealing(original, iniziale, costo_iniziale, T, equilibrio):
    tempoI = time.time()
    ottimo_candidato = iniziale
    ottimo_candidato_costo = costo_iniziale
    
    current = iniziale
    costo_current = costo_iniziale
    
    optimal_cost = int(original.get_optimal_cost_steiner_tree())
    
    while T > 0:
        #print("Temperatura: ", T)
        for _ in range(0, equilibrio): #raggiungo lo stato stabile della temperatura
            #print("-- Iterazione:", k)
            new_solution = campionamento_casuale(original, current)
            
            #2) Calcolo DELTAE
            new_solution_cost = new_solution.calculate_cost()
            delta_e = new_solution_cost - costo_current
            #print("---- delta_e:", delta_e, "costo prima:", costo_current, "costo dopo: ", new_solution_cost)
            
            # 2.5) Verifico se la soluzione è migliore di quella corrente, se lo è controllo anche se è migliore dell'ottimo candidato
            if check_admissibility(original, new_solution):
                #Controlliamo se è l'ottimo (per risparmiare computazione)
                if int(new_solution_cost) <= optimal_cost:
                    return new_solution, new_solution_cost, time.time() - tempoI
                        
                if delta_e < 0 : #Accetto
                    current = copy.deepcopy(new_solution)
                    costo_current = new_solution_cost
                    
                    #Se è migliore dell'ottimo candidato aggiorno la soluzione
                    if new_solution_cost < ottimo_candidato_costo:
                        ottimo_candidato = copy.deepcopy(new_solution)
                        ottimo_candidato_costo = new_solution_cost
                        
    
                #Se non è migliore allora la accetto con un valore probabilistico 
                else: 
                    r = random.random()
                    #print("---- r",r)
                    limite = math.exp(-delta_e/T)
                    #print("---- limite:",limite)
                    if r < limite:
                        #print("---- Accetto comunque")
                        current = copy.deepcopy(new_solution)
                        costo_current = new_solution_cost 
            else:
                print("Non ammissibile :/")
                sys.exit()
                      
                
        T = T -1
    return ottimo_candidato, ottimo_candidato_costo, time.time() - tempoI 
    
