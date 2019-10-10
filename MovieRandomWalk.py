import networkx as nx
import numpy as np
import pandas as pd
#from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
import secrets as sc #per la funzione random
from collections import Counter

#funzione per estrarre il prossimo nodo in modo casuale, con la probabilità condizionata dal rating
#la variabile t serve a limitare il sottoinsieme di nodi da estrarre: più il valore è alto e più nodi saranno filtrati
def extract_neigh(node, t = 0.75):
	neig = sorted(node.items(), key=lambda edge: edge[1]['rating'])
	threshold = int(len(neig)*t)
	neig = neig[threshold:]
	next = sc.choice(neig)
	return next[0]

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
movie_ratings.to_csv('import.csv', index=False)

#train, test = train_test_split(movie_ratings, test_size=0.5)
#TRAIN=0.75/TEST=0.25
kf = KFold(n_splits = 4, shuffle = True)#, random_state = 0)
result = next(kf.split(movie_ratings), None)
train = movie_ratings.iloc[result[0]]
test =  movie_ratings.iloc[result[1]]
print('Numero righe del train set: ',len(train))
print('Numero righe del test set: ',len(test))
#print(movie_ratings.sample(10))
print('------------------------------------------------')

#generazione del grafo train
Gtrain = nx.from_pandas_edgelist(train, 'userId', 'title', ['rating'])
Gtrain.name = 'Train_Set'
print(nx.info(Gtrain))
print('------------------------------------------------')
#generazione del grafo test
Gtest = nx.from_pandas_edgelist(test, 'userId', 'title', ['rating'])
Gtest.name = 'Test_Set'
print(nx.info(Gtest))
#nx.write_weighted_edgelist(G, 'movie.weighted.edgelist')
print('------------------------------------------------')

#aggiungo un nuovo utente con relativi film visti al train set
newUser = 777
Gtrain.add_edge(newUser, 'The Machinist (2004)', rating=3.0)
Gtrain.add_edge(newUser, 'Harry Potter and the Prisoner of Azkaban (2004)', rating=4.0)
Gtrain.add_edge(newUser, 'Toy Story (1995)', rating=5.0)
Gtrain.add_edge(newUser, 'Pulp Fiction (1994)', rating=5.0)
Gtrain.add_edge(newUser, 'The Mask', rating=4.0)
Gtrain.add_edge(newUser, 'Raiders of the Lost Ark (Indiana Jones and the Raiders of the Lost Ark) (1981)', rating=4.5)
Gtrain.add_edge(newUser, 'Shawshank Redemption, The (1994)', rating=5.0)
Gtrain.add_edge(newUser, 'Mission: Impossible - Rogue Nation (2015)', rating=2.0)
Gtrain.add_edge(newUser, 'Back to the Future (1985)', rating=4.5)
#idem per il test set
Gtest.add_edge(newUser, 'The Machinist (2004)', rating=3.0)
Gtest.add_edge(newUser, 'Harry Potter and the Prisoner of Azkaban (2004)', rating=4.0)
Gtest.add_edge(newUser, 'Toy Story (1995)', rating=5.0)
Gtest.add_edge(newUser, 'Pulp Fiction (1994)', rating=5.0)
Gtest.add_edge(newUser, 'The Mask', rating=4.0)
Gtest.add_edge(newUser, 'Raiders of the Lost Ark (Indiana Jones and the Raiders of the Lost Ark) (1981)', rating=4.5)
Gtest.add_edge(newUser, 'Shawshank Redemption, The (1994)', rating=5.0)
Gtest.add_edge(newUser, 'Mission: Impossible - Rogue Nation (2015)', rating=2.0)
Gtest.add_edge(newUser, 'Back to the Future (1985)', rating=4.5)

#parametri globali
ripetizioni = 10000
numSteps = 2 #lunghezza prevista della random walk
top = 25
walk = []
visitedFilm = []
visitedUser = []
start = 777 #da sostituire con l'id utente che vuole avere un consiglio

def run (grafo):
	giavisti = ([n for n in grafo.neighbors(start)])	
	step = 0
	flag = False #True per gli utenti, viceversa per i film
	visitedUser.append(start)
	for f in giavisti:
		visitedFilm.append(f) #salvo i film già visionati per evitare di consigliarli di nuovo
	nodo = start
	#prev = start
	primoF = True #flag che indica se ci troviamo ad aggiungere il primo film

	for i in range(0,ripetizioni):	
		while (step < numSteps): 
			nodo = extract_neigh(grafo[nodo])
			#print(nodo)
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

			#walk.append(nodo) #il nodo trovato in questa iterazione è nuovo, quindi devo aggiornare i seguenti parametri
			prev = nodo
			flag = not flag
			step += 1
			#print('------------------------------------------------')
		
		#Salvataggio del film trovato con l'ultima walk
		walk.append(visitedFilm[-1])
		#reset dei vari parametri
		nodo = start
		primoF = True
		flag = False
		step = 0
		visitedUser.clear()
		visitedUser.append(start)
		visitedFilm.clear()
		for f in giavisti:
			visitedFilm.append(f)
	
	#conta delle occorrenze dei film durante le ripetizioni della random walk + ordinamento
	res = sorted(Counter(walk).items(), key=lambda x: x[1], reverse=True)
	for r in res[:top]:
		print(r)
		
	return res[:top]

print('Consigli TRAIN set')
trainlista = run(Gtrain)
walk.clear()
visitedUser.clear()
visitedFilm.clear()
print('------------------------------------------------')
print('Consigli TEST set')
print('------------------------------------------------')
testlista = run(Gtest)

#dopo aver eseguito le walk sia su train che test, si stima la precisione dei suggerimenti
conta = 0
common = []
for i in range(0,len(trainlista)):
	for j in range(0,len(testlista)):
		if trainlista[i][0] == testlista[j][0]:
			common.append(testlista[j])
			conta +=1

#controllo dei film suggeriti in entrambi i set e stampa a schermo la top 5
conta /= top
print("\n\nAccuracy: ", conta)
print('------------------------------------------------')
print("\nTitoli suggeriti (in ordine di attinenza")
common.sort(key=lambda x: x[1], reverse=True)
for elem in common[:5]:
	print (elem[0])

"""
funzioni utils
#print([n for n in G.neighbors(2)]) #vedo tutti i film visti da un certo utente
#print(G[2]) #vedo tutti i film visti da un certo utente con voto assegnato
#print([n for n in G.neighbors('Whiplash (2014)')]) #vedo tutti gli utenti che hanno visto un certo film
for x in G.nodes():
      print ("Node:", x, "has total #degree:",G.degree(x), " , In_degree: ", G.out_degree(x)," and out_degree: ", G.in_degree(x))
	  for u,v in G.edges():
      print ("Weight of Edge ("+str(u)+","+str(v)+")", G.get_edge_data(u,v))	  
	  
	  Data = open('ratings.csv', "r")
next(Data, None)  # skip the first line in the input file
Graphtype = nx.Graph()  #undirected

G = nx.parse_edgelist(Data, delimiter=';', create_using=Graphtype, nodetype=int, data=(('rating', float),))
"""	  
