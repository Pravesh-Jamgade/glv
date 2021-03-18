import argparse, json, csv, math
from datetime import datetime
import pandas as pd
import numpy as np
import pptk

def convert(data):
	locations = data['locations']
	with open(args.output, 'w') as csvfile:
	    filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	    filewriter.writerow(['timestamp', 'latitude', 'longitude', 'altitude', 'type'])
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

	    			filewriter.writerow([timestamp, lat, lon, alt, confidanceType])

	print('Done! Wrote ' + str(len(locations)) + ' points.')


def process():
    points = pd.read_csv(plt_file, skiprows=6, header=None,
                         parse_dates=[[5, 6]], infer_datetime_format=True)

    # for clarity rename columns
    points.rename(inplace=True, columns={'5_6': 'time', 0: 'lat', 1: 'lon', 3: 'alt', 4: 'label'})

    # remove unused columns
    points.drop(inplace=True, columns=[2, 4])

    return points

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Convert Google Maps location history to csv file.')
	parser.add_argument('-i', '--input', action="store", help='Filepath to location history .json file.', required=True)
	parser.add_argument('-o', '--output', action="store", help='Filepath to write output .csv file.', required=True)

	args = parser.parse_args()
	file = open(args.input)
	data = json.load(file)
	convert(data)
	df = pd.read_csv(args.output)
	p = np.c_[ df['lon', df['lat'], np.zeros(len(df))]]
	v = pptk.viewer(p)
	v.attribute(df['alt'])
