# Import necessary modules
from UIElements import Background, Text, TextButton, ImageButton, InputBox, ValueSlider, RangeSlider, ScrollBar, Frame, LineGraph
import DatabaseModule as dm
import EnvironmentModule as em
import PopulationModule as pm
import CameraModule as cm
import pygame as pg
import math
import time
import random as rnd

# Main menu class
class MainMenu:
    # Creates the main menu using the screen dimensions
    def __init__(self, screenDimensions, windowData):
        # Creates and positions UI elements of main menu
        screenCentre = (screenDimensions[0]//2, screenDimensions[1]//2)
        self.background = Background()
        self.title = Text("Evolution simulator", 1, int(screenDimensions[1]*0.1), [screenCentre[0], screenDimensions[1]*0.1], title = True)
        self.environmentsButton = TextButton(screenDimensions[1]*0.2, 4, 5, 20, [screenCentre[0], screenDimensions[1] * 0.35], "Environments", 0, 0.4)
        self.settingsButton = TextButton(screenDimensions[1]*0.2, 4, 5, 20, [screenCentre[0], screenDimensions[1] * 0.6], "Settings", 0, 0.4)
        self.helpButton = TextButton(screenDimensions[1]*0.2, 4, 5, 20, [screenCentre[0], screenDimensions[1] * 0.85], "Help", 0, 0.4)

    # Handles interactions between user inputs and UI elements of the main menu
    def handle(self, mousePosition, events, mouseInputs, keyInputs, deltaTime):
        # Tracks and records input
        lmbPressed = False
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    lmbPressed = True

        # Tracks user interactions with UI elements
        enviromentsButtonPressed = self.environmentsButton.handle(mousePosition, lmbPressed)
        settingsButtonPressed = self.settingsButton.handle(mousePosition, lmbPressed)
        helpButtonPressed = self.helpButton.handle(mousePosition, lmbPressed)

        # Responds to user interactions
        if enviromentsButtonPressed:
            return "EnvironmentsMenu", [[0,0]]
        else:
            # Returns nothing in a manner which can be unpacked
            return None, None
    
    # Displays the main menu
    def display(self, screen):
        self.background.draw(screen)
        self.title.draw(screen)
        self.environmentsButton.draw(screen)
        self.settingsButton.draw(screen)
        self.helpButton.draw(screen)

# Environment slot class - used for the environments menu
class EnvironmentSlot:
    # Creates the environment slot, using the frame dimensions and the index of it
    def __init__(self, frameDimensions, i):
        # Extracts necessary values from database and stores them as attributes
        # Determines id of slot's environment and population tables in the database
        self.tableId = f"{math.floor((i+1)/10)}{(i+1)%10}"
        activeString = dm.select_query("Slots", [["Active"], f"id = {self.tableId}"])[0][0]
        # Determines whether slot is active or not (has an environment and population stored under its id)
        self.active = (activeString == "True")
        # Determines name of the slot
        self.name = dm.select_query("Slots", [["Name"], f"id = {self.tableId}"])[0][0]
        # Determines date of which the slt was last accessed
        self.dateLastAccessed = dm.select_query("Slots", [["DateLastAccessed"], f"id = {self.tableId}"])[0][0]

        # Variable indicating whether slot is being renamed or not - intially set to false
        self.renaming = False

        # Calculates the frame centre
        frameCentre = (frameDimensions[0]//2, frameDimensions[1]//2)
        # Creates UI elements if the slot is active
        if self.active:
            self.subFrame = Frame(frameDimensions[1] * 0.75, 4/3, 5, 10, (frameCentre[0],frameDimensions[1]//2 + frameDimensions[1] * i))
            self.title = Text(self.name, 0, int(frameDimensions[1]*0.1), (frameCentre[0], frameDimensions[1]*0.25 + frameDimensions[1] * i))
            self.dateLastAccessedText = Text(self.dateLastAccessed, 0, int(frameDimensions[1]*0.05), (frameCentre[0], frameDimensions[1]*0.15 + frameDimensions[1] * i))
            self.loadButton  = TextButton(frameDimensions[1]*0.15, 5, 5, 10, (frameCentre[0], frameDimensions[1]*0.425 + frameDimensions[1] * i), "Load", 0, 0.4)
            self.renameButton = TextButton(frameDimensions[1]*0.15, 5, 5, 10, (frameCentre[0], frameDimensions[1]*0.6 + frameDimensions[1] * i), "Rename", 0, 0.4)
            self.deleteButton = TextButton(frameDimensions[1]*0.15, 5, 5, 10, (frameCentre[0], frameDimensions[1]*0.775 + frameDimensions[1] * i), "Delete", 0, 0.4)
            self.renamingFrame = Frame(frameDimensions[1] * 0.35, 2.5, 5, 10, (frameCentre[0],frameDimensions[1]*0.325 + frameDimensions[1] * i))
            self.renamingInputBox = InputBox(frameDimensions[1] * 0.15, 5, 5, 5, (frameCentre[0],frameDimensions[1]*0.325 + frameDimensions[1] * i), textRatio=0.4, placeholderText="Enter name here", allowedCharacters="Alphanumeric")
        # Creates different set of UI elements if the slot is inactive
        else:
            self.subFrame = Frame(frameDimensions[1] * 0.5, 2, 5, 10, (frameCentre[0],frameDimensions[1]//2 + frameDimensions[1] * i))
            self.title = Text(self.name, 0, int(frameDimensions[1]*0.1), (frameCentre[0], frameDimensions[1]*0.35 + frameDimensions[1] * i))
            self.createNewButton = TextButton(frameDimensions[1]*0.25, 3, 5, 10, (frameCentre[0], frameDimensions[1]*0.6 + frameDimensions[1] * i), "Create new", 0, 0.4)

    # Handles user interactions with the slot
    def handle(self, mousePosition, lmbPressed, keydown, parentRect, offsetVector):
        # If the slot is active
        if self.active:
            # If the slot is not being renamed
            if not self.renaming:
                # If the load button is pressed
                if self.loadButton.handle(mousePosition, lmbPressed, parentRect = parentRect):
                    # Updates the date last accessed for the slot
                    dm.update_query("Slots",[[int(self.tableId), "True", self.name, time.strftime("%d/%m/%Y")]])
                    # Signals for the program to transition to the simulation window, providing the valid table id for the simulation to refer to
                    return "SimulationWindow", [self.tableId]
                # If the rename button is pressed
                if self.renameButton.handle(mousePosition, lmbPressed, parentRect = parentRect):
                    # Slot is set to not being renamed if currently being named and vice versa
                    self.renaming = not self.renaming
            # If mouse pressed and mouse is not colliding with the renaming frame's global position (will not be considered if 'renaming' is false)
            elif lmbPressed and not self.renamingFrame.rect.collidepoint((mousePosition[0] - parentRect.topleft[0], mousePosition[1] - parentRect.topleft[1])):
                # Set renaming to false
                self.renaming = False
                # Clears the input text in the renaming input box
                self.renamingInputBox.inputText = ""
            # If the delete button is pressed
            if self.deleteButton.handle(mousePosition, lmbPressed, parentRect = parentRect):
                # Updates slot's state to be empty accordingly
                dm.update_query("Slots",[[int(self.tableId), "False", "Empty slot", ""]])
                # Reloads the environment menu in the with the same offset inside the frame (as a result of the scroll bar)
                return "EnvironmentsMenu", [offsetVector]
        # If the slot is empty
        else:
            # If create new button is pressed
            if self.createNewButton.handle(mousePosition, lmbPressed, parentRect = parentRect):
                # Transfer user to environment creation
                return "EnvironmentConditionsMenu", [self.tableId]
        # If slot is being renamed
        if self.renaming:
            # Store input text entered
            newName = self.renamingInputBox.handle(mousePosition, lmbPressed, keydown, parentRect = parentRect)
            # If input text is enetered
            if newName:
                # Updates name attribute
                self.name = newName
                # Updates name to database
                dm.update_query("Slots",[[int(self.tableId), "True", self.name, self.dateLastAccessed]])
                # Reloads the environment menu in the with the same offset inside the frame (as a result of the scroll bar)
                return "EnvironmentsMenu", [offsetVector]
        
        # Returns nothing in a manner which can be unpacked
        return None, None
    
    # Offsets UI elements of the slot (varies whether slot is active or not)
    def offset(self, offsetVector):
        self.subFrame.offset(offsetVector)
        self.title.offset(offsetVector)
        if self.active:
            self.dateLastAccessedText.offset(offsetVector)
            self.loadButton.offset(offsetVector)
            self.renameButton.offset(offsetVector)
            self.deleteButton.offset(offsetVector)
            self.renamingFrame.offset(offsetVector)
            self.renamingInputBox.offset(offsetVector)
        else:
            self.createNewButton.offset(offsetVector)
    
    # Displays UI elements of the slot (varies whether slot is active or not)
    def display(self, surface):
        self.subFrame.draw(surface)
        self.title.draw(surface)
        if self.active:
            self.dateLastAccessedText.draw(surface)
            self.loadButton.draw(surface)
            self.renameButton.draw(surface)
            self.deleteButton.draw(surface)
            if self.renaming:
                self.renamingFrame.draw(surface)
                self.renamingInputBox.draw(surface)
        else:
            self.createNewButton.draw(surface)

# Environments menu class
class EnvironmentsMenu:
    # Creates the environments menu using the screen dimensions and window data
    def __init__(self, screenDimensions, windowData):
        # Determines the centre of the screen
        screenCentre = (screenDimensions[0]//2, screenDimensions[1]//2)
        # Creates main UI elements of the menu
        self.background = Background()
        self.title = Text("Environments", 1, int(screenDimensions[1]*0.1), [screenCentre[0], screenDimensions[1]*0.1], title = True)
        self.backButton = ImageButton(screenDimensions[0]*0.02, 2, (screenDimensions[0]*0.03, screenDimensions[0]*0.03), pg.image.load("Assets/BackArrow.png").convert_alpha(), 0.7)
        self.frame = Frame(screenDimensions[1]*0.75, 1.75, 5, 10, (screenCentre[0], screenDimensions[1] * 0.55))
        self.scrollBar = ScrollBar(screenDimensions[1]*0.65, 0.1, 5, 10, (screenDimensions[1]*1.2525, screenDimensions[1]*0.375), 0.1)

        # Creates 10 environment slots
        self.environmentSlots = []
        for i in range(10):
            self.environmentSlots.append(EnvironmentSlot((self.frame.rect.width, self.frame.rect.height), i))

        # Sets the offset vector of the UI elements within the frame (as a result of the scroll bar)
        self.offsetVector = windowData[0]
        # Calculates the max scroll Y offset (scroll bar will not affect X), dependent on screen dimensions - which relate to the size of the frame
        self.maxScrollOffset = -screenDimensions[1]*6.75
        # Adjusts the position of the scroll bar handle to coincide with the given offset vector (calculation is derived from rearranging other calculations related to the scroll bar)
        self.scrollBar.move_handle((self.offsetVector[1]/self.maxScrollOffset * (self.scrollBar.maxHandleCentreY - self.scrollBar.minHandleCentreY))+self.scrollBar.minHandleCentreY)

    # Handles interactions with the UI elements
    def handle(self, mousePosition, events, mouseInputs, keyInputs, deltaTime):
        # Tracks and records user inputs
        lmbPressed = False
        lmbHeld = False
        keydown = None
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    lmbPressed = True
            elif event.type == pg.KEYDOWN:
                keydown = event
        if mouseInputs[0]:
            lmbHeld = True

        # Handles interactions with the back button and records whether it's pressed
        backButtonPressed = self.backButton.handle(mousePosition, lmbPressed)

        # Handles interactiosn with the scroll bar and records its scorll progress
        scrollProgress = self.scrollBar.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        # Adjust the offset vector of the UI elemtns in the frame dependent on the scroll progress
        self.offsetVector[1] = self.maxScrollOffset * scrollProgress

        # Iterates through all environmnet slots
        for slot in self.environmentSlots:
            # Handles interactions with the slot and records whether it is signaling for a new window to be opened, if so, it stores data to be give to this window
            newWindow, windowData = slot.handle(mousePosition, lmbPressed, keydown, self.frame.rect, self.offsetVector)
            # If a new window was returned
            if newWindow:
                return newWindow, windowData
            # Offsets the slot
            slot.offset(self.offsetVector)

        # If the back button is pressed
        if backButtonPressed:
            # Signal for program to return to the main menu
            return "MainMenu", None
        # Returs nothing in a manner which can be unpacked
        else:
            return None, None
    
    # Displays the menu
    def display(self, screen):
        self.background.draw(screen)
        self.title.draw(screen)
        self.backButton.draw(screen)
        self.frame.draw(screen)
        self.scrollBar.draw(self.frame.surface)
        for slot in self.environmentSlots:
            slot.display(self.frame.surface)

# Environment conditions menu class
class EnvironmentConditionsMenu:
    # Creates the environment conditions menu
    def __init__(self, screenDimensions, windowData):
        # Stores the id of the slot's table in the database
        self.tableId = windowData[0]

        # Creates and positions UI elements which are outside of the centre frame
        screenCentre = (screenDimensions[0]//2, screenDimensions[1]//2)
        self.background = Background()
        self.title = Text("Environment conditions", 1, int(screenDimensions[1]*0.1), (screenCentre[0], screenDimensions[1]*0.1), title = True)
        self.backButton = ImageButton(screenDimensions[0]*0.02, 2, (screenDimensions[0]*0.03, screenDimensions[0]*0.03), pg.image.load("Assets/BackArrow.png").convert_alpha(), 0.7)
        self.nextButton = TextButton(screenDimensions[1]*0.04, 5, 5, 10, (screenDimensions[0] - screenDimensions[1]*0.12, screenDimensions[1] * 0.04), "Next", 0, 0.6)
        self.frame = Frame(screenDimensions[1]*0.75, 1.75, 5, 10, (screenCentre[0], screenDimensions[1] * 0.55))
        
        # Creates and positions UI elements which are inside of the centre frame
        self.scrollBar = ScrollBar(screenDimensions[1]*0.65, 0.1, 5, 10, (screenDimensions[1]*1.2525, screenDimensions[1]*0.375), 0.475)
        # Calculates frame structure
        frameDimensions = [self.frame.width, self.frame.height]
        frameCentre = [frameDimensions[0]//2, frameDimensions[1]//2]
        # Stores arguments for generating the environment in a dictionary
        self.arguments = {"noise": 1,
                        "averageTemperature": 15,
                        "averageWaterSize": 0.5,
                        "floraDensity": 0.1,
                        "environmentSize": 1/3,
                        "screenPixelDimensions": screenDimensions,
                        "waterNoiseRatio": 0.1,
                        "waterStyle": "Rivers",
                        "seed": rnd.random()
                        }
        # Noise argument
        self.noiseTitle = Text("Noise:", 1, int(frameDimensions[1]*0.075), (frameCentre[0], frameDimensions[1]*0.1))
        self.noiseSlider = ValueSlider(frameDimensions[1]*0.05, 20, 4, 10, (frameCentre[0], frameDimensions[1]*0.2), frameDimensions[1]*0.04, [0,2], 1, 0.4)
        # Average temperature argument
        self.averageTemperatureTitle = Text("Average temperature (°C):", 1, int(frameDimensions[1]*0.075), (frameCentre[0], frameDimensions[1]*0.35))
        self.averageTemperatureSlider = ValueSlider(frameDimensions[1]*0.05, 20, 4, 10, [frameCentre[0], frameDimensions[1]*0.45], frameDimensions[1]*0.04, [-15,45], 15, 0.4)
        # Average water size argument  
        self.averageWaterSizeTitle = Text("Average water body size:", 1, int(frameDimensions[1]*0.075), (frameCentre[0], frameDimensions[1]*0.6))
        self.averageWaterSizeSlider = ValueSlider(frameDimensions[1]*0.05, 20, 4, 10, [frameCentre[0], frameDimensions[1]*0.7], frameDimensions[1]*0.04, [0,1], 0.5, 0.4)
        # Flora density argument
        self.floraDensityTitle = Text("Flora density:", 1, int(frameDimensions[1]*0.075), (frameCentre[0], frameDimensions[1]*0.85))
        self.floraDensitySlider = ValueSlider(frameDimensions[1]*0.05, 20, 4, 10, [frameCentre[0], frameDimensions[1]*0.95], frameDimensions[1]*0.04, [0,0.25], 0.1, 0.4)
        # Water noise ratio argument
        self.waterNoiseRatioTitle = Text("Water noise ratio:", 1, int(frameDimensions[1]*0.075), (frameCentre[0], frameDimensions[1]*1.1))
        self.waterNoiseRatioSlider = ValueSlider(frameDimensions[1]*0.05, 20, 4, 10, (frameCentre[0], frameDimensions[1]*1.2), frameDimensions[1]*0.04, [0.05,5], 1, 0.4)
        # Water style argument
        self.waterStyleTitle = Text("Water style:", 1, int(frameDimensions[1]*0.075), (frameCentre[0], frameDimensions[1]*1.35))
        self.waterStyleText = Text("Rivers", 0, int(frameDimensions[1]*0.05), (frameCentre[0], frameDimensions[1]*1.45))
        self.riversButton = TextButton(frameDimensions[1]*0.05, 5, 5, 10, (frameCentre[0] - frameDimensions[1]*0.15, frameDimensions[1]*1.55), "Rivers", 0, 0.6)
        self.lakesButton = TextButton(frameDimensions[1]*0.05, 5, 5, 10, (frameCentre[0] + frameDimensions[1]*0.15, frameDimensions[1]*1.55), "Lakes", 0, 0.6)
        # Environment size argument
        self.environmentSizeTitle = Text("Environment size:", 1, int(frameDimensions[1]*0.075), (frameCentre[0], frameDimensions[1]*1.7))
        self.environmentSizeSlider = ValueSlider(frameDimensions[1]*0.05, 20, 4, 10, (frameCentre[0], frameDimensions[1]*1.8), frameDimensions[1]*0.04, [1/3,2], 1/3, 0.4)
        # Seed argument
        self.seedTitle = Text("Generation seed:", 1, int(frameDimensions[1]*0.075), (frameCentre[0], frameDimensions[1]*1.95))
        self.seedInputBox = InputBox(frameDimensions[1]*0.1, 5, 5, 10, (frameCentre[0], frameDimensions[1]*2.075), 0.4, placeholderText = "Enter seed (optional)", allowedCharacters = "Numeric")
        
        # Stores the offset vector of the UI elements in the frame
        self.offsetVector = [0,0]
        # Stores the max offset vector of the elements in the frame
        self.maxScrollOffset = -frameDimensions[1]*1.175

    # Handles user interactions with the menu
    def handle(self, mousePosition, events, mouseInputs, keyInputs, deltaTime):
        # Tracks and records user inputs
        lmbPressed = False
        lmbHeld = False
        keydown = None
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    lmbPressed = True
            elif event.type == pg.KEYDOWN:
                keydown = event
        if mouseInputs[0]:
            lmbHeld = True

        # Handles interactactions with the UI elements outside of the centre frame
        backButtonPressed = self.backButton.handle(mousePosition, lmbPressed)
        nextButtonPressed = self.nextButton.handle(mousePosition, lmbPressed)

        # Handles interactions with the UI elements inside of the centre frame
        # All sliders are handled, with the respective value in the dictionary being altered (if the sliders are adjusted)
        self.arguments["noise"] = self.noiseSlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        self.arguments["averageTemperature"] = self.averageTemperatureSlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        self.arguments["averageWaterSize"] = self.averageWaterSizeSlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        self.arguments["floraDensity"] = self.floraDensitySlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        self.arguments["waterNoiseRatio"] = self.waterNoiseRatioSlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        # If rivers button is pressed, set water style of environment to rivers
        if self.riversButton.handle(mousePosition, lmbPressed, parentRect = self.frame.rect):
            self.arguments["waterStyle"] = "Rivers"
            self.waterStyleText.change_text("Rivers")
        # if lakes button is pressed, set water style of environment to lakes
        if self.lakesButton.handle(mousePosition, lmbPressed, parentRect = self.frame.rect):
            self.arguments["waterStyle"] = "Lakes"
            self.waterStyleText.change_text("Lakes")
        self.arguments["environmentSize"] = self.environmentSizeSlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        # Records input of the seed input box
        seed = self.seedInputBox.handle(mousePosition, lmbPressed, keydown, parentRect = self.frame.rect)
        # If an input was entered
        if seed:
            # Update the 'seed' value
            self.arguments["seed"] = seed

        # Determines scroll progress of the scroll bar by handling interctiosn with the scroll bar
        scrollProgress = self.scrollBar.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        # Updates the offset vector
        self.offsetVector[1] = self.maxScrollOffset * scrollProgress

        # Offsets the UI elements in the centre frame dependent on scroll progress
        self.noiseTitle.offset(self.offsetVector)
        self.noiseSlider.offset(self.offsetVector)
        self.averageTemperatureTitle.offset(self.offsetVector)
        self.averageTemperatureSlider.offset(self.offsetVector)
        self.averageWaterSizeTitle.offset(self.offsetVector)
        self.averageWaterSizeSlider.offset(self.offsetVector)
        self.floraDensityTitle.offset(self.offsetVector)
        self.floraDensitySlider.offset(self.offsetVector)
        self.waterNoiseRatioTitle.offset(self.offsetVector)
        self.waterNoiseRatioSlider.offset(self.offsetVector)
        self.waterStyleTitle.offset(self.offsetVector)
        self.waterStyleText.offset(self.offsetVector)
        self.riversButton.offset(self.offsetVector)
        self.lakesButton.offset(self.offsetVector)
        self.environmentSizeTitle.offset(self.offsetVector)
        self.environmentSizeSlider.offset(self.offsetVector)
        self.seedTitle.offset(self.offsetVector)
        self.seedInputBox.offset(self.offsetVector)

        # If back button is pressed, return to environment slots menu
        if backButtonPressed:
            return "EnvironmentsMenu", [[0,0]]
        # If next button is pressed, generate and save the environment and go to population conditions menu
        elif nextButtonPressed:
            environment = em.Environment()
            environment.generate(**self.arguments)
            environment.save(self.tableId)
            return "PopulationConditionsMenu", [self.tableId, environment]
        # If none are pressed, return nothing in a manner which is unpackable
        else:
            return None, None

    # Displays the menu
    def display(self, screen):
        # Draws the UI elements outside of the centre frame
        self.background.draw(screen)
        self.title.draw(screen)
        self.backButton.draw(screen)
        self.nextButton.draw(screen)
        self.frame.draw(screen)

        # Draws the UI elements inside of the centre frame
        self.scrollBar.draw(self.frame.surface)
        self.noiseTitle.draw(self.frame.surface)
        self.noiseSlider.draw(self.frame.surface)
        self.averageTemperatureTitle.draw(self.frame.surface)
        self.averageTemperatureSlider.draw(self.frame.surface)
        self.averageWaterSizeTitle.draw(self.frame.surface)
        self.averageWaterSizeSlider.draw(self.frame.surface)
        self.floraDensityTitle.draw(self.frame.surface)
        self.floraDensitySlider.draw(self.frame.surface)
        self.waterNoiseRatioTitle.draw(self.frame.surface)
        self.waterNoiseRatioSlider.draw(self.frame.surface)
        self.waterStyleTitle.draw(self.frame.surface)
        self.waterStyleText.draw(self.frame.surface)
        self.riversButton.draw(self.frame.surface)
        self.lakesButton.draw(self.frame.surface)
        self.environmentSizeTitle.draw(self.frame.surface)
        self.environmentSizeSlider.draw(self.frame.surface)
        self.seedTitle.draw(self.frame.surface)
        self.seedInputBox.draw(self.frame.surface)

# Populations conditions menu class definition
class PopulationConditionsMenu:
    # Creates the menu
    def __init__(self, screenDimensions, windowData):
        # Stores the id of the slot's table in the database
        self.tableId = windowData[0]
        # Stores the generated environment object respective to the population - used to generate the population
        self.environment = windowData[1]

        # Creates and positions UI elements which are outside of the centre frame
        screenCentre = (screenDimensions[0]//2, screenDimensions[1]//2)
        self.background = Background()
        self.title = Text("Population conditions", 1, int(screenDimensions[1]*0.1), (screenCentre[0], screenDimensions[1]*0.1), title = True)
        self.backButton = ImageButton(screenDimensions[0]*0.02, 2, (screenDimensions[0]*0.03, screenDimensions[0]*0.03), pg.image.load("Assets/BackArrow.png").convert_alpha(), 0.7)
        self.nextButton = TextButton(screenDimensions[1]*0.04, 5, 5, 10, (screenDimensions[0] - screenDimensions[1]*0.12, screenDimensions[1] * 0.04), "Next", 0, 0.6)
        self.frame = Frame(screenDimensions[1]*0.75, 1.75, 5, 10, (screenCentre[0], screenDimensions[1] * 0.55))

        # Creates and positions UI elements which are inside of the centre frame
        self.scrollBar = ScrollBar(screenDimensions[1]*0.65, 0.1, 5, 10, (screenDimensions[1]*1.2525, screenDimensions[1]*0.375), 0.475)
        # Calculates frame structure
        frameDimensions = [self.frame.width, self.frame.height]
        frameCentre = [frameDimensions[0]//2, frameDimensions[1]//2]
        # Stores arguments for generating the population in a dictionary
        self.arguments = {"speciesCount": 1,
                        "speciesSize": 15,
                        "environment": self.environment.environment,
                        "environmentDimensions": self.environment.environmentDimensions,
                        "speedRange": [0.2, 0.8],
                        "sightRange": [0.2,0.8],
                        "temperatureControlRange": [0,1],
                        "metabolicRateMultiplier": 2/75,
                        "maxSightRadius": 20
                        }
        # Species count argument
        self.speciesCountTitle = Text("Initial number of species:", 1, int(frameDimensions[1]*0.075), [frameCentre[0], frameDimensions[1]*0.1])
        self.speciesCountSlider = ValueSlider(frameDimensions[1]*0.05, 20, 4, 10, (frameCentre[0], frameDimensions[1]*0.2), frameDimensions[1]*0.04, [2,25], 10, 0.4)
        # Species size argument
        self.speciesSizeTitle = Text("Species' initial size:", 1, int(frameDimensions[1]*0.075), [frameCentre[0], frameDimensions[1]*0.35])
        self.speciesSizeSlider = ValueSlider(frameDimensions[1]*0.05, 20, 4, 10, (frameCentre[0], frameDimensions[1]*0.45), frameDimensions[1]*0.04, [2,25], 10, 0.4)
        # Speed range argument
        self.speedRangeTitle = Text("Initial speed range:", 1, int(frameDimensions[1]*0.075), [frameCentre[0], frameDimensions[1]*0.6])
        self.speedRangeSlider = RangeSlider(frameDimensions[1]*0.05, 20, 4, 10, (frameCentre[0], frameDimensions[1]*0.7), frameDimensions[1]*0.04, [0,100], [20,80], 0.4)
        # Sight range argument
        self.sightRangeTitle = Text("Initial sight range:", 1, int(frameDimensions[1]*0.075), [frameCentre[0], frameDimensions[1]*0.85])
        self.sightRangeSlider = RangeSlider(frameDimensions[1]*0.05, 20, 4, 10, (frameCentre[0], frameDimensions[1]*0.95), frameDimensions[1]*0.04, [0,100], [20,80], 0.4)
        # Temperature control range arugment
        self.temperatureControlRangeTitle = Text("Initial temperature control range:", 1, int(frameDimensions[1]*0.075), [frameCentre[0], frameDimensions[1]*1.1])
        self.temperatureControlRangeSlider = RangeSlider(frameDimensions[1]*0.05, 20, 4, 10, (frameCentre[0], frameDimensions[1]*1.2), frameDimensions[1]*0.04, [0,100], [0,100], 0.4)
        # Metabolic rate mutliplier argument
        self.metabolicRateMultiplierTitle = Text("Metabolic rate multiplier:", 1, int(frameDimensions[1]*0.075), [frameCentre[0], frameDimensions[1]*1.35])
        self.metabolicRateMultiplierSlider = ValueSlider(frameDimensions[1]*0.05, 20, 4, 10, (frameCentre[0], frameDimensions[1]*1.45), frameDimensions[1]*0.04, [0.5,1.5], 1, 0.4)
        # Max sight radius argument
        self.maxSightRadiusTitle = Text("Max sight radius:", 1, int(frameDimensions[1]*0.075), [frameCentre[0], frameDimensions[1]*1.6])
        self.maxSightRadiusSlider = ValueSlider(frameDimensions[1]*0.05, 20, 4, 10, (frameCentre[0], frameDimensions[1]*1.7), frameDimensions[1]*0.04, [5,40], 20, 0.4)

        # Stores the offset vector of the UI elements in the frame
        self.offsetVector = [0,0]
        # Stores the max offset vector of the frame
        self.maxScrollOffset = -frameDimensions[1]*0.775

    # Handles user interactions with the menu
    def handle(self, mousePosition, events, mouseInputs, keyInputs, deltaTime):
        # Tracks and records user inputs
        lmbPressed = False
        lmbHeld = False
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    lmbPressed = True
        if mouseInputs[0]:
            lmbHeld = True

        # Handles interactactions with the UI elements outside of the centre frame
        backButtonPressed = self.backButton.handle(mousePosition, lmbPressed)
        nextButtonPressed = self.nextButton.handle(mousePosition, lmbPressed)

        # Handles interactactions with the UI elements inside of the centre frame
        # All sliders are handled, with the respective value in the dictionary being altered (if the sliders are adjusted)
        self.arguments["speciesCount"] = self.speciesCountSlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        self.arguments["speciesSize"] = self.speciesSizeSlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        # Determines and converts speed range
        speedRange = self.speedRangeSlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        self.arguments["speedRange"][0], self.arguments["speedRange"][1] = speedRange[0]/100, speedRange[1]/100
        # Determines and converts sight range
        sightRange = self.sightRangeSlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        self.arguments["sightRange"][0], self.arguments["sightRange"][1] = sightRange[0]/100, sightRange[1]/100
        # Determines and converts temp control range
        temperatureControlRange = self.temperatureControlRangeSlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        self.arguments["temperatureControlRange"][0],  self.arguments["temperatureControlRange"][1] = temperatureControlRange[0]/100, temperatureControlRange[1]/100
        # Determines and converts metabolic rate multiplier
        self.arguments["metabolicRateMultiplier"] = self.metabolicRateMultiplierSlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect) * (2/75)
        # Determines max sight radius
        self.arguments["maxSightRadius"] = round(self.maxSightRadiusSlider.handle(mousePosition, lmbHeld, parentRect = self.frame.rect))

        # Determines scroll progress of the scroll bar by handling interactions with the scroll bar
        scrollProgress = self.scrollBar.handle(mousePosition, lmbHeld, parentRect = self.frame.rect)
        # Updates the offset vector
        self.offsetVector[1] = self.maxScrollOffset * scrollProgress

        # Offsets the UI elements in the centre frame dependent on scroll progress
        self.speciesCountTitle.offset(self.offsetVector)
        self.speciesCountSlider.offset(self.offsetVector)
        self.speciesSizeTitle.offset(self.offsetVector)
        self.speciesSizeSlider.offset(self.offsetVector)
        self.speedRangeTitle.offset(self.offsetVector)
        self.speedRangeSlider.offset(self.offsetVector)
        self.sightRangeTitle.offset(self.offsetVector)
        self.sightRangeSlider.offset(self.offsetVector)
        self.temperatureControlRangeTitle.offset(self.offsetVector)
        self.temperatureControlRangeSlider.offset(self.offsetVector)
        self.metabolicRateMultiplierTitle.offset(self.offsetVector)
        self.metabolicRateMultiplierSlider.offset(self.offsetVector)
        self.maxSightRadiusTitle.offset(self.offsetVector)
        self.maxSightRadiusSlider.offset(self.offsetVector)

        # If back button pressed, return to the environment conditions menu
        if backButtonPressed:
            return "EnvironmentConditionsMenu", [self.tableId]
        # If next button pressed generate and save the population and go to simulation window
        elif nextButtonPressed:
            population = pm.Population()
            population.generate(**self.arguments)
            population.save(self.tableId)
            # Records important data regarding the population
            population.record(self.tableId, newTable = True)
            dm.update_query("Slots", [[int(self.tableId), "True", f"Environment {int(self.tableId)}", time.strftime("%d/%m/%Y")]])
            return "SimulationWindow", [self.tableId]
        # If none are pressed, return nothing in a manner which is unpackable
        else:
            return None, None
    
    # Displays the menu
    def display(self, screen):
        # Draws the UI elements outside of the centre frame
        self.background.draw(screen)
        self.title.draw(screen)
        self.backButton.draw(screen)
        self.nextButton.draw(screen)
        self.frame.draw(screen)

        # Draws the UI elements which are inside of the centre frame
        self.scrollBar.draw(self.frame.surface)
        self.speciesCountTitle.draw(self.frame.surface)
        self.speciesCountSlider.draw(self.frame.surface)
        self.speciesSizeTitle.draw(self.frame.surface)
        self.speciesSizeSlider.draw(self.frame.surface)
        self.speedRangeTitle.draw(self.frame.surface)
        self.speedRangeSlider.draw(self.frame.surface)
        self.sightRangeTitle.draw(self.frame.surface)
        self.sightRangeSlider.draw(self.frame.surface)
        self.temperatureControlRangeTitle.draw(self.frame.surface)
        self.temperatureControlRangeSlider.draw(self.frame.surface)
        self.metabolicRateMultiplierTitle.draw(self.frame.surface)
        self.metabolicRateMultiplierSlider.draw(self.frame.surface)
        self.maxSightRadiusTitle.draw(self.frame.surface)
        self.maxSightRadiusSlider.draw(self.frame.surface)

# Simulation window class
class SimulationWindow:
    # Creates the window
    def __init__(self, screenDimensions, windowData):
        # Stores id used to find the table for the environment and population
        self.tableId = windowData[0]
        # Loads the environment
        self.environment = em.Environment()
        self.environment.load(self.tableId)
        # Loads the population
        self.population = pm.Population()
        self.population.load(self.environment.environment, self.environment.environmentDimensions, self.tableId)
        # Creates the camera object
        self.camera = cm.Camera(self.environment.environmentDimensions, screenDimensions)
        # Creates variable to track milliseconds since initialisation of simulation
        self.totalTime = 0
        # Sets simulation speed
        self.timeSpeed = 1
        # Sets mutation intensity of offspring
        self.mutationIntensity = 0.05
        
        # Calculates the centre of the screen
        screenCentre = (screenDimensions[0]//2, screenDimensions[1]//2)

        # Creates the UI elements displayed on the screen at all times
        self.backButton = ImageButton(screenDimensions[0]*0.02, 2, (screenDimensions[0]*0.03, screenDimensions[0]*0.03), pg.image.load("Assets/BackArrow.png").convert_alpha(), 0.7)
        self.settingsButton = ImageButton(screenDimensions[0]*0.02, 2, (screenDimensions[0]*0.08, screenDimensions[0]*0.03), pg.image.load("Assets/Gear.png").convert_alpha(), 0.7)
        self.statisticsButton = ImageButton(screenDimensions[0]*0.02, 2, (screenDimensions[0]*0.13, screenDimensions[0]*0.03), pg.image.load("Assets/StatisticsIcon.png").convert_alpha(), 0.7)
        self.saveButton = ImageButton(screenDimensions[0]*0.02, 2, (screenDimensions[0]*0.18, screenDimensions[0]*0.03), pg.image.load("Assets/SaveIcon.png").convert_alpha(), 0.7)

        # Sets settings as currently inactive (unopen)
        self.settingsActive = False
        # Creates the UI elements displayed on the screen when the settings are open
        self.settingsFrame = Frame(screenDimensions[1]*0.5, 1.5, 5, 20, screenCentre)
        frameDimensions = (self.settingsFrame.rect.width, self.settingsFrame.rect.height)
        frameCentre = (frameDimensions[0]//2, frameDimensions[1]//2)
        self.timeSpeedTitle = Text("Time speed:", 1, int(frameDimensions[1]*0.075), (frameCentre[0], frameDimensions[1]*0.1))
        self.timeSpeedSlider = ValueSlider(frameDimensions[1]*0.05, 20, 4, 10, (frameCentre[0], frameDimensions[1]*0.2), frameDimensions[1]*0.04, [0.1,5], 1, 0.4)
        self.mutationIntensityTitle = Text("Mutation intensity:", 1, int(frameDimensions[1]*0.075), (frameCentre[0], frameDimensions[1]*0.35))
        self.mutationIntensitySlider = ValueSlider(frameDimensions[1]*0.05, 20, 4, 10, (frameCentre[0], frameDimensions[1]*0.45), frameDimensions[1]*0.04, [0.01,0.5], 0.05, 0.4)

        # Sets statistics as currently inactive (unopen)
        self.statisticsActive = False
        # Creates the UI elements displayed on the screen when the statistics are open
        # Retrieves the current statistics stored regarding the population
        values = self.population.retrieve(self.tableId, convertValues = True)
        # Assigns the dependent variablea names and colours
        dependentVariableNames = ["Average speed", "Average sight", "Average temperature control", "Average metabolic rate", "Average age"]
        dependentVariableColours = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255)]
        # Creates the graph to represent the data of the population, plots the initial values of the population
        self.statisticsGraph = LineGraph(screenDimensions[1]*0.75, 2, 10, screenCentre, "Time", dependentVariableNames, dependentVariableColours, 1, values[0], int(screenDimensions[0]*0.005))
        # If there are more values stored regarding the statistics of the population (rather than the initial), plot these too
        for i in range(1,len(values)):
            self.statisticsGraph.plot(values[i])
        
    # Handles interactions between the user and the window and controls the simulation
    def handle(self, mousePosition, events, mouseInputs, keyInputs, deltaTime):
        # Tracks and records user inputs
        lmbPressed = False
        lmbHeld = False
        for event in events:
            # Adjusts camera zoom dependant on scroll wheel inputs
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.camera.zoom(4)
                if event.button == 5:
                    self.camera.zoom(-4)
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    lmbPressed = True
        if mouseInputs[0]:
            lmbHeld = True

        # Moves camera dependant on keys pressed
        keys = pg.key.get_pressed()
        displacement = [0,0]
        if keys[pg.K_w] or keys[pg.K_UP]:
            displacement[1] -= 1
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            displacement[0] -= 1
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            displacement[1] += 1
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            displacement[0] += 1
        self.camera.move(displacement)

        # Handles the back button and records whether it is pressed
        backButtonPressed = self.backButton.handle(mousePosition, lmbPressed)
        # Handles the settings button and determines whether it is pressed
        if self.settingsButton.handle(mousePosition, lmbPressed):
            # If settings button is pressed, the settings are set to active if inactive and vice versa
            self.settingsActive = not self.settingsActive
            # Sets the statistics to inactive regardless of its current state (so that settings and statistics are never concurrently active)
            self.statisticsActive = False
        # Handles the statistics button and determines whether it is pressed
        if self.statisticsButton.handle(mousePosition, lmbPressed):
            # If statistics button is pressed, the statistics are set to active if inactive and vice versa
            self.statisticsActive = not self.statisticsActive
            # Sets the settings to inactive regardless of its current state (so that settings and statistics are never concurrently active)
            self.settingsActive = False
        # Handles the save button and determines whether it is pressed
        if self.saveButton.handle(mousePosition, lmbPressed):
            # Saves the state of the population
            self.population.save(self.tableId)
        
        # If the settings are active (open)
        if self.settingsActive:
            # Handles interactions with the slider relating to the time speed of the simulation and updates the time speed dependent on the value represented by the slider
            self.timeSpeed = self.timeSpeedSlider.handle(mousePosition, lmbHeld, parentRect = self.settingsFrame.rect)
            # Handles interactions with the slider relating to the mutation intenisty of the simulation and updates the mutation intensity dependent on the value represented by the slider
            self.mutationIntensity = self.mutationIntensitySlider.handle(mousePosition, lmbHeld, parentRect = self.settingsFrame.rect)

        # Updates total time (modified by the time speed)
        self.totalTime += deltaTime * self.timeSpeed

        # Handles organism interactions with the environment and other organisms and records the total iterations simulated
        totalIterations = self.population.handle(self.totalTime, self.mutationIntensity)

        # If total iterations has been returned and (total iterations - 1) is a multiple of 300 (1 is used so that the graph will always have atleast 2 points on it - as this comparison will be true after the first iteration)
        if totalIterations and totalIterations % 300 == 1:
            # Rceords the current stats and plots these
            newValues = self.population.record(self.tableId, returnConvertedData = True)
            self.statisticsGraph.plot(newValues)

        # If the back button is pressed, svae the population state and return to the environments menu
        if backButtonPressed:
            self.population.save(self.tableId)
            return "EnvironmentsMenu", [[0,0]]
        # Returns nothing in a manner which can be unpacked - as necessary
        else:
            return None, None
    
    # Displays the simulation window
    def display(self, screen):
        # Uses camera object to display the environment and population
        self.camera.display(screen, self.environment, self.population)
        self.backButton.draw(screen)
        self.settingsButton.draw(screen)
        self.statisticsButton.draw(screen)
        self.saveButton.draw(screen)
        # Displays the settings UI elements, if settings are active
        if self.settingsActive:
            self.settingsFrame.draw(screen)
            self.timeSpeedTitle.draw(self.settingsFrame.surface)
            self.timeSpeedSlider.draw(self.settingsFrame.surface)
            self.mutationIntensityTitle.draw(self.settingsFrame.surface)
            self.mutationIntensitySlider.draw(self.settingsFrame.surface)
        # Displays the statistics UI elements, if statistics are active
        if self.statisticsActive:
            self.statisticsGraph.draw(screen)


