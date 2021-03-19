import argparse, json, csv, math
from datetime import datetime
import pandas as pd
import numpy as np
import pptk
from time import localtime, strftime
import h5py

# for nagpur india
utm_zone = 44
#IN_VEHICLE, STILL, UNKNOWN, TILTING, ON_BICYCLE

class Tables:
	def __init__(self):
		self.ts = []
		self.lat = []
		self.lon = []
		self.alt = []
		self.type = []

	def add(self, ts, lat, lon, alt, ty):
		self.ts.append(ts)
		self.lat.append(lat)
		self.lon.append(lon)
		self.alt.append(alt)
		self.type.append(ty)

def processData(data):

	csvfile = open(args.output + ".csv", 'w')
	filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	filewriter.writerow(['timestamp', 'latitude', 'longitude', 'altitude', 'type'])

	locations = data['locations']
	tables = Tables()

	for l, location in enumerate(locations):
		lat = float(location['latitudeE7'])/math.pow(10, 7)
		lon = float(location['longitudeE7'])/math.pow(10, 7)
		alt = float(location.get('altitude', 0))
		activity = location.get('activity', -1)

		if activity == -1:
			continue
		else:
			for m, currentActivity in enumerate(activity):
				confidanceType = "UNKNOWN"
				timestamp = datetime.utcfromtimestamp(int(currentActivity['timestampMs']) / 1000)
				activityType = currentActivity.get('activity', -1)
				if activityType == -1:
					continue
				else:
					confidance = 0
					for n, typeOfActivity in enumerate(activityType):
						myconfidance = typeOfActivity['confidence']
						if myconfidance > confidance:
							confidanceType = typeOfActivity['type']

					if int(args.type) == 0:
							filewriter.writerow([timestamp, lat, lon, alt, confidanceType])

					if int(args.type) == 1:
						tables.add(timestamp, lat, lon, alt, confidanceType)

	csvfile.close()

	# if int(args.type) == 1:
	# 	dt = h5py.vlen_dtype(np.dtype('int32'))
	# 	with h5py.File(args.output + ".hdf", 'w') as f:
	# 		aSet = f.create_dataset("timestamp", data=tables.ts, dtype = dt)
	# 		bSet = f.create_dataset("latitude", data=tables.lat)
	# 		cSet = f.create_dataset("longitude", data=tables.lon)
	# 		dSet = f.create_dataset("altitude", data=tables.alt)
	# 		eSet = f.create_dataset("type", data=tables.type)

	print('Done! Wrote ' + str(len(locations)) + ' points.')


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Convert Google Maps location history to csv file.')
	parser.add_argument('-i', '--input', action="store", help='Filepath to location history .json file.', required=True)
	parser.add_argument('-o', '--output', action="store", help='Filepath to write output', required=True)
	parser.add_argument('-t', '--type', action="store", type=int, help='Output file type (0, csv), (1, hdf)', required=True)

	args = parser.parse_args()
	googleLocationjson = open(args.input)
	googleLocationObj = json.load(googleLocationjson)
	data = processData(googleLocationObj)

	df = pd.read_csv(args.output)
	p = np.c_[ df['longitude'], df['latitude'], np.zeros(len(df))]
	v = pptk.viewer(p)
	v.attribute(df['type'])
	v.color_map('jet', scale=[0, 2000])


