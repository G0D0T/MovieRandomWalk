import networkx as nx #per la gestione del grafo
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold #per lo split del train e test set
import secrets as sc #per la funzione random
from collections import Counter

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
#movie_ratings.to_csv('import.csv', index=False)

#train, test = train_test_split(movie_ratings, test_size=0.5)
#TRAIN=0.9/TEST=0.1
kf = KFold(n_splits = 10, shuffle = True)#, random_state = 0)
result = next(kf.split(movie_ratings), None)
train = movie_ratings.iloc[result[0]]
test =  movie_ratings.iloc[result[1]]
print('Numero righe del train set: ',len(train))
print('Numero righe del test set: ',len(test))
#print(movie_ratings.sample(10))
print('------------------------------------------------')

#generazione del grafo train
Grafo = nx.from_pandas_edgelist(train, 'userId', 'title', ['rating'])
Grafo.name = 'Train_Set'
print(nx.info(Grafo))
print('------------------------------------------------')
print('ATTENDERE...')

#variabili e contatori vari
ripetere = 1000
passi = 3
hit = 0
hit5 = 0
hit10 = 0
hit15 = 0
superhit = 0
top = 5
visitatiF = []
visitatiU = []
walk = []

temp = 0

#funzione che estrae il prossimo "hop" della random walk
def extract_neigh(node, t = 0.75):
	neig = sorted(node.items(), key=lambda edge: edge[1]['rating'])
	threshold = int(len(neig)*t)
	neig = neig[threshold:]
	next = sc.choice(neig)
	return next[0]

#funzione che ritorna il "traguardo" della random walk
def randomwalk(start):
	visti = ([n for n in Grafo.neighbors(start)])
	for f in visti:
		visitatiF.append(f)
	visitatiU.append(start)
	nodo = start
	step = 0
	tempc = 0
	tempcc = 0	
	while step < passi:
		nodo = extract_neigh(Grafo[nodo])
		#se il nodo ha valore int o meno viene gestito come userId o film
		if (isinstance(nodo, int)):
			if nodo in visitatiU:
				if tempc > 7:
					break
				tempc += 1
				nodo = prev
				continue
			else:
				visitatiU.append(nodo)
		else:
			if step == 0:
				pass#do nothing				
			elif nodo in visitatiF:
				if tempcc > 7:
					break
				tempcc += 1
				nodo = prev
				continue
			else:
				visitatiF.append(nodo)
		
		step += 1
		prev = nodo
	
	res = visitatiF[-1]
	visitatiF.clear()
	visitatiU.clear()
	return res
			
for index, row in test.iterrows():
	temp += 1	
	user = row['userId']
	film = row['title']
	for i in range(0, ripetere): 
		r = randomwalk(user)
		walk.append(r)
	#conta delle occorrenze dei film durante le ripetizioni della random walk + ordinamento
	consigli = sorted(Counter(walk).items(), key=lambda x: x[1], reverse=True)
	walk.clear()
	#controllo del film in lista:
	#SuperHit = primo della lista -> stesso film del test set
	#Top = il film è in alto nella lista dei suggerimenti
	#Hit = il film è nella lista dei suggerimenti
	if film == consigli[0][0]:
		superhit += 1
	for i in range(0,len(consigli)):		
		if film in consigli[i][0]:
			hit += 1
		if film in consigli[i][0] and i < top:	
			hit5 += 1
		elif film in consigli[i][0] and i < top+5:	
			hit10 += 1
		elif film in consigli[i][0] and i < top+10:	
			hit15 += 1
	#la top 15 dei suggerimenti viene stampata all'interno di un file
	with open("o.txt", "a") as f:
		print("Film suggeriti per l'utente: ", user, film, file=f)
		for elem in consigli[:top+10]:
			print(elem, file=f)			
	#stampa a schermo dei vari contatori a ogni iterazione
	print(temp, hit, hit5, hit10, hit15, superhit)

#calcolo della precisione dei suggerimenti e stampa (su file)
tot = len(test.index)
accuracy5 = hit5/tot
accuracy10 = hit10/tot
accuracy15 = hit15/tot
print('------------------------------------------------')
with open("o.txt", "a") as f:
	print("RISULTATO FINALE...\n\n")
	print('Hit: ',hit, file=f)
	print('Precisione delle top 5: ',accuracy5, hit5, file=f)
	print('Precisione delle top 10: ',accuracy10, hit10, file=f)
	print('Precisione delle top 15: ',accuracy15, hit15, file=f)
	print('SuperHit: ', superhit, file=f)

