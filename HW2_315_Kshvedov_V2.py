#made for windows
import re
import numpy as np
from csv import reader
from scipy import spatial as sp
import time
import codecs

lines = []
movies = {}
useRate = []
numbUsers = 0
numbFilms = 0
simScores = {}


#Hash Optimized
movieNames = {}
movieRatings = {}
movieNonzero = {}
movieVLength = {}
movieNeighbor = {}
movieOrig = {}
movieEstimated = {}
recommendedMovies = {}

#reads all lines from user file and creates a 2D array
def countUsers(fName):
    global numbUsers
    oFile = codecs.open(fName, 'r', encoding="utf8")
    i = 0
    for line in reader(oFile):
        useRate.append(line)
        numbUsers = useRate[i][0]
        i += 1
    print("Users: ", numbUsers)
    oFile.close()

#Reads all movies from file and places in a 2D array
def readMovies(fName):
    oFile = open(fName, encoding="utf8")
    i = 0
    for line in reader(oFile):
        lines.append(line)
    print("Finished reading Movie File!")
    oFile.close()

#creates a library of movies based on
def movieLib():
    global numbFilms
    for movie in lines[1:]:
        tGenr = movie[2].split("|")
        tempDict = {}
        for each in tGenr:
            tempDict[each] = 1
        ratings = []
        for i in range(int(numbUsers)):
            ratings.append(0)
        #Hash
        movies[movie[0]] = [movie[1], tempDict, ratings, [], numbFilms]

        #Hash Optimized
        movieID = movie[0]
        movieNames[movieID] = movie[1]
        movieRatings[movieID] = ratings
        movieOrig[movieID] = ratings
        movieEstimated[movieID] = ratings
        numbFilms += 1
        #print(numbFilms)

    print("Movie Library Created!")

#inputs all user rating into each movie
def inputingRating():
    #Hash Optimized
    start = time.time()
    for rating in useRate[1:]:
        movieOrig[rating[1]][int(rating[0])-1] = float(rating[2])
        movieRatings[rating[1]][int(rating[0])-1] = float(rating[2])
    end = time.time()
    print("InputRating Hash Optimized in seconds: ",end - start)

#normalizes all movie ratings that are not zeroes
def normRating():
    #Hash Optimized
    start = time.time()
    for key in movieRatings.keys():
        temp = np.array(movieRatings[key])
        if np.count_nonzero(movieRatings[key]) != 0:
            avr = temp[temp.nonzero()].mean()
        for j in range(0,int(numbUsers)):
            if movieRatings[key][j] != 0:
                movieRatings[key][j] -= avr
        #print("Movie Ratings, optimized:", movieRatings[key])
        movieVLength[key] = np.linalg.norm(movieRatings[key])
        movieNonzero[key] = np.count_nonzero(movieRatings[key])
    end = time.time()
    print("normRating Hash Optimized in seconds: ",end - start)

#calculates the similarity score for a given movie and createa a dictionary of them
#The cases of movies that have not been rated at all, the cosine would be 0/0
#In those cases i place similarity of 0, this just means its completely different
#where a -1 would mean a negative correlation which could mean some similarities
def simulateScore():
    #Hash Optimized
    startHO = time.time()
    for key1 in movieNames.keys():
        #if int(key1) <= 200:
                start = time.time()
                topSim = []
                for key2 in movieNames.keys():
                    #if int(key2) <= 200:
                        #print(key2)
                        if key1 != key2:
                            #print ("nonzero: ", movieNonzero[key1],movieNonzero[key2])
                            if movieNonzero[key1] != 0 and movieNonzero[key2] != 0:
                                temp = movieVLength[key1]*movieVLength[key2]
                                temp1=np.dot(movieRatings[key1], movieRatings[key2])
                                temp2=float(temp1)/float(temp)
                                #print("(",temp1,")/",temp,"=",temp2," VS ", temp3)
                                topSim.append([key2,temp2])
                                #print(key2)
                            else:
                                topSim.append([key2, 0])
                topSim.sort()
                topSim.sort(reverse=True, key = lambda x: x[1])
                movieNeighbor[key1] = []
                for i in range(0,5):
                    movieNeighbor[key1].append(topSim[i])
                #print(movieNeighbor[key1])
                end = time.time()
                print(key1, "- simulateScore Hash Optimized in seconds: ",end - start)
    endHO = time.time()
    print("simulateScore Hash Optimized in seconds: ",endHO - startHO)
    print("Centered Similarity Scores Created!")

def estimateZeroRating():
    startHO = time.time()
    for key in movieNames.keys():
        #if int(key) <= 200:
            start = time.time()
            for i in range(int(numbUsers)):
                if movieOrig[key][i] == 0:
                    top = 0
                    bot = 0
                    for mov in movieNeighbor[key]:
                        top += movieOrig[mov[0]][i]*mov[1]
                        bot += mov[1]
                    if bot != 0:
                        movieEstimated[key][i] = top/bot
            end = time.time()
            #print(key, "- estimate Zero Ratings in seconds: ",end - start)
    endHO = time.time()
    print("estimate Zero Ratings in seconds: ",endHO - startHO)
    print("All zero ratings Estimated!")

def topFiveMoviesUser(file):
    startHO = time.time()
    for i in range(int(numbUsers)):
        temp = []
        for key in movieNames.keys():
            temp.append([key, movieEstimated[key][i]])
        temp.sort()
        temp.sort(reverse=True, key = lambda x: x[1])
        recommendedMovies[i]=[temp[0]]
        for j in range(1,5):
            recommendedMovies[i].append(temp[j])
        print("User: ", i+1,"Top 5 Recommended: ",recommendedMovies[i])
        file.write(str(i+1))
        file.write(" ")
        file.write(str(recommendedMovies[i][0][0]))
        file.write(" ")
        file.write(str(recommendedMovies[i][1][0]))
        file.write(" ")
        file.write(str(recommendedMovies[i][2][0]))
        file.write(" ")
        file.write(str(recommendedMovies[i][3][0]))
        file.write(" ")
        file.write(str(recommendedMovies[i][4][0]))
        file.write("\n")
    endHO = time.time()
    print("Top five for each user picked in: ",endHO - startHO)
    print("All user have a top five new movies to watch!")

if __name__ == '__main__':

    countUsers("./ratings.csv")
    readMovies("./movies.csv")
    writeFile = open("output.txt", "w")
    movieLib()
    inputingRating()
    normRating()
    simulateScore()
    estimateZeroRating()
    topFiveMoviesUser(writeFile)
    writeFile.close()
    #temp = np.linalg.norm([0,2,0,4,5])*np.linalg.norm([0,0,1,0,3])
    #simScores[(key1,key2)]=np.dot(movieRatings[key1], movieRatings[key2])/temp
    #temp1=np.dot([0,2,0,4,5],[0,0,1,0,3])
    #temp2=temp1/temp
    #temp3=1 - sp.distance.cosine([0,2,0,4,5],[0,0,1,0,3])
    #print("(",temp1,")/",temp,"=",temp2," VS ", temp3)