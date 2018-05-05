import pandas as pd
import csv
import pickle


class ServiceList:

	def __init__(self):
		self.usersFileName = "services.txt"

	def readServiceFile(self, fileName):
		data = pd.read_csv(fileName, sep="\t", usecols = ['ServiceID', 'Latitude', 'Longitude'])
		dictionary = dict()
		data = data[:500]
		with open(self.usersFileName, 'wb') as txt_file:
			for index, row in data.iterrows():
				if row['Latitude'] == 'null':
					row['Latitude'] = 0
				if row['Longitude'] == 'null':
					row['Longitude'] = 0				
				dictionary[int(row['ServiceID'])] = [float(row['Latitude']), float(row['Longitude'])]
			pickle.dump(dictionary, txt_file)

obj = ServiceList()
obj.readServiceFile('dataset1/wslist.txt')
