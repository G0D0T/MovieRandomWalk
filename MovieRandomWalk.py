import networkx as nx
import numpy as np
import pandas as pd
import random as rdm
import matplotlib.pyplot as plt
#import csv

def extract_neigh(node, t = 0.8):
	neig = sorted(node.items(), key=lambda edge: edge[1]['rating'])
	threshold = int(len(neig)*t)
	neig = neig[threshold:]
	next = rdm.choice(neig)
	return next[0]

def consigli(reccomend, filt):
	print('----------------------------------')
	print('In base alla sua watchlist, le suggeriamo i seguenti film: ')
	for f in reccomend[filt:]:
		print(f)

typesMovies = {'movieId': np.dtype(int),'title': np.dtype(str),'genres' : np.dtype(str)}
typesRatings = {'userId': np.dtype(int),'movieId': np.dtype(int),'rating': np.dtype(float),'timestamp' : np.dtype(int)}

movies = pd.read_csv('movies.csv', dtype=typesMovies, low_memory = False)
ratings = pd.read_csv('ratings.csv', dtype=typesRatings, low_memory = False)

movie_ratings = pd.merge(movies, ratings)

movie_ratings.drop("timestamp", inplace = True, axis = 1)
movie_ratings.drop("movieId", inplace = True, axis = 1)
movie_ratings.drop("genres", inplace = True, axis = 1)

print(movie_ratings.sample(10))

G = nx.from_pandas_edgelist(movie_ratings, 'userId', 'title', ['rating'])
movie_ratings.to_csv('import.csv', index=False)
print(nx.info(G))
#nx.write_weighted_edgelist(G, 'movie.weighted.edgelist')

#print(G[184]['Flint (2017)']['rating']) #test
#print([n for n in G.neighbors(2)]) #vedo tutti i film visti da un certo utente
#print(G[2]) #vedo tutti i film visti da un certo utente con voto assegnato
#print([n for n in G.neighbors('Whiplash (2014)')]) #vedo tutti gli utenti che hanno visto un certo film

numSteps = 10
step = 0
flag = False #True per gli utenti, viceversa per i film
walk = []
visitedFilm = []
visitedUser = []
start = 1 #da sostituire con l'id utente che vuole avere un consiglio
giavisti = ([n for n in G.neighbors(start)])#.items()

def main():	
	global step
	global flag
	walk.append(start)
	visitedUser.append(start)
	for f in giavisti:
		visitedFilm.append(f)
	nodo = start
	prev = start
	primoF = True

	while step < numSteps:
		nodo = extract_neigh(G[nodo])
		print(nodo)
		if flag:
			if nodo not in visitedUser:
				visitedUser.append(nodo)			
			else:
				nodo = prev
				continue
		else:
			if nodo not in visitedFilm:
				visitedFilm.append(nodo)
			elif primoF:
				primoF = False
				flag = not flag
				continue
			else:
				nodo = prev
				continue

		walk.append(nodo)
		prev = nodo
		flag = not flag
		step += 1

	consigli(visitedFilm, len(giavisti))

main()

"""
film visti per esempio
'The Machinist (2004)'
'Harry Potter and the Prisoner of Azkaban (2004)'
'Toy Story (1995)'
'Pulp Fiction (1994)'
'The Mask'


for x in G.nodes():
      print ("Node:", x, "has total #degree:",G.degree(x), " , In_degree: ", G.out_degree(x)," and out_degree: ", G.in_degree(x))   
for u,v in G.edges():
      print ("Weight of Edge ("+str(u)+","+str(v)+")", G.get_edge_data(u,v))
	  
	  
	  Data = open('ratings.csv', "r")
next(Data, None)  # skip the first line in the input file
Graphtype = nx.Graph()  #undirected

G = nx.parse_edgelist(Data, delimiter=';', create_using=Graphtype, nodetype=int, data=(('rating', float),))
"""	  
