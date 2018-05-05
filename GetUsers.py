import pandas as pd
import csv
import json
import pickle

class UsersList:

	def __init__(self):
		self.usersFileName = "users.txt"

	def readUsersFile(self, fileName):
		data = pd.read_csv(fileName, sep="\t", usecols = ['UserID', 'Latitude', 'Longitude'])
		data = data[:100]
		dictionary = dict()
		with open(self.usersFileName, 'wb') as txt_file:
			for index, row in data.iterrows():	
				dictionary[int(row['UserID'])] = [row['Latitude'], row['Longitude']]
			pickle.dump(dictionary, txt_file)

obj = UsersList()
obj.readUsersFile('dataset1/userlist.txt')