import csv
import json
from geopy.distance import vincenty
import collections
import itertools
import pickle
import random
import numpy as np
from sklearn import linear_model

class QoSPredictor:
	
	def getDict(self, filename):
		dictionary = dict()
		with open(filename, 'rb') as txt_file:
			dictionary = pickle.load(txt_file)
		return dictionary

	def __init__(self):
		self.throughput = self.getDict("throughput1.txt")
		self.users = self.getDict("users.txt")
		self.services = self.getDict("services.txt")
		existingPairs = dict()
		for key, value in self.throughput.items():
			if value:
				existingPairs[key] = value
		self.throughput = existingPairs
		self.kdash = 20
		self.k = 10

	def createBuckets(self):
		self.users = collections.OrderedDict(sorted(self.users.items(), key=lambda e: (e[1][0], e[1][1])))
		self.services = collections.OrderedDict(sorted(self.services.items(), key=lambda e: (e[1][0], e[1][1])))
		bucketNumber = 0
		prevLoc = self.users[list(self.users.keys())[0]]
		latWidth = 0.1156
		longWidth = 0.1491
		self.assignedBucketToUser = [0]*len(self.users)
		self.usersInBucket = {}
		for key, value in self.users.items():
			if value[0] > (prevLoc[0] + latWidth) or value[1] > (prevLoc[1] + longWidth):
				bucketNumber = bucketNumber + 1
			self.assignedBucketToUser[key] = bucketNumber
			self.usersInBucket.setdefault(bucketNumber, []).append(key)
			prevLoc = value
			#print key, bucketNumber

		print "----------------------------------"
		bucketNumber = 0
		prevLoc = self.services[list(self.services.keys())[0]]
		self.servicesInBucket =  {}
		self.assignedBucketToService = [0]*(len(self.services))
		for key, value in self.services.items():
			if value[0] > (prevLoc[0] + latWidth) or value[1] > (prevLoc[1] + longWidth):
				bucketNumber = bucketNumber + 1
			self.assignedBucketToService[key] = bucketNumber
			self.servicesInBucket.setdefault(bucketNumber, []).append(key)
			prevLoc = value
			#print key, bucketNumber


	def getTopCorrelated(self, user, service):
		tput = self.throughput[user, service]
		userBucket = self.assignedBucketToUser[user]
		serviceBucket = self.assignedBucketToService[service]
		usersList = [u for u in self.usersInBucket[userBucket] if u!=user]
		servicesList = [s for s in self.servicesInBucket[serviceBucket] if s!=service]

		if len(usersList)*len(servicesList) < 5:
			usersList = random.sample(range(1, 100), 4)
			servicesList = random.sample(range(1,500), 5)
		
		self.userServicePairs = list(itertools.product(usersList, servicesList))
		sameBucketPairsDist = dict()
		sameBucketCorrelationDist = dict()


		for pair in self.userServicePairs:
			sameBucketPairsDist[pair] = self.getUserServicePairDist(user, service, pair[0], pair[1])
			sameBucketCorrelationDist[pair] = self.getCrossCorrelation(self.throughput[user, service], self.throughput[pair])


		orderedPairsByDist = collections.OrderedDict(sorted(sameBucketPairsDist.items(), key=lambda e: e[1]))
		orderedPairsByCorrelation = collections.OrderedDict(sorted(sameBucketCorrelationDist.items(), key=lambda e: e[1]))

		topCorrelatedPairs = []
		for key, value in orderedPairsByCorrelation.items():
			if len(topCorrelatedPairs) == self.k:
				break
			topCorrelatedPairs.append(key)
		return topCorrelatedPairs


	def getTopCorrelatedWithoutBuckets(self, user, service):
		tput = self.throughput[user, service]
		sameBucketPairsDist = dict()
		sameBucketCorrelationDist = dict()

		for key, value in self.throughput.items():
			if key[0] != user or key[1] != service:
				sameBucketPairsDist[key] = self.getUserServicePairDist(user, service, key[0], key[1])
		orderedPairsByDist = collections.OrderedDict(sorted(sameBucketPairsDist.items(), key=lambda e: e[1]))
		
		i = 0
		for key, value in orderedPairsByDist.items():
			if i == self.kdash:
				break
			sameBucketCorrelationDist[key] = self.getCrossCorrelation(tput, self.throughput[key])
			i = i + 1

		orderedPairsByCorrelation = collections.OrderedDict(sorted(sameBucketCorrelationDist.items(), key=lambda e: e[1]))

		topCorrelatedPairs = []
		for key, value in orderedPairsByCorrelation.items():
			if len(topCorrelatedPairs) == self.k:
				break
			topCorrelatedPairs.append(key)
		return topCorrelatedPairs



	def predictLasso(self, user, service):
		topCorrelatedPairs = self.getTopCorrelatedWithoutBuckets(user, service)

		temporalSequences = []
		temporalSequenceInput = self.throughput[user, service]
		for pair in topCorrelatedPairs:
			temporalSequences.append(self.throughput[pair])

		last = len(temporalSequences[0]) - 1

		temporalSequences = np.array(temporalSequences)
		predictSeq = temporalSequences[:,last]
		temporalSequences = np.delete(temporalSequences, last, 1)
		temporalSequences = np.transpose(temporalSequences)

		reg = linear_model.LinearRegression()	
		reg.fit(temporalSequences, temporalSequenceInput[:-1])	

		clf = linear_model.Lasso(alpha=0.1)
		clf.fit(temporalSequences, temporalSequenceInput[:-1])
		print("Predicted QoS with Lasso Regressor for user %d and service %d: %f",user, service, clf.predict(predictSeq.reshape(1, -1))[0])
		print("Predicted QoS with Linear Regressor for user %d and service %d: %f", user, service, reg.predict(predictSeq.reshape(1, -1))[0])
		print("Actual QoS value: ", temporalSequenceInput[-1])



	def getCrossCorrelation(self, seq1, seq2):
		return np.correlate(seq1, seq2)[0]


	def getUserServicePairDist(self, user1, service1, user2, service2):
		distance = 0.5*(self.getGeoDistance(self.users[user1], self.users[user2]) + 
		       self.getGeoDistance(self.services[service1], self.services[service2]))
		return distance

	def getGeoDistance(self, point1, point2):
		distance = vincenty(point1, point2).meters
		return distance


predictor = QoSPredictor()
predictor.createBuckets()
predictor.predictLasso(8,11)