# Import necessary modules
import math
import random as rnd
import numpy as np
import pygame as pg
import DatabaseModule as dm
import json

# Returns dot product for two 2-dimensional vectors
def dot_2(vector1, vector2):
    return vector1[0] * vector2[0] + vector1[1] * vector2[1]

# Linear interpolation function
def lerp(a, b, d):
    return a + d*(b-a)

# Function used to smooth out interpolation between gradients
def fade(x):
    return (6 * (x**5)) - (15 * (x**4)) + (10 * (x**3))

# Returns an array of random floats influenced by perlin noise
def perlin_grid(width, height, lattice1DScale = 16):
    # Validates that all arguments are integers 
    width, height, lattice1DScale  = int(width), int(height), int(lattice1DScale)
    
    # Declares primary list for this function
    perlinGrid = []
    
    # Creates gradient vector grid
    gradVectorGrid = []
    # Determines dimensions of gradient vector grid proportional to perlin grid
    gradVectorGridWidth = math.ceil(width / lattice1DScale) + 1
    gradVectorGridHeight = math.ceil(height / lattice1DScale) + 1
    # Assigns random gradient to each lattice point
    for y in range(gradVectorGridHeight):
        gradVectorGrid.append([])
        for x in range(gradVectorGridWidth):
            # Appends random gradient vector
            gradVectorGrid[y].append([math.cos(rnd.random()*2*math.pi), math.sin(rnd.random()*2*math.pi)])
    # Converts to ndarray to improve efficiency of operations
    gradVectorGrid = np.array(gradVectorGrid)
    
    # Appends sub-arrays to grid
    for y in range(height):
        perlinGrid.append([])
    
    # Assigns float to each coordinate in grid
    for y0 in range(gradVectorGridHeight-1):
        for x0 in range(gradVectorGridWidth-1):
            # Determines coordinates of alternative corner lattice points
            x1, y1 = x0 + 1, y0 + 1
            
            # Determines gradient vectors for each corner lattice point
            grad00 = gradVectorGrid[y0, x0]
            grad01 = gradVectorGrid[y1, x0]
            grad10 = gradVectorGrid[y0, x1]
            grad11 = gradVectorGrid[y1, x1]

            # Determines scaled x0 and y0 values
            x0Scaled = x0 * lattice1DScale
            y0Scaled = y0 * lattice1DScale
            # Assigns float to each coordinate in lattice
            for y in range(lattice1DScale):
                # Validates that y coordinate is not larger than grid height
                if y + y0Scaled >= height:
                    continue
                for x in range(lattice1DScale): 
                    # Validates that x coordinate is not larger than grid width
                    if x + x0Scaled >= width:
                        continue    

                    # Determines difference between coordinates and corner lattice points
                    dx0, dy0 = x / lattice1DScale, y / lattice1DScale
                    dx1, dy1 = dx0 - 1, dy0 - 1

                    # Determines dot products between gradient vector and (dx, dy) vector
                    # Computed for each corner lattice point
                    dot00 = dot_2((dx0, dy0), grad00)
                    dot01 = dot_2((dx0, dy1), grad01)
                    dot10 = dot_2((dx1, dy0), grad10)
                    dot11 = dot_2((dx1, dy1), grad11)

                    # Values created to smooth out interpolation
                    u, v = fade(dx0), fade(dy0)

                    # Creates perlin float by using linear interpolation
                    perlinFloat = lerp(lerp(dot00, dot10, u), lerp(dot01, dot11, u), v)

                    # Appends float to grid
                    perlinGrid[(y0 * lattice1DScale) + y].append(perlinFloat)
    
    # Returns final grid of floats as ndarray
    return np.array(perlinGrid)

# Define colours corresponding to temperatures
veryHighTempColour = np.array([231, 111, 81])
highTempColour = np.array([233, 196, 106])
mildTempColour = np.array([42, 180, 143])
lowTempColour = np.array([36, 102, 83])
veryLowTempColour = np.array([169, 214, 229])

# Defines colours corresponding to water depth
shallowWaterColour = np.array([78, 168, 222])
deepWaterColour = np.array([50, 120, 170])

# Environment grid square class
class EnvironmentGridSquare():
    # Initialisation function
    def __init__(self, temperature, waterDepth, floraPresent):
        # Stores conditions of grid square
        self.temperature = temperature
        # Represents temperature as a float between 0 and 1 to the nearest mutliple of 0.04 
        self.temperatureFloat = round(((temperature+15)/60)*25)/25
        # Stores whether flora is present or not as a boolean value
        self.floraPresent = floraPresent
        # Rounds the water depth down to the nearest multiple of 0.25
        self.waterDepth = math.floor(waterDepth*4)/4

        # Determines colour of displayed grid square
        # If square is water
        if waterDepth > 0:
            # Stores condition of square being water
            self.isWater = True
            # Determines colour by interpolating corresponding to depth
            self.colour = shallowWaterColour + self.waterDepth*(deepWaterColour - shallowWaterColour)
            # Alters colour by interpolating corresponding to temperature
            if self.temperatureFloat > 8/12:
                self.colour = self.colour + 0.2*(veryHighTempColour-self.colour)
            elif self.temperatureFloat > 7/12:
                self.colour = self.colour + 0.2*(highTempColour-self.colour)
            elif self.temperatureFloat > 5/12:
                self.colour = self.colour + 0.2*(mildTempColour-self.colour)
            elif self.temperatureFloat > 4/12:
                self.colour = self.colour + 0.2*(lowTempColour-self.colour)
            elif self.temperatureFloat > 3/12:
                self.colour = self.colour + 0.2*(veryLowTempColour -self.colour)
        # If square is not water
        else:
            # Stores condition of square not being water
            self.isWater = False
            # Determines colour by interpolating corresponding to temperature
            if self.temperatureFloat > 9/12:
                self.colour = veryHighTempColour
            elif self.temperatureFloat > 8/12:
                self.colour = highTempColour + (((self.temperatureFloat - 8/12)/(1/12))**(1/2))*(veryHighTempColour-highTempColour)
            elif self.temperatureFloat > 7/12:
                self.colour = mildTempColour + (((self.temperatureFloat - 7/12)/(1/12))**(1/2))*(highTempColour-mildTempColour)
            elif self.temperatureFloat > 5/12:
                self.colour = mildTempColour
            elif self.temperatureFloat > 4/12:
                self.colour = lowTempColour + ((self.temperatureFloat - 4/12)/(1/12)**(1/2))*(mildTempColour-lowTempColour)
            elif self.temperatureFloat > 3/12:
                self.colour = veryLowTempColour + (((self.temperatureFloat - 3/12)/(1/12))**(1/2))*(lowTempColour-veryLowTempColour)
            else:
                self.colour = veryLowTempColour
            
    # Draws the grid square
    def draw(self, screen, position, length):
        # Draws the square
        pg.draw.rect(screen, self.colour, (position[0],position[1],length,length))

# Function for determining depth of water for rivers
def get_river_depth(float, lower, upper, difference):
    if float > lower and float < upper:
        return -(2/upper)*abs(float - (upper/2)) + 1
    else:
        return 0
    
# Function for determining depth of water for lakes
def get_lake_depth(float, lower, upper, difference):
    if float > lower and float < upper:
        return ((float - lower)**(1/2))/(difference)
    else:
        return 0

# Environment class
class Environment():
    # Generate the environment
    def generate(self, noise, averageTemperature, averageWaterSize, floraDensity, environmentSize, screenPixelDimensions, waterNoiseRatio = 1, waterStyle = "Lakes", seed = rnd.random()):
        # Sets the seed
        rnd.seed(seed)
        
        # Validates that noise argument passed is in domain
        if noise < 0 or noise > 3:
            raise ValueError("Error: Noise must not be between 0 and 3.")
        # Converts noise to a value which can be passed through as an arugment for 'lattice1DScale'
        noiseConverted = math.ceil(288*((1/6)**noise))
        
        # Validates that environment size argument passed is within domain
        if environmentSize < 1/3 or environmentSize > 2:
            raise ValueError("Error: Environment size must be between 1/3 and 2.")
        # Scales dimensions and ensures dimensions are integers
        environmentWidth, environmentLength = np.ceil(np.array(screenPixelDimensions, dtype = float) * environmentSize).astype(int)
        
        # Validates that average temperature passed is within domain
        if averageTemperature < -15 or averageTemperature > 45:
            raise ValueError("Error: Average temperature must be between -15 and 45 (Celsius).")
        # Determines grid of floats for assigning temperature to regions of the environment
        temperatureGrid = perlin_grid(environmentWidth//4 + 1, environmentLength//4 + 1, lattice1DScale = noiseConverted)

        # Validates that water noise scale is greater than 0
        if waterNoiseRatio < 0.05:
            raise ValueError("Error: Water noise scale must be greater than or equal to 0.05.")
        # Determines grid of floats for assigining water sources to regions of the environment
        waterGrid = perlin_grid(environmentWidth//4 + 1,environmentLength//4 + 1, lattice1DScale = max(2,noiseConverted/waterNoiseRatio))
        
        # Validates that water style argument is valid
        if waterStyle.title() != "Rivers" and waterStyle.title() != "Lakes":
            raise ValueError("Error: Water style must be either rivers or lakes.")
        # Validates that average water size passed is within domain
        if averageWaterSize < 0 or averageWaterSize > 1:
            raise ValueError("Error: Average water size must be between 0 and 1.")
        # Assigns function to get water depth depending on water style and accordingly defines the arguments to be passed
        if waterStyle.title() == "Rivers":
            get_water_depth = get_river_depth
            upper = (averageWaterSize)**3
            lower = 0
            difference = upper - lower
        else:
            get_water_depth = get_lake_depth
            upper = 1
            lower = (1/25) ** (averageWaterSize)
            difference = upper - lower

        # Validates that flora density passed is within domain
        if floraDensity < 0 or floraDensity > 1:
            raise ValueError("Error: Flora density must be between 0 and 1.")
        # Determines grid of floats for assigning flora to regions of the environment
        floraGrid = perlin_grid(environmentWidth//4 + 1,environmentLength//4 + 1, lattice1DScale = 8)
        
        # Creates environment array, iterating through each grid square
        self.environment = []
        for y in range(environmentLength//4 + 1):
            self.environment.append([])
            for x in range(environmentWidth//4 + 1):
                    # Determines temperature and clamps it between -15 and 45 degrees celsius
                    temperature = max(-15,min(averageTemperature + (25 * (temperatureGrid[y,x])),45))
                    # Determines the depth of water in a square (will be 0 if none)
                    waterDepth = get_water_depth(waterGrid[y,x],lower,upper,difference)
                    # Determines whether flora is present on the square
                    floraPresent = False
                    if floraGrid[y,x] > 0.075 and waterDepth == 0:
                        if rnd.random() < floraDensity:
                            floraPresent = True
                    # Stores environment grid square object in array
                    self.environment[y].append(EnvironmentGridSquare(temperature, waterDepth, floraPresent))

        # Converts environment array to a ndarray - to speed up later computations
        self.environment = np.array(self.environment)
        # Determines dimensions of the environment (without extra squares)
        self.environmentDimensions = np.array([environmentWidth//4,environmentLength//4])

        # Creates the display surface object
        self.environmentSurface = pg.Surface((self.environmentDimensions[0] + 1, self.environmentDimensions[1] + 1)).convert()
        # Draws each grid square onto the display surface 
        for y in range(self.environmentDimensions[1]+1):
            for x in range(self.environmentDimensions[0]+1):
                colour = self.environment[y,x].colour
                self.environmentSurface.fill(colour, (x, y, 1, 1))
        
        # Saves the data of the environment in a dictionary
        self.data = {"noise": noise,
                    "averageTemperature": averageTemperature,
                    "averageWaterSize": averageWaterSize,
                    "floraDensity": floraDensity,
                    "environmentSize": environmentSize,
                    "screenPixelDimensions": screenPixelDimensions,
                    "waterNoiseRatio": waterNoiseRatio,
                    "waterStyle": waterStyle,
                    "seed": seed}

    # Saves the environment data to the table in the database
    def save(self, tableId):
        # Deletes the current table
        dm.delete_table(f"Environment{tableId}")
        # Creates the table
        dm.create_table(f"Environment{tableId}", [["Data", "TEXT"]])
        # Converts data dictionary into a valid format
        jsonData = json.dumps(self.data)
        # Inserts the converted data into table
        dm.insert_query(f"Environment{tableId}", [[jsonData]])
    
    # Loads environment from table in the database
    def load(self, tableId):
        # Selects coverted data from table
        jsonData = dm.select_query(f"Environment{tableId}", [["*"]])[0][1]
        # Converts data back into a dictionary
        data = json.loads(jsonData)
        # Generates the environment using the dictionary
        self.generate(**data)

    # Draws each grid square in the environment
    def draw(self, screen, screenPixelDimensions, topLeft, gridSquareLength, viewChanged):
        # Determines bottom right square of the section of the environment to be displayed
        bottomRight = np.array([topLeft[0] + screenPixelDimensions[0]//gridSquareLength + 1, topLeft[1] + screenPixelDimensions[1]//gridSquareLength + 1])

        # If the view of the environment has changed
        if viewChanged:
            # Determines dimensions of subsurface
            dimensions = bottomRight-topLeft
            # Extracts subsurface of environment of the section being viewed 
            visibleEnvironment = self.environmentSurface.subsurface((topLeft[0], topLeft[1], dimensions[0], dimensions[1]))
            # Scales the section of the environment accordingly
            self.visibleEnvironment = pg.transform.scale(visibleEnvironment, (dimensions[0] * gridSquareLength, dimensions[1] * gridSquareLength))

        # Displays subsurface of the environment
        screen.blit(self.visibleEnvironment, (0,0))

