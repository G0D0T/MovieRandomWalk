import networkx as nx
import numpy as np
import pandas as pd
import secrets as sc #per la funzione random

#funzione per estrarre il prossimo nodo in modo casuale, con la probabilità condizionata dal rating
#la variabile t serve a limitare il sottoinsieme di nodi da estrarre: più il valore è alto e più nodi saranno filtrati
def extract_neigh(node, t = 0.75):
	neig = sorted(node.items(), key=lambda edge: edge[1]['rating'])
	threshold = int(len(neig)*t)
	neig = neig[threshold:]
	next = sc.choice(neig)
	return next[0]

#funzione finale per la stampa a schermo di quanto trovato
def consigli(reccomend, filt):
	print('----------------------------------')
	print('In base alla sua watchlist, le suggeriamo i seguenti film: ')
	for f in reccomend[filt:]:
		print(f)

#set dei tipi delle colonne del dataset per una lettura più agevole
typesMovies = {'movieId': np.dtype(int),'title': np.dtype(str),'genres' : np.dtype(str)}
typesRatings = {'userId': np.dtype(int),'movieId': np.dtype(int),'rating': np.dtype(float),'timestamp' : np.dtype(int)}

#import dei dataset originali
movies = pd.read_csv('movies.csv', dtype=typesMovies, low_memory = False)
ratings = pd.read_csv('ratings.csv', dtype=typesRatings, low_memory = False)

#unione dei due dataset
movie_ratings = pd.merge(movies, ratings)

#drop delle colonne inutili
movie_ratings.drop("timestamp", inplace = True, axis = 1)
movie_ratings.drop("movieId", inplace = True, axis = 1)
movie_ratings.drop("genres", inplace = True, axis = 1)

#print(movie_ratings.sample(10))

#generazione del grafo
G = nx.from_pandas_edgelist(movie_ratings, 'userId', 'title', ['rating'])
movie_ratings.to_csv('import.csv', index=False)
print(nx.info(G))
#nx.write_weighted_edgelist(G, 'movie.weighted.edgelist')

#aggiungo un nuovo utente con relativi film visti
newUser = 777
G.add_edge(newUser, 'The Machinist (2004)', rating=5.0)
G.add_edge(newUser, 'Harry Potter and the Prisoner of Azkaban (2004)', rating=4.0)
G.add_edge(newUser, 'Toy Story (1995)', rating=5.0)
G.add_edge(newUser, 'Pulp Fiction (1994)', rating=5.0)
G.add_edge(newUser, 'The Mask', rating=4.0)

#print([n for n in G.neighbors(2)]) #vedo tutti i film visti da un certo utente
#print(G[2]) #vedo tutti i film visti da un certo utente con voto assegnato
#print([n for n in G.neighbors('Whiplash (2014)')]) #vedo tutti gli utenti che hanno visto un certo film

#parametri globali
numSteps = 10 #lunghezza prevista della random walk
walk = []
visitedFilm = []
visitedUser = []
start = 777 #da sostituire con l'id utente che vuole avere un consiglio
giavisti = ([n for n in G.neighbors(start)])#.items()

def main():	
	step = 0
	flag = False #True per gli utenti, viceversa per i film
	walk.append(start)
	visitedUser.append(start)
	for f in giavisti:
		visitedFilm.append(f) #salvo i film già visionati per evitare di consigliarli di nuovo
	nodo = start
	#prev = start
	primoF = True #flag che indica se ci troviamo ad aggiungere il primo film
	endd = 0 #variabile che evita loop infiniti (possibile in un certo caso)

	while (step < numSteps) and (endd < 30):
		if endd > 15: #verifico di non trovarmi in un "vicolo cieco" e, in caso, ritorno indietro
			if flag:				
				nodo = visitedUser[-2]
				flag = not flag
			else:
				nodo = visitedFilm[-2]
				flag = not flag
		endd += 1
		nodo = extract_neigh(G[nodo])
		print(nodo)
		#print(prev)
		if flag:
			if nodo not in visitedUser:
				visitedUser.append(nodo)			
			else:			#nel caso il nodo sia già stato visitato, passo alla prossima iterazione
				nodo = prev
				continue
		else:
			if nodo not in visitedFilm:
				visitedFilm.append(nodo)
			elif primoF:
				primoF = False
				flag = not flag
				prev = nodo
				continue
			else:
				nodo = prev
				continue

		walk.append(nodo) #il nodo trovato in questa iterazione è nuovo, quindi devo aggiornare i seguenti parametri
		prev = nodo
		flag = not flag
		step += 1

	consigli(visitedFilm, len(giavisti))

main()

"""
funzioni utils

for x in G.nodes():
      print ("Node:", x, "has total #degree:",G.degree(x), " , In_degree: ", G.out_degree(x)," and out_degree: ", G.in_degree(x))   
for u,v in G.edges():
      print ("Weight of Edge ("+str(u)+","+str(v)+")", G.get_edge_data(u,v))
	  
	  
	  Data = open('ratings.csv', "r")
next(Data, None)  # skip the first line in the input file
Graphtype = nx.Graph()  #undirected

G = nx.parse_edgelist(Data, delimiter=';', create_using=Graphtype, nodetype=int, data=(('rating', float),))
"""	  
