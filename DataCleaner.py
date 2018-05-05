import pandas as pd
import csv
import pickle


class DataCleaner:

	def __init__(self):
		self.throughput = dict()
		self.tpFileName = "throughput2.txt"

	def readResponseFile(self, fileName):
		data = pd.read_csv(fileName, sep=" ", names = ['userID', 'serviceID', 'timeSlideID', 'rt'])
		data.set_index(["userID","serviceID"])
		#print data.index
		with open(self.tpFileName, 'wb') as txt_file:
			for uId in range(100):
				print uId
				for sID in range(500):
					df = data.query('userID == ' + str(uId) + ' and serviceID == ' + str(sID))
					tpRow = list(df['rt']);
					if(self.isRecordValid(tpRow)):
						self.throughput[uId, sID] = tpRow
			
			pickle.dump(self.throughput, txt_file)

	def readThroughputFile(self, fileName):
		data = pd.read_csv(fileName, sep=" ", names = ["userID", "serviceID", "timeSlideID", "throughput"])

	def cleanData(self):
		self.cleanedMatrix = []
		for row in self.responseMatrix:
			if(isRecordValid(row)):
				cleanedMatrix.append(row)

	def cleanRow(self, row):
		for i in range(1,len(row)):
			if(row[i] == 0):
				row[i] = row[i - 1]

	def isRecordValid(self, record):
		#print len(record)
		if(len(record) > 0 and record[-1] == -1):
			return False;
		return True

obj = DataCleaner()
obj.readResponseFile('dataset2/rtdata.txt')