from re import error
import requests
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


#A coordinatePoint is a basic object that can store lat and long values
class coordinatePoint:
  def __init__(self, lat, long):
    self.lat = lat
    self.long = long
    self.isNorth = True if self.lat > 0 else False
    self.isEast = True if self.long > 0 else False
  def __str__(self):
    return "Lat: " + str(self.lat) + " Long: " + str(self.long)
  def getLat(self):
    return self.lat
  def getLong(self):
    return self.long
  def calcDistanceTo(self, other):
    earthRadius = 6378000 #In meters
    lat1 = self.lat
    long1 = self.long
    lat2 = other.getLat() 
    long2 = other.getLong()
    latDifference = (lat2 - lat1)/2
    longDifference = (long2 - long1) / 2
    a = np.square(np.sin(latDifference)) + (np.cos(lat1) * np.cos(lat2) * np.square(np.sin(longDifference)))
    sqrtA = np.sqrt(a)
    result = (2 * earthRadius) * np.arcsin(sqrtA)
    return str(result)
    
#A elevationPoint extends coordinatePoint and can store elevation as well
#Defaults elevation value to -1 if not provided
class elevationPoint(coordinatePoint):
  def __init__(self, lat, long, elev=-1):
    super().__init__(lat, long)
    if elev != -1:
      self.elev = elev
    else:
      self.elev = -1
    
  def __str__(self):
    return "Lat: " + str(self.lat) + " Long: " + str(self.long) + " Elev: " + str(self.elev)
    
  def getElev(self):
    return self.elev
    
  def setElev(self, elev):
    self.elev = elev


class cordMap:
  def __init__(self, coordinatePoint1, coordinatePoint2, accuracy, mapName):
    if accuracy < 0:
      raise error("Accuracy must be greater than or equal to 0")
    self.mapName = mapName
    if coordinatePoint1.getLat() > coordinatePoint2.getLat():
      self.latMax = coordinatePoint1.getLat()
      self.latMin = coordinatePoint2.getLat()
      self.is2dLat = False
    elif coordinatePoint1.getLat() < coordinatePoint2.getLat():
      self.latMax = coordinatePoint2.getLat()
      self.latMin = coordinatePoint1.getLat()
      self.is2dLat = False
    else:
      self.latMax = coordinatePoint1.getLat()
      self.latMin = coordinatePoint1.getLat()
      self.is2dLat = True
    if coordinatePoint1.getLong() > coordinatePoint2.getLong():
      self.longMax = coordinatePoint1.getLong()
      self.longMin = coordinatePoint2.getLong()
      self.is2dLong = False
    elif coordinatePoint1.getLong() < coordinatePoint2.getLong():
      self.longMax = coordinatePoint2.getLong()
      self.longMin = coordinatePoint1.getLong()
      self.is2dLong = False
    else:
      self.longMax = coordinatePoint1.getLong()
      self.longMin = coordinatePoint1.getLong()
      self.is2dLong = True

    self.latDistance = self.latMax - self.latMin
    self.longDistance = self.longMax - self.longMin
    self.sizeOfGrid = accuracy + 2
    self.lats = [-1] * self.sizeOfGrid
    self.longs = [-1] * self.sizeOfGrid
    self.grid = [[elevationPoint(-1, -1) for _ in range(self.sizeOfGrid)] for _ in range(self.sizeOfGrid)]
    
  def getName(self):
    return self.mapName
  #initGrid updates the grid's lat and long values to their respective values
  # This also initializes the lat and long arrays for debugging
  def initGrid(self):
    for i in range(self.sizeOfGrid):
      for j in range(self.sizeOfGrid):
        setLatValue = round(self.latMax - (i * self.latDistance / (self.sizeOfGrid - 1)), 6)
        setLongValue = round(self.longMin + (j * self.longDistance / (self.sizeOfGrid - 1)), 6)
        self.grid[i][j] = elevationPoint(setLatValue, setLongValue) 
        if i == 0:
          self.longs[j] = setLongValue
        if j == 0:
          self.lats[i] = setLatValue
  #printGridLats prints the grid lat values
  def printGridLats(self):
    for i in range(0, self.sizeOfGrid):
      for j in range(0, self.sizeOfGrid):
        print(self.grid[i][j].getLat(), end=' ')
      print("\n")
  #printGridLongs prints the grid long values
  def printGridLongs(self):
    for i in range(0, self.sizeOfGrid):
      for j in range(0, self.sizeOfGrid):
        print(self.grid[i][j].getLong(), end=' ')
      print("\n")
  #printGridElevations prints the grid elevations
  def printGridElevations(self):
    for i in range(0, self.sizeOfGrid):
      for j in range(0, self.sizeOfGrid):
        print(self.grid[i][j].getElev(), end=' ')
      print("\n")
  #printGrid prints all elevations along with headers for lat and longs
  #This should be used in place of any other print function for most cases
  def printGrid(self):
    print("GRID", end=' ')
    for header in range(0, self.sizeOfGrid):
      print(self.grid[0][header].getLong(), end=' ')
    print("\n")
    for i in range(0, self.sizeOfGrid):
      print(self.grid[i][0].getLat(), end=' ')
      for j in range(0, self.sizeOfGrid):
        currentPoint = self.grid[i][j]
        print(currentPoint.getElev(), end=' ')
      print("\n")

  
  def printEdges(self):
    for i in range(0, self.sizeOfGrid):
      print(self.lats[i], end=' ')
    print("\n")
    for j in range(0, self.sizeOfGrid):
      print(self.longs[j], end=' ')
    print("\n")

  
  def initElevations(self):
    print("Generating JSON file...")
    url = "https://api.open-elevation.com/api/v1/lookup?locations="
    fileToSend = {"locations": []}
    for i in range(0, self.sizeOfGrid):
      for j in range(0, self.sizeOfGrid):
        currentPoint = self.grid[i][j]
        fileToSend["locations"].append({"latitude": currentPoint.getLat(), "longitude":currentPoint.getLong()})
    #jsonifiedFileToSend = json.dumps(fileToSend) #DEBUGGING PURPOSES ONLY
    #print(jsonifiedFileToSend)
    print("Contacting Database...")
    response = requests.post(url, json=fileToSend)
    print("Data Recieved... Parsing...")
    #print(response.json())
    data = response.json()
    for i in range(len(data["results"])):
      databit = data["results"][i]
      self.grid[i // self.sizeOfGrid][i % self.sizeOfGrid].setElev(int(databit["elevation"]))
    self.printEdges()
    print("Elevations Generated! Feel free to printGrid")

  def Visualize(self):
    print("Generating Visualization...")
    self.fig = plt.figure()
    ax = self.fig.add_subplot(111, projection='3d')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_zlabel('Elevation')
    graphLats = []
    graphLongs = []
    graphElevations = []
    bottom = np.zeros((self.sizeOfGrid * self.sizeOfGrid))
    for i in range(0, self.sizeOfGrid):
      for j in range(0, self.sizeOfGrid):
        currentPoint = self.grid[i][j]
        graphLats.append(currentPoint.getLat())
        graphLongs.append(currentPoint.getLong())
        graphElevations.append(currentPoint.getElev())
    graphLats = np.array(graphLats)
    graphLongs = np.array(graphLongs)
    bottom = np.zeros((self.sizeOfGrid * self.sizeOfGrid))
    width = np.array([self.latDistance / (self.sizeOfGrid - 1)]*self.sizeOfGrid*self.sizeOfGrid)
    depth = np.array([self.longDistance / (self.sizeOfGrid - 1)]*self.sizeOfGrid*self.sizeOfGrid)
    
    ax.bar3d(graphLongs, graphLats, bottom, width, depth, graphElevations)
    plt.show()