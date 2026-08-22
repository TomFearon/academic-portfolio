# Import necessary modules
import pygame as pg
from WindowsModule import MainMenu, EnvironmentsMenu, EnvironmentConditionsMenu, PopulationConditionsMenu, SimulationWindow

# Initialisies pygame
pg.init()
# Declares 'screen' variable
screen = pg.display.set_mode()
# Determines screen dimensions
screenDimensions = screen.get_size()
# Creates clock object
clock = pg.time.Clock()

# Stores window classes in dictionary, so that they can be referenced
windows = {
    "MainMenu": MainMenu,
    "EnvironmentsMenu": EnvironmentsMenu,
    "EnvironmentConditionsMenu": EnvironmentConditionsMenu,
    "PopulationConditionsMenu": PopulationConditionsMenu,
    "SimulationWindow": SimulationWindow
}

# Sets the initial window as the main menu, providing no window data
currentWindow = windows["MainMenu"](screenDimensions, None)

# Controls the loop of the program
running = True
while running:
    # Gets all events of the iteration
    events = pg.event.get()
    # Iterates through all events
    for event in events:
        # If event is quit, end the loop
        if event.type == pg.QUIT:
            # If current window is the simulation window when program is closed
            if isinstance(currentWindow, SimulationWindow):
                # Emergency autosaves the population being simulated
                currentWindow.population.save(currentWindow.tableId)
            running = False
    
    # Gets all active key inputs (not key events)
    keyInputs = pg.key.get_pressed()

    # Gets the position of the user's mouse
    mousePosition = pg.mouse.get_pos()
    # Gets all active mouse inputs (not mouse events)
    mouseInputs = pg.mouse.get_pressed()

    # Limits fps to 150 and tracks difference in milliseconds since last iteration
    deltaTime = clock.tick(150)

    # Handles the current window, storing the new window for the program to transition to along with the data to provide it with
    newWindow, windowData = currentWindow.handle(mousePosition, events, mouseInputs, keyInputs, deltaTime)
    # If a new window has been given
    if newWindow:
        # Updates the current window and provides this new window its necessary data
        currentWindow = windows[newWindow](screenDimensions, windowData)

    # Displays the current window
    currentWindow.display(screen)

    # Updates the display
    pg.display.flip()

# Quits pygame
pg.quit()

