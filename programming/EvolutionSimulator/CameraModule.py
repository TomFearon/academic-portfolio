# Imports necessary modules
import math
import numpy as np

# Camera class
class Camera(): 
    # Initialisation function
    def __init__(self, environmentDimensions, screenPixelDimensions):
        # Determines structure of environment
        self.environmentDimensions = np.array(environmentDimensions)
        self.gridSquareLength = 12

        # Determines dimensions of pixels on user screen
        self.screenPixelDimensions = np.array(screenPixelDimensions)

        # Determine minimum grid square length, so that bottom right coordinate is within the environment when fully zoomed out
        minGridSquareLengths = self.screenPixelDimensions/self.environmentDimensions
        self.minGridSquareLength = math.ceil(np.max(minGridSquareLengths))
        
        # Determines centre of the environment
        self.centre = self.environmentDimensions//2
        # Determines the dimensions of the area of grid squares to be displayed on screen
        screenSquareDimensions = self.screenPixelDimensions//self.gridSquareLength
        # Determines top left of middle of environment - so that the centre of environment is in the centre of the user screen
        self.topLeft = self.centre - (screenSquareDimensions//2)

        # Boolean variable storing whether the view has changed since the last display
        self.viewChanged = True
    
    # Function to clamp coordinates of top left 
    def clamp_top_left(self, screenSquareDimensions):
        # Determines the max top left
        maxTopLeft = self.environmentDimensions - screenSquareDimensions
        # Clamps top left to max top left
        self.topLeft[0] = max(0,min(self.topLeft[0],maxTopLeft[0]))
        self.topLeft[1] = max(0,min(self.topLeft[1],maxTopLeft[1]))

    # Function to control movement of camera
    def move(self, displacement):
        # Converts displacement vector tuple into a ndarray
        displacement = np.array(displacement)
        # If displacement occurs 
        if np.any(displacement != 0):
            # Moves camera dependant on displacement and grid square length
            self.topLeft += displacement * math.floor(14/(self.gridSquareLength**(1/2)))

            # Determines new centre square of the screen
            screenSquareDimensions = self.screenPixelDimensions//self.gridSquareLength
            self.centre = self.topLeft + screenSquareDimensions//2

            # Clamps top left coordinates
            self.clamp_top_left(screenSquareDimensions)

            # Updates view changed variable
            self.viewChanged = True

    # Function to control zoom of camera:
    def zoom(self, zoom):
        # Adjusts grid square length according to zoom
        self.gridSquareLength += zoom
        # Clamps the grid square length to be above minimum and below 96
        self.gridSquareLength = min(96,max(self.minGridSquareLength,self.gridSquareLength))
        
        # Ensures centre square of the screen remains in the centre of the screen
        screenSquareDimensions = self.screenPixelDimensions//self.gridSquareLength
        self.topLeft = self.centre - screenSquareDimensions//2

        # Clamps top left coordinates
        self.clamp_top_left(screenSquareDimensions)

        # Updates view changed variable
        self.viewChanged = True
    
    # Displays section of environment being viewed by the camera
    def display(self, screen, environment, population):
        # Draws the environment grid squares
        environment.draw(screen, self.screenPixelDimensions, self.topLeft, self.gridSquareLength, self.viewChanged)
        # Draws the organisms
        population.draw(screen, self.screenPixelDimensions, self.topLeft, self.gridSquareLength, self.viewChanged)
        # Updates view changed variable
        self.viewChanged = False

