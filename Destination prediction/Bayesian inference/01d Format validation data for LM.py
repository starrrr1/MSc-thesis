# -*- coding: utf-8 -*-

"""
01c Format training data for LM.py

This script formats the training data so that it can be used for easy import in
R. Currently, the linear model includes the following explanatory variables:
    - Hour of the day
    - Day of the week
    - Week of the year
    - Haversine distance between starting and end point of the trip
    - Starting point
    - Destination
"""

from __future__ import division

import numpy as np
import pandas as pd

def haversine(p1, p2):
  """ haversine
      Calculate the great circle distance between two points 
      on the earth (specified in decimal degrees)
      
      Arguments:
      ----------
      p1: 2d numpy array
        Two-dimensional array containing longitude and latitude coordinates of points.
      p2: 2d numpy array
        Two-dimensional array containing longitude and latitude coordinates of points.
        
      Returns:
      --------
      dist: 1d numpy array 
        One-dimensional array with the distances between p1 and p2.
  """
  # Convert decimal degrees to radians 
  lon1, lat1, lon2, lat2 = map(np.radians, [p1[0], p1[1], p2[0], p2[1]])
  
  # Haversine formula 
  dlon = lon2 - lon1 
  dlat = lat2 - lat1 
  a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
  c = 2 * np.arcsin(np.sqrt(a)) 
  r = 6371 
  
  return c * r
  
if __name__ == "__main__":
  print "- 01d Format validation data for LM.py"
  
  # Define the filepaths
  filepath = "E:/MSc thesis/Processed data/train_binarized_trips_validation.csv"
  filepath_processed = "E:/MSc thesis/Processed data/val_lm.csv"
  chunk_size = 1000
  
  # Define variables to export
  expl_vars = ["TRIP_ID", "START_POINT_LON", "START_POINT_LAT", "TRUNC_POINT_LON", "TRUNC_POINT_LAT", "END_POINT_LON", "END_POINT_LAT", "START_CELL", "TRUNC_CELL", "END_CELL", "HOUR", "WDAY", "WEEK", "DURATION", "TRUNC_DURATION", "TRUNC_DISTANCE"]
  
  # Number of points used for the discretization
  N, M = (100, 75)

  # Define function that transforms cells to ids
  id_to_nr = lambda (i, j): N * j + i # (i + 1) 
  
  # Read in the file
  data_chunks = pd.read_csv(filepath_or_buffer = filepath,
                            sep = ",",
                            chunksize = chunk_size,
                            usecols = ["TRIP_ID", "TIMESTAMP", "START_POINT", "TRUNC_POINT", "END_POINT", "GRID_POLYLINE", "TRUNC_GRID_POLYLINE", "HOUR", "WDAY", "DURATION", "TRUNC_DURATION"],
                            converters = {"START_POINT": lambda x: eval(x),
                                          "TRUNC_POINT": lambda x: eval(x),
                                          "END_POINT": lambda x: eval(x),
                                          "GRID_POLYLINE": lambda x: eval(x),
                                          "TRUNC_GRID_POLYLINE": lambda x: eval(x)})
                                          
  # Iterate through the chunks
  for idx, chunk in enumerate(data_chunks): 
    # Convert string timestamp to datetime
    chunk["TIMESTAMP"] = pd.to_datetime(chunk["TIMESTAMP"])
    
    # Compute start points and truncated points
    chunk["START_POINT_LON"] = chunk["START_POINT"].map(lambda x: x[0])
    chunk["START_POINT_LAT"] = chunk["START_POINT"].map(lambda x: x[1])
    chunk["TRUNC_POINT_LON"] = chunk["TRUNC_POINT"].map(lambda x: x[0])
    chunk["TRUNC_POINT_LAT"] = chunk["TRUNC_POINT"].map(lambda x: x[1])

    # Get the cell id's
    chunk["START_CELL"] = chunk["GRID_POLYLINE"].map(lambda x: id_to_nr(x[0]))
    chunk["TRUNC_CELL"] = chunk["TRUNC_GRID_POLYLINE"].map(lambda x: id_to_nr(x[-1]))
    
    # Compute traversed distance
    chunk["TRUNC_DISTANCE"] = chunk.apply(lambda x: haversine(x["START_POINT"], x["TRUNC_POINT"]), axis = 1)
    
    # Compute week of year
    chunk["WEEK"] = chunk["TIMESTAMP"].dt.week
    
    # Attach final destination to the validation set (should not be used in prediction)
    chunk["END_CELL"] = chunk["GRID_POLYLINE"].map(lambda x: id_to_nr(x[-1]))
    chunk["END_POINT_LON"] = chunk["END_POINT"].map(lambda x: x[0])
    chunk["END_POINT_LAT"] = chunk["END_POINT"].map(lambda x: x[1])
    
    # Save the chunk to a file
    if idx == 0:
      chunk.to_csv(filepath_processed, header = True, index = False, columns = expl_vars)
    else:
      chunk.to_csv(filepath_processed, mode = "a", header = False, index = False, columns = expl_vars)
                                          
    print "-- Processed chunk %d of 11" % idx                      

    