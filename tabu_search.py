from functions_grafo import *
from euristiche import *
import copy
import time
#TABU SEARCH



def tabu(original, solution, cost, max_intorno, max_tabu):
    start_time = time.time()
    k = 1 #numero di esplorazioni 
    
    #Ottimo totale
    best_solution = solution #migliore soluzione trovata fino a questo momento
    best_solution_cost = cost #costo della migliore soluzione trovata fino a questo momento
    
    #Ottimo candidato
    ottimo_candidato = solution
    ottimo_candidato_cost = sys.maxsize
    
    #mmmh
    best_of_this_round = ''
    best_of_this_round_cost = sys.maxsize
    
    #Tabu list
    tabu_list = []
    
    #Archi della soluzione
    all_edges = solution.get_edges()
    edges_unique = remove_duplicate(all_edges)
    
    #Durante l'esplorazione dello stesso intorno ho bisogno di operare sempre sullo stesso grafo 
    grafo_su_cui_operare = copy.deepcopy(solution)

    intorni_esplorati = 0
    #print("Inizio tabu search, intorno 0")
    while True:
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
        
        #Trovo il collegamento e lo aggiungo formando la nuova soluzione - IMPEDISCO DI RICREARE LA STESSA SOLUZIONE! (se è possibile)
        grafo_senza_arco = copy.deepcopy(original)
        grafo_senza_arco.remove_edge(removed_edge)
        collegamento = grafo_senza_arco.find_shortest_path(partenza, arrivo)
        if collegamento == None:
            collegamento = original.find_shortest_path(partenza, arrivo)
        #print("collegamento: ", collegamento)
        #print("collegamento aggiunto: ", collegamento)
        #Aggiungo il percorso al grafo di steiner
        for edge in collegamento:
            new_solution.add_edge(edge[0],edge[1],collegamento[edge])
        
        ##############################################################################################################
        #3) Calcolo il costo della nuova soluzione e faccio gli aggiornamenti
        new_cost = new_solution.calculate_cost()
        #plt.figure()
        #plt.title("Rimuovendo: "+str(removed_edge)+"\nAggiungendo: "+str(collegamento)+"\nCosto: "+str(new_cost))
        #new_solution.draw_graph()
        #print("new_cost: ", new_cost)
        
        #Devo trovare la migliore soluzione per questo round (ammissibile e diversa dall'ottimo candidato) - ammissibile rispetto alla tabu list
        if new_cost < best_of_this_round_cost and check_admissibility(original, new_solution) and ottimo_candidato.get_edges() != new_solution.get_edges() and removed_edge not in tabu_list:
            #print("Nuova soluzione per questo  round:", new_cost, "vs", best_of_this_round_cost)
            best_of_this_round_cost = new_cost
            best_of_this_round = copy.deepcopy(new_solution)
            best_of_this_round_collegamento = collegamento
            
        #Criterio di aspirazione - non importa la mossa tabu
        if new_cost < best_solution_cost and check_admissibility(original, new_solution):
            best_solution_cost = new_cost
            best_solution = copy.deepcopy(new_solution)
            best_of_this_round_collegamento = collegamento
            #print("Criterio di aspirazione soddisfatto, costo: ", best_solution_cost, "mossa tabu o no: ", removed_edge)
            intorni_esplorati = 0
            
            
        ##############################################################################################################
        #Se ho esplorato tutto l'intorno senza trovare una soluzione migliore della migliore per tot volte mi fermo!
        if len(edges_unique) == 0 and intorni_esplorati >= max_intorno:
            end_time = time.time()
            execution_time = end_time - start_time
            #print("Intorno raggiuntooo: ", intorni_esplorati)
            return best_solution, best_solution_cost, k, execution_time
        
        #Ho finito di esplorare l'intorno, mi sposto su quello nuovo andando ad aggiornare l'ottimo candidato
        if len(edges_unique) == 0:
            intorni_esplorati +=1 
            #print("------------------------------------------------------------\nHo esplorato tutto l'intorno, passo al prossimo intorno", intorni_esplorati)
            
            #Aggiorno l'ottimo candidato
            if best_of_this_round:
                ottimo_candidato = copy.deepcopy(best_of_this_round)
            ottimo_candidato_cost = best_of_this_round_cost
            
            #Aggiorno il best del prossimo round
            best_of_this_round = None
            best_of_this_round_cost = sys.maxsize
            
            
            all_edges = ottimo_candidato.get_edges()
            edges_unique = remove_duplicate(all_edges)
            k = k + 1 #passo ad esplorare il prossimo intorno
            grafo_su_cui_operare = copy.deepcopy(ottimo_candidato) #Nuovo grafo su cui esplorare l'intorno
            
            
            #Aggiorno tabu list (la mantengo sempre di al massimo tot elementi + il nuovo path aggiunto)
            if len(tabu_list) > 0:
                tabu_list.pop(0)
                
            while len(tabu_list) > max_tabu:
                tabu_list.pop(0)
            
            for edge in best_of_this_round_collegamento: #Aggiungo tutto il path che ho messo in soluzione in questo round
                tabu_list.append(edge)
            #print("collegamento aggiunto in tabu list:", best_of_this_round_collegamento)    
            #print("tabu list per questo intorno: ", tabu_list)
            #print("In questo momento l'ottimo candidato ha valore: ", ottimo_candidato_cost)
           

