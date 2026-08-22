# Import necessary modules
import pygame as pg
import math
import time

# Background class
class Background:
    # Creates the background
    def __init__(self):
        # Stores colour of the background
        self.colour = (248,249,250)
    
    # Draws the backrgound
    def draw(self, surface):
        # Fills the screen wth the colour of the background
        surface.fill(self.colour)

# Text class
class Text:
    # Creates the text
    def __init__(self, text, colourIndex, height, centrePosition, title = False):
        # Stores whether text is a title or not
        self.title = title
        # If text is title, set font to title font
        if self.title:
            self.font = pg.font.Font("Assets/Montserrat-Bold.ttf", height)
        # Text is not title, set font to a body font
        else:
            self.font = pg.font.Font("Assets/OpenSans-Regular.ttf", height)

        # Stores array of potential colours of text
        self.colours = [(255,255,255), (33,37,41)]
        
        # Stores text as string
        self.text = text
        # Determines and stores colour of text
        self.colour = self.colours[colourIndex]

        # Stores centre position of text
        self.centrePosition = centrePosition
        # Stores offsetted centre position of text
        self.offsettedPosition = self.centrePosition
        
        # Creates text surface object
        self.textSurface = self.font.render(self.text, True, self.colour)
        # Creates text rect object
        self.textRect = self.textSurface.get_rect(center = self.centrePosition)

    # Function for changing the text displayed in the text surface
    def change_text(self, text):
        # Stores new text string
        self.text = text
        # Updates text surface and text rect objects
        self.textSurface = self.font.render(self.text, True, self.colour)
        self.textRect = self.textSurface.get_rect(center = self.offsettedPosition)
    
    # Function for changing the colour of the text displayed in the text surface
    def change_colour(self, colourIndex):
        # Stores the new colour
        self.colour = self.colours[colourIndex]
        # Updates the text surface object
        self.textSurface = self.font.render(self.text, True, self.colour)

    # Function for changing size of text surface
    def change_size(self, height):
        # Determines font of text and scales it to new size
        if self.title:
            self.font = pg.font.Font("Assets/Montserrat-Bold.ttf", height)
        else:
            self.font = pg.font.Font("Assets/OpenSans-Regular.ttf", height)
        
        # Updates text surface and text rect objects
        self.textSurface = self.font.render(self.text, True, self.colour)
        self.textRect = self.textSurface.get_rect(center = self.offsettedPosition)
    
    # Function for offsetting the text surface
    def offset(self, offsetVector):
        # Calculates new offsetted position
        self.offsettedPosition = (self.centrePosition[0] + offsetVector[0], self.centrePosition[1] + offsetVector[1])
        # Updates the text rect object
        self.textRect = self.textSurface.get_rect(center = self.offsettedPosition)

    # Function for drawing text onto screen
    def draw(self, surface):
        # Draws text surface using text rect
        surface.blit(self.textSurface, self.textRect)

# Text button class
class TextButton:
    # Creates the text button
    def __init__(self, height, aspectRatio, borderWidth, cornerRadius, centrePosition, text, textColourIndex, textRatio, activatedRatio = 1.025, pressCooldown = 0.1, title = False):
        # Stores the active and passive colour of the button
        self.passiveButtonColour = (67,97,238)
        self.activeButtonColour = (76,201,240)

        # Stores variable to indicate whether button is active (being hovered over by user), which is set to false
        self.active = False
        # Sets current colour of button
        self.buttonColour = self.passiveButtonColour

        # Sets colour of the border of the button
        self.borderColour = (43,45,66)

        # Stores height of button
        self.buttonHeight = height
        # Calculates width of button using aspect ratio and stores the width
        self.buttonWidth = self.buttonHeight*aspectRatio

        # Calculates and stores border width
        self.borderWidth = self.buttonWidth + borderWidth
        # Calculates and stores border height
        self.borderHeight = self.buttonHeight + borderWidth

        # Stores corner radius
        self.cornerRadius = cornerRadius

        # Stores centre psoition of the button
        self.centrePosition = centrePosition
        # Stores offsetted position
        self.offsettedPosition = self.centrePosition

        # Creates rect object for the border
        self.borderRect = pg.Rect(0, 0, self.borderWidth, self.borderHeight)
        # Centres the border
        self.borderRect.center = self.centrePosition
        # Creates rect object for the button
        self.buttonRect = pg.Rect(0, 0, self.buttonWidth, self.buttonHeight)
        # Centres the button
        self.buttonRect.center = self.offsettedPosition

        # Stores the ratio of the size of the button when activated
        self.activatedRatio = activatedRatio

        # Stores the text size ratio
        self.textRatio = textRatio
        # Creates the text object
        self.textObject = Text(text, textColourIndex, int(self.textRatio*self.buttonHeight), self.centrePosition, title = title)

        # Store boolean variable to indicate whether button is being pressed
        self.pressed = False
        # Stores click cooldown (min delay between button pressed)
        self.pressCooldown = pressCooldown
        # Stores time since last press
        self.sincePress = 0
    
    # Function for activating button
    def activate(self):
        # Set button as active
        self.active = True
        # Changes current button colour
        self.buttonColour = self.activeButtonColour
        # Increases size of button, border and text and positions them
        self.borderRect = pg.Rect(0, 0, self.borderWidth*self.activatedRatio, self.borderHeight*self.activatedRatio)
        self.borderRect.center = self.offsettedPosition
        self.buttonRect = pg.Rect(0, 0, self.buttonWidth*self.activatedRatio, self.buttonHeight*self.activatedRatio)
        self.buttonRect.center = self.offsettedPosition
        self.textObject.change_size(int(self.textRatio*self.buttonHeight*self.activatedRatio))
        
    # Function for deactivating button
    def deactivate(self):
        # Set as not active
        self.active = False
        # Adjusts current button colour
        self.buttonColour = self.passiveButtonColour
        # Decreases size of button, border and text and positions them
        self.borderRect = pg.Rect(0, 0, self.borderWidth, self.borderHeight)
        self.borderRect.center = self.offsettedPosition
        self.buttonRect = pg.Rect(0, 0, self.buttonWidth, self.buttonHeight)
        self.buttonRect.center = self.offsettedPosition
        self.textObject.change_size(int(self.textRatio*self.buttonHeight))
    
    # Handles the user interactions with the button
    def handle(self, mousePosition, press, parentRect = None):
        # Determines local position of mouse
        if parentRect:
            localMousePosition = (mousePosition[0] - parentRect.topleft[0], mousePosition[1] - parentRect.topleft[1])
        else:
            localMousePosition = mousePosition
        # If the user is hovering over the button and mouse is inside parent rect
        if self.buttonRect.collidepoint(localMousePosition) and (not parentRect or parentRect.collidepoint(mousePosition)):
            # If button not currently active and press cooldown  has passed
            if not self.active and (time.time() - self.sincePress) >= self.pressCooldown:
                # Activate button
                self.activate()
            # If button is pressed and press delay has passed
            if press and (time.time() - self.sincePress) >= self.pressCooldown:
                # Indicates that button is being pressed
                self.pressed = True
                # Records time since last press
                self.sincePress = time.time()
                # Deactivates button, indicating that is has been pressed
                self.deactivate()
            # If button is not pressed
            else:
                # Indicates that button is not being pressed
                self.pressed = False
        # If user is not hovering over the button
        else:
            # If button is currently active
            if self.active:
                # Deactivate button
                self.deactivate()
            # Indicates that button is not being pressed
            self.pressed = False
        
        # Returns value indicating whether button has been pressed or not
        return self.pressed

    # Function used for offsetting the text button
    def offset(self, offsetVector):
        # Calculates new offsetted position
        self.offsettedPosition = (self.centrePosition[0] + offsetVector[0], self.centrePosition[1] + offsetVector[1])
        self.borderRect.center = self.offsettedPosition
        self.buttonRect.center = self.offsettedPosition
        self.textObject.offset(offsetVector)

    # Function for drawing the text button
    def draw(self, surface):
        # Draws the border
        pg.draw.rect(surface, self.borderColour, self.borderRect, border_radius = self.cornerRadius)
        # Draws the button
        pg.draw.rect(surface, self.buttonColour, self.buttonRect, border_radius = self.cornerRadius)
        # Draws the text
        self.textObject.draw(surface)

# Function to determine whether point (like mouse position) collides with a circle
def circle_collide_point(centre, radius, point):
    # Distance from centre to point
    distance = math.sqrt((point[0] - centre[0])**2 + (point[1] - centre[1])**2)
    # Returns true if distance is less than or equal to the radius of the circle, if not, returns false
    return distance <= radius

# Image button class
class ImageButton:
    # Creates the image button
    def __init__(self, radius, borderWidth, centrePosition, image, imageRatio, activatedRatio = 1.05, pressCooldown = 0.1):
        # Stores the active and passive colour of the button
        self.passiveButtonColour = (67,97,238)
        self.activeButtonColour = (76,201,240)

        # Stores variable to indicate whether button is active (being hovered over by user), which is set to false
        self.active = False
        # Sets current colour of button
        self.buttonColour = self.passiveButtonColour

        # Sets colour of the border of the button
        self.borderColour = (43,45,66)

        # Stores centre psoition of the button
        self.centrePosition = centrePosition
        # Stores offsetted position of the button
        self.offsettedPosition = self.centrePosition

        # Stores the ratio of the size of the button when activated
        self.activatedRatio = activatedRatio

        # Stores radius of button
        self.buttonRadius = radius
        # Sets the current radius of button
        self.currentButtonRadius = self.buttonRadius

        # Calculates and stores radius of border
        self.borderRadius = radius + borderWidth
        # Sets the current radius of the border
        self.currentBorderRadius = self.borderRadius

        # Stores activated ratio
        self.activatedRatio = activatedRatio

        # Stores the unscaled image
        self.unscaledImage = image
        # Stores the image ratio
        self.imageRatio = imageRatio
        # Stores the scaled image
        self.scaledImage = pg.transform.smoothscale(self.unscaledImage, (self.currentButtonRadius*2*self.imageRatio, self.currentButtonRadius*2*self.imageRatio))
        # Creates the image rect object
        self.imageRect = self.scaledImage.get_rect(center = self.offsettedPosition)

        # Store boolean variable to indicate whether button is being pressed
        self.pressed = False
        # Stores click cooldown (min delay between button pressed)
        self.pressCooldown = pressCooldown
        # Stores time since last press
        self.sincePress = 0
    
    # Function for activating the button
    def activate(self):
        # Set button as active
        self.active = True
        # Changes current button colour
        self.buttonColour = self.activeButtonColour
        # Increases size of button, border and image
        self.currentButtonRadius = self.buttonRadius*self.activatedRatio
        self.currentBorderRadius = self.borderRadius*self.activatedRatio
        self.scaledImage = pg.transform.smoothscale(self.unscaledImage, (self.currentButtonRadius*2*self.imageRatio, self.currentButtonRadius*2*self.imageRatio))
        # Recreates the image rect object
        self.imageRect = self.scaledImage.get_rect(center = self.offsettedPosition)
    
    # Function for deactivatin the btton
    def deactivate(self):
        # Set button as inactive
        self.active = False
        # Changes current button colour
        self.buttonColour = self.passiveButtonColour
        # Increases size of button, border and image
        self.currentButtonRadius = self.buttonRadius
        self.currentBorderRadius = self.borderRadius
        self.scaledImage = pg.transform.smoothscale(self.unscaledImage, (self.currentButtonRadius*2*self.imageRatio, self.currentButtonRadius*2*self.imageRatio))
        # Recreates the image rect object
        self.imageRect = self.scaledImage.get_rect(center = self.offsettedPosition)
    
    # Handles interactions with the button
    def handle(self, mousePosition, press, parentRect = None):
        # Determines local position of mouse
        if parentRect:
            localMousePosition = (mousePosition[0] - parentRect.topleft[0], mousePosition[1] - parentRect.topleft[1])
        else:
            localMousePosition = mousePosition
        # If the user is hovering over the button and mouse is inside parent rect
        if circle_collide_point(self.offsettedPosition, self.buttonRadius, localMousePosition) and (not parentRect or parentRect.collidepoint(mousePosition)):
            # If button not currently active and press delay has passed
            if not self.active and (time.time() - self.sincePress) >= self.pressCooldown:
                # Activate button
                self.activate()
            # If button is pressed and press delay has passed
            if press and (time.time() - self.sincePress) >= self.pressCooldown:
                # Indicates that button is being pressed
                self.pressed = True
                # Records time since last press
                self.sincePress = time.time()
                # Deactivates the button, indicating that it has been pressed
                self.deactivate()
            # If button is not pressed
            else:
                # Indicates that button is not being pressed
                self.pressed = False
        # If user is not hovering over the button
        else:
            # If button is currently active
            if self.active:
                # Deactivate button
                self.deactivate()
            # Indicates that button is not being pressed
            self.pressed = False

        # Returns value indicating whether button has been pressed or not
        return self.pressed
    
    # Function for offsetting image button
    def offset(self, offsetVector):
        # Calculates offsetted position
        self.offsettedPosition = (self.centrePosition[0] + offsetVector[0], self.centrePosition[1] + offsetVector[1])
        # Positions image
        self.imageRect.center = self.offsettedPosition

    # Function for drawing the image button
    def draw(self, surface):
        # Draws the border
        pg.draw.circle(surface, self.borderColour, self.offsettedPosition, self.currentBorderRadius)
        # Draws the button
        pg.draw.circle(surface, self.buttonColour, self.offsettedPosition, self.currentButtonRadius)
        # Draws the image
        surface.blit(self.scaledImage, self.imageRect)

characterSets = {"Alpha": list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"),
                "Alphanumeric": list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"),
                "Numeric": list("0123456789"),
                "SignedNumeric": list("012345678-"),
                "Decimal": list("123456789."),
                "SignedDecimal": list("123456789.-")}

# Input box class
class InputBox:
    # Creates the text box
    def __init__(self, height, aspectRatio, borderWidth, cornerRadius, centrePosition, textRatio, pressCooldown = 0.1, placeholderText = "", allowedCharacters = "Alphanumeric"):
        # Sets colour of box
        self.boxColour = (255,255,255)

        # Stores active border colour
        self.activeBorderColour = (120, 125, 130)
        # Stores passive border colour
        self.passiveBorderColour = (33,37,41)

        # Stores varaible indicating whether box is active or not
        self.active = False
        # Sets current border colour
        self.borderColour = self.passiveBorderColour

        # Stored box height
        self.boxHeight = height
        # Calculates box width using aspect ratio
        self.boxWidth = self.boxHeight*aspectRatio

        # Calculates and stores border width
        self.borderWidth = self.boxWidth + borderWidth
        # Calculates and stores border height
        self.borderHeight = self.boxHeight + borderWidth

        # Stores corner radius
        self.cornerRadius = cornerRadius

        # Stores centre psoition of the box
        self.centrePosition = centrePosition
        # Stores offsetted position of the box
        self.offsettedPosition = self.centrePosition

        # Creates rect object for the border
        self.borderRect = pg.Rect(0, 0, self.borderWidth, self.borderHeight)
        # Centres the border
        self.borderRect.center = self.offsettedPosition
        # Creates rect object for the box
        self.boxRect = pg.Rect(0, 0, self.boxWidth, self.boxHeight)
        # Centres the box
        self.boxRect.center = self.offsettedPosition

        # Stores the text size ratio
        self.textRatio = textRatio
        # Stores the placeholder text
        self.placeholderText = placeholderText
        # Stores input text
        self.inputText = ""
        # Stores allowed characters
        self.allowedCharacters = characterSets[allowedCharacters]
        # Creates the text object
        self.textObject = Text(self.placeholderText, 1, int(self.textRatio*self.boxHeight), self.offsettedPosition)
        
        # Stores click cooldown (min delay between button pressed)
        self.pressCooldown = pressCooldown
        # Stores time since last press
        self.sincePress = 0
    
    # Function for activating the input box
    def activate(self):
        # Sets box is active
        self.active = True
        # Changes text displayed in the box
        self.textObject.change_text(self.inputText)
        # Adjusts the border colour
        self.borderColour = self.activeBorderColour
    
    # Function for deactivating the text box
    def deactivate(self):
        # Sets box as inactive
        self.active = False
        # If there is no input text
        if self.inputText == "":
            # Changes text displayed to placeholder text
            self.textObject.change_text(self.placeholderText)
        # Adjusts the border colour
        self.borderColour = self.passiveBorderColour
    
    # Function for handling interactions with the input box
    def handle(self, mousePosition, press, keyInput, parentRect = None):
        # Determines local position of mouse
        if parentRect:
            localMousePosition = (mousePosition[0] - parentRect.topleft[0], mousePosition[1] - parentRect.topleft[1])
        else:
            localMousePosition = mousePosition
        # If the mouse is touching the box
        if self.boxRect.collidepoint(localMousePosition) and (not parentRect or parentRect.collidepoint(mousePosition)):
            # If box is being pressed and press cooldown has passed
            if press and (time.time() - self.sincePress) >= self.pressCooldown:
                # Records time since last press
                self.sincePress = time.time()
                # If active, deactivates
                if self.active:
                    self.deactivate()
                # If not active, activates
                else:
                    self.activate()
        # If mouse pressed but mouse not touching the box
        elif press:
            # If box is active, deactivates
            if self.active:
                    self.deactivate()

        # If box is active
        if self.active:
            # If a key input has been passed
            if keyInput:
                # If the key input is backspace
                if keyInput.key == pg.K_BACKSPACE:
                    # Remove end letter of input text
                    self.inputText = self.inputText[:-1]
                    # Updates text object with backspace
                    self.textObject.change_text(self.inputText)
                # If key input is enter
                elif keyInput.key == pg.K_RETURN:
                    # Deactiavtes box
                    self.deactivate()
                # If key input is another key
                else:
                    # If key input is within allowed characters, add to input text
                    for character in self.allowedCharacters:
                        if keyInput.unicode == character:
                            self.inputText += keyInput.unicode
                            break

                    # Updates text object with new input text
                    self.textObject.change_text(self.inputText)

        # Returns current input text in box, if box is not active and input text has been entered
        if not self.active and len(self.inputText) != 0:
            return self.inputText

    # Function for offsetting the input box
    def offset(self, offsetVector):
        # Calculates offsetted position
        self.offsettedPosition = (self.centrePosition[0] + offsetVector[0], self.centrePosition[1] + offsetVector[1])
        # Positions box and border
        self.boxRect.center = self.offsettedPosition
        self.borderRect.center = self.offsettedPosition
        # Offsets the text object
        self.textObject.offset(offsetVector)

    # Function for drawing the input box    
    def draw(self, surface):
        # Draws the border
        pg.draw.rect(surface, self.borderColour, self.borderRect, border_radius = self.cornerRadius)
        # Draws the box
        pg.draw.rect(surface, self.boxColour, self.boxRect, border_radius = self.cornerRadius)
        # Draws the text
        self.textObject.draw(surface)

# Value slider class
class ValueSlider:
    # Creates value slider
    def __init__(self, height, aspectRatio, borderWidth, cornerRadius, centrePosition, handleRadius, valueRange, initialValue, textRatio):
        # Stores bar colour
        self.barColour = (255,255,255)
        # Stores bar border colour
        self.barBorderColour = (33,37,41)

        # Stores colour of handle when passive
        self.handlePassiveColour = (67,97,238)
        # Stores colour of handle when active
        self.handleActiveColour = (76,201,240)
        # Stores colour of handle
        self.handleBorderColour = (43,45,66)

        # Stores variable indicating whether handle is active or not
        self.handleActive = False
        # Sets handle colour
        self.handleColour = self.handlePassiveColour

        # Stores bar height
        self.barHeight = height
        # Calculates bar width using aspect ratio
        self.barWidth = self.barHeight*aspectRatio

        # Calculates and stores bar border height
        self.barBorderHeight = self.barHeight + borderWidth
        # Calculates and stores bar border width 
        self.barBorderWidth = self.barWidth + borderWidth

        # Stores corner radius
        self.cornerRadius = cornerRadius

        # Stores centre position
        self.centrePosition = centrePosition
        # Stores offsetted position of the slider
        self.offsettedPosition = self.centrePosition

        # Stores value range
        self.valueRange = valueRange

        # Stores handle radius
        self.handleRadius = handleRadius
        # Calculates and stores the handle border radius
        self.handleBorderRadius = handleRadius + borderWidth//(3/2)

        # Creates bar rect object
        self.barRect = pg.Rect(0, 0, self.barWidth, self.barHeight)
        # Centres the bar
        self.barRect.center = self.offsettedPosition
        # Creates bar border rect object
        self.barBorderRect = pg.Rect(0, 0, self.barBorderWidth, self.barBorderHeight)
        # Centres the bar border
        self.barBorderRect.center = self.offsettedPosition

        # Stores current value determined by handle
        self.currentValue = initialValue

        # Calculates minimum handle centre position
        self.minHandleCentreX = self.offsettedPosition[0] - (self.barWidth//2)
        # Calculates maximum handle centre position
        self.maxHandleCentreX = self.offsettedPosition[0] + (self.barWidth//2)

        # Stores position of the handle
        self.handleCentrePosition = [self.minHandleCentreX + self.barWidth * (self.currentValue - self.valueRange[0])/(self.valueRange[1] - self.valueRange[0]), self.offsettedPosition[1]]
        # Stores offsetted positon of the centre of the handle
        self.handleOffsettedPosition = self.handleCentrePosition

        # Stores the text ratio
        self.textRatio = textRatio
        # Creates text object ot represent current value of handle
        self.currentValueTextObject = Text(str(round(self.currentValue,2)), 0, int(self.barHeight*self.textRatio), self.handleOffsettedPosition)

    # Moves handle and adjusts current value accordingly
    def move_handle(self, newX):
        # Moves handle position, clamping it between its minimum and maximum
        self.handleOffsettedPosition[0] = max(self.minHandleCentreX,min(newX, self.maxHandleCentreX))
        # Calculates the current value dependent on where the handle is
        self.currentValue = (self.valueRange[1] - self.valueRange[0]) * ((self.handleOffsettedPosition[0]-self.minHandleCentreX)/(self.maxHandleCentreX-self.minHandleCentreX)) + self.valueRange[0]
        # Changes the text of the current value text object and offsets it
        self.currentValueTextObject.change_text(str(round(self.currentValue,2)))
        self.currentValueTextObject.offset((self.handleOffsettedPosition[0] - self.handleCentrePosition[0], self.handleOffsettedPosition[1] - self.handleCentrePosition[1]))

    # Function to activate the handle
    def activate(self):
        # Sets handle to active
        self.handleActive = True
        # Adjusts handle colour
        self.handleColour = self.handleActiveColour

    # Function to deactivate the handle
    def deactivate(self):
        # Sets handle to inactive
        self.handleActive = False
        # Adjusts handle colour
        self.handleColour = self.handlePassiveColour
    
    # Handles interactions with the handle
    def handle(self, mousePosition, held, parentRect = None):
        # Determines local position of mouse
        if parentRect:
            localMousePosition = (mousePosition[0] - parentRect.topleft[0], mousePosition[1] - parentRect.topleft[1])
        else:
            localMousePosition = mousePosition
        # If the mouse collides with the handle
        if circle_collide_point(self.handleOffsettedPosition, self.handleRadius, localMousePosition) and (not parentRect or parentRect.collidepoint(mousePosition)):
            # If the handle is being held
            if held:
                # If handle is not active, activate it
                if not self.handleActive:
                    self.activate()
                # Moves handle according to x position of mouse
                self.move_handle(localMousePosition[0])
            # If not held
            else:
                # If the handle is active, deactivate it
                if self.handleActive:
                    self.deactivate()
        
        # If mouse is held and handle is active (but mouse not colliding with handle)
        elif held and self.handleActive:
            # Moves handle according to x position of mouse
            self.move_handle(localMousePosition[0])
        # If mouse is not held and/or handle is inactive
        else:
            # If handle is active, deactivate it 
            if self.handleActive:
                self.deactivate()

        # Returns the current value represented by the handle
        return self.currentValue
        
    # Function for offsetting the slider
    def offset(self, offsetVector):
        # Calculates offsetted position
        self.offsettedPosition = (self.centrePosition[0] + offsetVector[0], self.centrePosition[1] + offsetVector[1])
        # Calculates minimum handle centre position
        self.minHandleCentreX = self.offsettedPosition[0] - (self.barWidth//2)
        # Calculates maximum handle centre position
        self.maxHandleCentreX = self.offsettedPosition[0] + (self.barWidth//2)
        # Positions the handle, bar, bar border and text object
        self.handleOffsettedPosition = [self.minHandleCentreX + self.barWidth * (self.currentValue - self.valueRange[0])/(self.valueRange[1] - self.valueRange[0]), self.offsettedPosition[1]]
        self.currentValueTextObject.offset((self.handleOffsettedPosition[0] - self.handleCentrePosition[0], offsetVector[1]))
        self.barRect.center = self.offsettedPosition
        self.barBorderRect.center = self.offsettedPosition

    # Draws the value slider
    def draw(self, surface):
        # Draws the bar border
        pg.draw.rect(surface, self.barBorderColour, self.barBorderRect, border_radius = self.cornerRadius)
        # Draws the bar
        pg.draw.rect(surface, self.barColour, self.barRect, border_radius = self.cornerRadius)
        # Draws the handle border
        pg.draw.circle(surface, self.handleBorderColour, self.handleOffsettedPosition, self.handleBorderRadius)
        # Draws the handle
        pg.draw.circle(surface, self.handleColour, self.handleOffsettedPosition, self.handleRadius)
        # Draws the current value text object
        self.currentValueTextObject.draw(surface)

# Range slider class
class RangeSlider:
    # Creates the range slider
    def __init__(self, height, aspectRatio, borderWidth, cornerRadius, centrePosition, handleRadius, valueRange, initialValues, textRatio):
        # Stores bar colour
        self.barColour = (255,255,255)
        # Stores bar border colour
        self.barBorderColour = (33,37,41)

        # Stores colour of handle when passive
        self.handlePassiveColour = (67,97,238)
        # Stores colour of handle when active
        self.handleActiveColour = (76,201,240)
        # Stores colour of handle border
        self.handleBorderColour = (43,45,66)

        # List indicating whether handles are active or 
        self.handlesActive = [False, False]
        # Sets handle colours and stores as list
        self.handlesColour = [self.handlePassiveColour, self.handlePassiveColour]

        # Stores bar height
        self.barHeight = height
        # Calculates bar width using aspect ratio
        self.barWidth = self.barHeight*aspectRatio

        # Calculates and stores bar border height
        self.barBorderHeight = self.barHeight + borderWidth
        # Calculates and stores bar border width 
        self.barBorderWidth = self.barWidth + borderWidth

        # Stores corner radius
        self.cornerRadius = cornerRadius

        # Stores centre position
        self.centrePosition = centrePosition
        # Stores offsetted position of the slider
        self.offsettedPosition = self.centrePosition

        # Stores value range
        self.valueRange = valueRange

        # Stores handle radius
        self.handleRadius = handleRadius
        # Calculates and stores the handle border radius
        self.handleBorderRadius = handleRadius + borderWidth//(3/2)

        # Creates bar rect object
        self.barRect = pg.Rect(0, 0, self.barWidth, self.barHeight)
        # Centres the bar
        self.barRect.center = self.centrePosition
        # Creates bar border rect object
        self.barBorderRect = pg.Rect(0, 0, self.barBorderWidth, self.barBorderHeight)
        # Centres the bar border
        self.barBorderRect.center = self.centrePosition

        # Stores current values determined by the handles
        self.currentValues = initialValues

        # Calculates minimum handle centre position
        self.minHandleCentreX = self.centrePosition[0] - (self.barWidth//2)
        # Calculates maximum handle centre position
        self.maxHandleCentreX = self.centrePosition[0] + (self.barWidth//2)

        # Stores position of the handles in a list
        self.handlesCentrePosition = [[self.minHandleCentreX + self.barWidth * (self.currentValues[0] - valueRange[0])/(valueRange[1] - valueRange[0]), self.centrePosition[1]]]
        self.handlesCentrePosition.append([self.minHandleCentreX + self.barWidth * (self.currentValues[1] - valueRange[0])/(valueRange[1] - valueRange[0]), self.centrePosition[1]])
        # Stores offsetted positions of handles in a list
        self.handlesOffsettedPosition = self.handlesCentrePosition.copy()

        # Stores the text ratio
        self.textRatio = textRatio
        # Creates text objects to represent value of handles and stores them in a list
        self.currentValueTextObjects = [Text(str(round(self.currentValues[0],2)), 0, int(self.barHeight*self.textRatio), self.handlesOffsettedPosition[0])]
        self.currentValueTextObjects.append(Text(str(round(self.currentValues[1],2)), 0, int(self.barHeight*self.textRatio), self.handlesOffsettedPosition[1]))

    # Moves handle and adjusts current value accordingly
    def move_handle(self, i, newX):
        # Moves handle position, clamping it between its minimum and maximum
        self.handlesOffsettedPosition[i][0] = max(self.minHandleCentreX,min(newX, self.maxHandleCentreX))
        # Calculates the current value dependent on where the handle is
        self.currentValues[i] = (self.valueRange[1] - self.valueRange[0]) * ((self.handlesOffsettedPosition[i][0]-self.minHandleCentreX)/(self.maxHandleCentreX-self.minHandleCentreX))
        # Changes text of current valu text object and positions it
        self.currentValueTextObjects[i].change_text(str(round(self.currentValues[i], 2)))
        self.currentValueTextObjects[i].offset((self.handlesOffsettedPosition[i][0] - self.handlesCentrePosition[i][0], self.handlesOffsettedPosition[i][1] - self.handlesCentrePosition[i][1]))

    # Function to activate the handle
    def activate(self, i):
        # Sets handle to active
        self.handlesActive[i] = True
        # Adjusts handle colour
        self.handlesColour[i] = self.handleActiveColour

    # Function to deactivate the handle
    def deactivate(self, i):
        # Sets handle to inactive
        self.handlesActive[i] = False
        # Adjusts handle colour
        self.handlesColour[i] = self.handlePassiveColour
    
    # Handles interactions with the slider
    def handle(self, mousePosition, held, parentRect = None):
        # Determines local position of mouse
        if parentRect:
            localMousePosition = (mousePosition[0] - parentRect.topleft[0], mousePosition[1] - parentRect.topleft[1])
        else:
            localMousePosition = mousePosition
        # Iterates through the two handles
        for i in [0,1]:
            # If the mouse collides with the handle
            if circle_collide_point(self.handlesOffsettedPosition[i], self.handleRadius, localMousePosition) and (not parentRect or parentRect.collidepoint(mousePosition)):
                # If the handle is being held
                if held:
                    # If no handles are active, activate it
                    if not any(self.handlesActive):
                        self.activate(i)
                    # Moves handle according to x position of mouse
                    if self.handlesActive[i]:
                        self.move_handle(i, localMousePosition[0])
                # If not held
                else:
                    # If the handle is active, deactivate it
                    if self.handlesActive[i]:
                        self.deactivate(i)
        
            # If mouse is held and handle is active (but mouse not colliding with handle)
            elif held and self.handlesActive[i]:
                # Moves handle according to x position of mouse
                self.move_handle(i, localMousePosition[0])
            # If mouse is not held and/or handle is inactive
            else:
                # If handle is active, deactivate it 
                if self.handlesActive[i]:
                    self.deactivate(i)

        # Returns the current values represented by the handles in numerically ascending order
        return [min(self.currentValues), max(self.currentValues)]
        
    # Function for offsetting the slider
    def offset(self, offsetVector):
        # Calculates offsetted position
        self.offsettedPosition = (self.centrePosition[0] + offsetVector[0], self.centrePosition[1] + offsetVector[1])
        # Calculates minimum handle centre position
        self.minHandleCentreX = self.offsettedPosition[0] - (self.barWidth//2)
        # Calculates maximum handle centre position
        self.maxHandleCentreX = self.offsettedPosition[0] + (self.barWidth//2)
        # Positions each handle and tehir respective text objects
        for i in [0,1]:
            self.handlesOffsettedPosition[i] = [self.minHandleCentreX + self.barWidth * (self.currentValues[i] - self.valueRange[0])/(self.valueRange[1] - self.valueRange[0]), self.offsettedPosition[1]]
            self.currentValueTextObjects[i].offset((self.handlesOffsettedPosition[i][0] - self.handlesCentrePosition[i][0], offsetVector[1]))
        # Positions the bar and the bar border
        self.barRect.center = self.offsettedPosition
        self.barBorderRect.center = self.offsettedPosition

    # Draws the range slider
    def draw(self, surface):
        # Draws the bar border
        pg.draw.rect(surface, self.barBorderColour, self.barBorderRect, border_radius = self.cornerRadius)
        # Draws the bar
        pg.draw.rect(surface, self.barColour, self.barRect, border_radius = self.cornerRadius)
        # Iterates through the two handles
        for i in [1,0]:
            # Draws the handle border
            pg.draw.circle(surface, self.handleBorderColour, self.handlesOffsettedPosition[i], self.handleBorderRadius)
            # Draws the handle
            pg.draw.circle(surface, self.handlesColour[i], self.handlesOffsettedPosition[i], self.handleRadius)
            # Draws the current value text object
            self.currentValueTextObjects[i].draw(surface)

# Scroll bar class
class ScrollBar:
    # Creates the scroll bar
    def __init__(self, height, aspectRatio, borderWidth, cornerRadius, centrePosition, handleHeightRatio):
        # Stores bar colour
        self.barColour = (255,255,255)
        # Stores bar border colour
        self.barBorderColour = (33,37,41)

        # Stores passive colour of handle
        self.handlePassiveColour = (200, 205, 210)
        # Stores active colour of handle
        self.handleActiveColour = (180, 185, 190)
        # Stores handle border colour
        self.handleBorderColour = (70, 75, 80)

        # Stores variable indicating whether handle is active or not
        self.handleActive = False
        # Sets handle colour
        self.handleColour = self.handlePassiveColour

        # Stores height of the scroll bar
        self.barHeight = height
        # Calculates and stores width of the scroll bar
        self.barWidth = height*aspectRatio

        # Calculates and stores bar border height
        self.barBorderHeight = self.barHeight + borderWidth
        # Calculates and stores bar border width 
        self.barBorderWidth = self.barWidth + borderWidth

        # Stores corner radius
        self.cornerRadius = cornerRadius

        # Stores centre position
        self.centrePosition = centrePosition

        # Calculates and stores handle height
        self.handleHeight = self.barHeight*handleHeightRatio
        # Stores handle width 
        self.handleWidth = self.barWidth

        # Calculates and stores handle border height
        self.handleBorderHeight = self.handleHeight + borderWidth
        # Stores handle border width
        self.handleBorderWidth = self.barBorderWidth

        # Creates the bar rect object
        self.barRect = pg.Rect(0, 0, self.barWidth, self.barHeight)
        # Centres the bar
        self.barRect.center = self.centrePosition
        # Creates the bar border rect object
        self.barBorderRect = pg.Rect(0, 0, self.barBorderWidth, self.barBorderHeight)
        # Centres the bar border
        self.barBorderRect.center = self.centrePosition

        # Stores the scroll progress of the bar
        self.scrollProgress = 0 

        # Calculates and stores min and max centre y position of the handle
        self.minHandleCentreY = (self.centrePosition[1] - self.barHeight//2) + self.handleHeight//2
        self.maxHandleCentreY = (self.centrePosition[1] + self.barHeight//2) - self.handleHeight//2

        # Stores the current handle centre position
        self.handleCentrePosition = [self.centrePosition[0], self.minHandleCentreY]

        # Creates the handle rect object
        self.handleRect = pg.Rect(0, 0, self.handleWidth, self.handleHeight)
        # Positions the handle
        self.handleRect.center = self.handleCentrePosition
        # Creates the handle border rect object
        self.handleBorderRect = pg.Rect(0, 0, self.handleBorderWidth, self.handleBorderHeight)
        # Positions the handle border
        self.handleBorderRect.center = self.handleCentrePosition

    # Moves handle and adjusts scroll progress accordingly
    def move_handle(self, newY):
        # Moves handle y position, clamping it between its minimum and maximum
        self.handleCentrePosition[1] = max(self.minHandleCentreY,min(newY, self.maxHandleCentreY))
        # Postions the handle and the handle border
        self.handleRect.center = self.handleCentrePosition
        self.handleBorderRect.center = self.handleCentrePosition
        # Calculates the scroll progress dependent on where the handle is
        self.scrollProgress = ((self.handleCentrePosition[1]-self.minHandleCentreY)/(self.maxHandleCentreY-self.minHandleCentreY))

    # Function to activate the handle
    def activate(self):
        # Sets handle to active
        self.handleActive = True
        # Adjusts handle colour
        self.handleColour = self.handleActiveColour
    
    # Function to deactivate the handle
    def deactivate(self):
        # Sets handle to inactive
        self.handleActive = False
        # Adjusts handle colour
        self.handleColour = self.handlePassiveColour

    # Handles interactions with the handle
    def handle(self, mousePosition, held, parentRect = None):
        # Determines local position of mouse
        if parentRect:
            localMousePosition = (mousePosition[0] - parentRect.topleft[0], mousePosition[1] - parentRect.topleft[1])
        else:
            localMousePosition = mousePosition
        # If the mouse collides with the handle
        if self.handleRect.collidepoint(localMousePosition) and (not parentRect or parentRect.collidepoint(mousePosition)):
            # If the handle is being held
            if held:
                # If handle is not active, activate it
                if not self.handleActive:
                    self.activate()
                # Moves handle according to x position of mouse
                self.move_handle(localMousePosition[1])
            # If not held
            else:
                # If the handle is active, deactivate it
                if self.handleActive:
                    self.deactivate()
        
        # If mouse is held and handle is active (but mouse not colliding with handle)
        elif held and self.handleActive:
            # Moves handle according to x position of mouse
            self.move_handle(localMousePosition[1])
        # If mouse is not held and/or handle is inactive
        else:
            # If handle is active, deactivate it 
            if self.handleActive:
                self.deactivate()

        # Returns the current value represented by the handle
        return self.scrollProgress

    # Draws the scroll bar
    def draw(self, surface):
        # Draws the bar border
        pg.draw.rect(surface, self.barBorderColour, self.barBorderRect, border_radius = self.cornerRadius)
        # Draws the bar
        pg.draw.rect(surface, self.barColour, self.barRect, border_radius = self.cornerRadius)
        # Draws the handle border
        pg.draw.rect(surface, self.handleBorderColour, self.handleBorderRect, border_radius = self.cornerRadius)
        # Draws the handle
        pg.draw.rect(surface, self.handleColour, self.handleRect, border_radius = self.cornerRadius)

# Frame class
class Frame:
    # Creates the frame
    def __init__(self, height, aspectRatio, borderWidth, cornerRadius, centrePosition):
        # Stores the colour of the frame
        self.frameColour = (76,201,240)
        
        # Stores the colour of the border
        self.borderColour = (43,45,66)

        # Stores the height of the frame
        self.height = height
        # Calculates and stores the width of the frame
        self.width = height *aspectRatio

        # Calculates and stores the border height
        self.borderHeight = self.height + borderWidth
        # Calculates and stores the border width
        self.borderWidth = self.width + borderWidth

        # Stores the corner radius
        self.cornerRadius = cornerRadius

        # Stores the centre position of the frame
        self.centrePosition = centrePosition
        # Stores offsetted position of the frame
        self.offsettedPosition = self.centrePosition

        # Creates frame rect object
        self.rect = pg.Rect(0, 0, self.width, self.height)
        # Centres the frame rect
        self.rect.center = self.offsettedPosition
        # Creates the transparent frame surface object
        self.surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
        # Creates border rect object
        self.borderRect = pg.Rect(0, 0, self.borderWidth, self.borderHeight)
        # Centres the border rect
        self.borderRect.center = self.offsettedPosition

    # Function used for offsetting the frame
    def offset(self, offsetVector):
        # Calculates new offsetted position
        self.offsettedPosition = (self.centrePosition[0] + offsetVector[0], self.centrePosition[1] + offsetVector[1])
        # Adjusts frame's position accordingly
        self.borderRect.center = self.offsettedPosition
        self.rect.center = self.offsettedPosition

    # Function to draw the frame
    def draw(self, surface):
        # Draws the border rect
        pg.draw.rect(surface, self.borderColour, self.borderRect, border_radius = self.cornerRadius)
        # Draws the surface
        surface.blit(self.surface, self.rect)
        # Draws the frame rect locally onto the surface
        pg.draw.rect(self.surface, self.frameColour, (0, 0, self.width, self.height), border_radius = self.cornerRadius)

# Line graph class
class LineGraph:
    # Creates the graph
    def __init__(self, height, aspectRatio, borderWidth, centrePosition, independentVariable, dependentVariableNames, dependentVariableColours, dependentVariableRange, initialValues, lineWidth):
        # Stores the colour of the border
        self.borderColour = (43,45,66)
        # Stores the colour of the graph (background)
        self.graphColour = (248,249,250)

        # Stores the height of the graph
        self.height = height
        # Calculates and stores the width of the graph
        self.width = height * aspectRatio

        # Calculates and stores the border height
        self.borderHeight = self.height + borderWidth
        # Calculates and stores the border width
        self.borderWidth = self.width + borderWidth
        # Calculates and stores the width of individual bars of the border
        self.borderBarWidth = borderWidth//2

        # Stores the centre position of the graph
        self.centrePosition = centrePosition
        # Stores offsetted position of the graph
        self.offsettedPosition = self.centrePosition

        # Creates graph rect object
        self.rect = pg.Rect(0, 0, self.width, self.height)
        # Centres the graph rect
        self.rect.center = self.offsettedPosition
        # Creates the transparent graph surface object
        self.surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
        # Creates border rect object
        self.borderRect = pg.Rect(0, 0, self.borderWidth, self.borderHeight)
        # Centres the border rect
        self.borderRect.center = self.offsettedPosition

        # Left and bottom border line are created instead of the whole border - to satisfy design requirements
        # Creates the left border line rect (same dimensions as if it was a part of the border)
        self.leftBorderLine = pg.Rect(0,0,self.borderBarWidth, self.borderHeight - self.borderBarWidth)
        # Positions the left border line (same position as if it was a part of the border)
        self.leftBorderLine.center = (self.centrePosition[0] - self.width//2 - math.ceil(self.borderBarWidth/2), self.centrePosition[1] + self.borderBarWidth//2)
        # Creates the bottom border line rect (same dimensions as if it was a part of the border)
        self.bottomBorderLine = pg.Rect(0,0,self.borderWidth - self.borderBarWidth, self.borderBarWidth)
        self.bottomBorderLine.center = (self.centrePosition[0] - math.ceil(self.borderBarWidth/2), self.centrePosition[1] + self.height//2 + self.borderBarWidth//2)
        
        # Stores the text object to represent the name of the independent variable given
        self.independentVariableTextObject = Text(str(independentVariable), 1, int(self.height * 0.05), (self.width//2, self.height * 0.95))
        
        # Stores the names and respective colours assigned to the dependent variables
        self.dependentVariableNames = dependentVariableNames
        self.dependentVariableColours = dependentVariableColours
        # Stores the range of dependent variables
        self.dependentVariableRange = dependentVariableRange

        # Creates rectangle and text objects to display dependent variable names alongside a rectangle of their colour
        # Creates arrays for stroing the rectangle text objects
        self.dependentVariableDisplayRects = []
        self.dependentVariableTextObjects = []
        # Creates a rectangle and text object for each dependent variable
        for i in range(len(dependentVariableNames)):
            # Creates, positions, and stores the rectangle object
            rect = pg.Rect(0,0,self.height*0.015,self.height*0.015)
            rect.center = (self.width*0.015, (0.015 + i*0.015) * self.width)
            self.dependentVariableDisplayRects.append(rect)
            # Creates, positions, and stores the text object
            text = Text(self.dependentVariableNames[i], 1, int(self.height*0.03), (0, (0.015 + i*0.015) * self.width))
            # Bypasses regular centre positioning to control where the left of the text object is
            text.textRect.topleft = (self.width*0.0225, text.textRect.topleft[1])
            self.dependentVariableTextObjects.append(text)

        # Stores the width of the lines on the graph
        self.lineWidth = lineWidth

        # Creates array to store points on graph
        self.points = []
        # Adds the initial points to the points array
        initialPoints = []
        for value in initialValues:
            # Determines initial points position (when the independent variable is set to 0)
            point = [0, (1-value/self.dependentVariableRange) * self.height]
            initialPoints.append(point)
        self.points.append(initialPoints)
    
    # Plots new given values onto the graph
    def plot(self, newValues):
        # Creates array to temporarily store new points
        newPoints = []
        # Determines each of the Y point on the graph relating to each of these values 
        for value in newValues:
            point = [0, (1-value/self.dependentVariableRange) * self.height]
            newPoints.append(point)
        self.points.append(newPoints)

        # Calculates the X difference between on the graph
        interval = self.width/(len(self.points)-1)
        # Uses this difference to iteratively update the X position of every point on the graph
        for i in range(len(self.points)):
            for point in self.points[i]:
                point[0] = interval * i
        
        # Redraws the graph elements on the graph surface to represent this new plot
        # Draws the background of the graph 
        pg.draw.rect(self.surface, self.graphColour, (0,0, self.width, self.height))

        # Iterates through each indpendent variables, drawing their repsective lines
        for i in range(len(self.dependentVariableNames)):
            for j in range(len(self.points) - 1):
                pg.draw.line(self.surface, self.dependentVariableColours[i], self.points[j][i], self.points[j+1][i], self.lineWidth)
        
        # Iterates through each dependent variable drawing their rectangle and text object, displaying them - indicating which colour lines correspond to which dependent variable
        for i in range(len(self.dependentVariableNames)):
            pg.draw.rect(self.surface, self.dependentVariableColours[i], self.dependentVariableDisplayRects[i])
            self.dependentVariableTextObjects[i].draw(self.surface)

        # Draws the text object to represent the name of the independent variable given
        self.independentVariableTextObject.draw(self.surface)

    # Function to draw the graph
    def draw(self, surface):
        # Draws the left border line
        pg.draw.rect(surface, self.borderColour, self.bottomBorderLine)
        # Draws the bottom border line
        pg.draw.rect(surface, self.borderColour, self.leftBorderLine)

        # Draws the transparent graph surface
        surface.blit(self.surface, self.rect)

            