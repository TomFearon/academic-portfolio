# Import necessary modules
import math
import random as rnd
import numpy as np
import pygame as pg
import PathfindingModule as pfm
import json
import DatabaseModule as dm

# Initialises pygame
pg.init()
# Can be altered to set module into debug mode
debug = False

# Loads screen, so that images can be loaded
screen = pg.display.set_mode((1,1),pg.HIDDEN)

# Loads images of flora and preserves their transparent backgrounds
coldPlant = pg.image.load("Assets/ColdPlant.png").convert_alpha()
mildPlant = pg.image.load("Assets/MildPlant.png").convert_alpha()
hotPlant = pg.image.load("Assets/HotPlant.png").convert_alpha()

# Closes pygame
pg.quit()

# Flora class
class Flora:
    # Initialisation function
    def generate(self, position, temperatureFloat):
        # Stores the temperatrue float
        self.temperatureFloat = temperatureFloat
        # Plant image corresponding to the temperature of the square is determined
        if self.temperatureFloat > 7/12:
            self.unscaledPlantImage = hotPlant
        elif self.temperatureFloat > 5/12:
            self.unscaledPlantImage = mildPlant
        else:
            self.unscaledPlantImage = coldPlant
        # Randomly decides a size for the plant (either 1/3, 2/3 or 1)
        self.maxPlantSize = math.ceil(rnd.random()*3)/3
        self.currentPlantSize = self.maxPlantSize
        self.plantImageSize = self.maxPlantSize
        # Scales the plant image corresponding to the initial length of grid squares and the size of the plant
        self.scaledPlantImage = pg.transform.scale(self.unscaledPlantImage,(12*self.currentPlantSize,12*self.currentPlantSize))
    
        # Determines plant health
        self.maxHealth = rnd.uniform(self.maxPlantSize - 1/3, self.maxPlantSize) * 100
        self.health = self.maxHealth

        # Stores position of Plant
        self.position = position

        # Declares boolean variable indicating whether Plant is dead or not
        self.dead = False
        # Stores iteration when flora died
        self.iterationOfDeath = 0
    
    def load(self, position, temperatureFloat, maxPlantSize, currentPlantSize, plantImageSize, maxHealth, health, dead, iterationOfDeath):
        # Stores the position of the plant
        self.position = position

        # Stores the temperatrue float
        self.temperatureFloat = temperatureFloat
        # Plant image corresponding to the temperature of the square is determined
        if temperatureFloat > 7/12:
            self.unscaledPlantImage = hotPlant
        elif temperatureFloat > 5/12:
            self.unscaledPlantImage = mildPlant
        else:
            self.unscaledPlantImage = coldPlant
        # Stores max, current, and plant image size
        self.maxPlantSize = maxPlantSize
        self.currentPlantSize = currentPlantSize
        self.plantImageSize = plantImageSize
        # Scales the plant image corresponding to the initial length of grid squares and the size of the plant
        self.scaledPlantImage = pg.transform.scale(self.unscaledPlantImage,(12*self.currentPlantSize,12*self.currentPlantSize))

        # Determines plant health
        self.maxHealth = maxHealth
        self.health = health

        # Stores position of Plant
        self.position = position

        # Stores boolean variable indicating whether Plant is dead or not
        self.dead = dead

        # Stores the iteration of death
        self.iterationOfDeath = iterationOfDeath
    
    # Handles plant each iteration
    def handle(self, totalIterations):
        # If plant is dead
        if self.dead:
            # Revive plant after 20 seconds
            if totalIterations - self.iterationOfDeath >= 600:
                # Resets plant health ansd size
                self.dead = False
                self.health = self.maxHealth
                self.currentPlantSize = self.maxPlantSize
        # If health is less than 0, plant is dead
        elif self.health <= 0:
            self.dead = True
            # Records time of death
            self.iterationOfDeath = totalIterations
        else:
            # Slightly replenishes lost plant health by at most 1%
            self.health = min(self.health + rnd.uniform(0,0.01) * self.health,self.maxHealth)
            # Adjusts plant size accordingly to health
            self.currentPlantSize = math.ceil((self.health/100)*3)/3 
    
    # Scales the plant image
    def scale_image(self, length):
        # Scales the plant image corresponding to the length of the square and the size of the plant
        self.scaledPlantImage = pg.transform.scale(self.unscaledPlantImage,(length * self.currentPlantSize,length * self.currentPlantSize))
    
    # Handles fauna consuming flora
    def consume(self):
        # Determines amount of energy to be taken from plant
        energyTaken = rnd.uniform(2,4)
        self.health -= energyTaken
        # Adjusts plant size accordingly to health
        self.currentPlantSize =  math.ceil((self.health/100)*3)/3 
        # Returns 10% of energy to fauna to be absorbed
        return energyTaken * 0.1

    # Draws Plant
    def draw(self, screen, position, length):
        # If plant not dead
        if not self.dead:
            # Scales image if necessary
            if self.currentPlantSize != self.plantImageSize:
                self.scale_image(length)
                self.plantImageSize = self.currentPlantSize
            # Draws plant
            screen.blit(self.scaledPlantImage, (position[0],position[1]))

# Fauna class
class Fauna:
    # Function to generate animal when environment is intially created
    def generate_initial(self, position, seed, speedRange, sightRange, temperatureControlRange,  metabolicRateMultiplier, maxSightRadius):
        # Sets seed
        rnd.seed(seed)

        # Stores position of the animal
        self.position = position
    
        # Randomly sets speed ability
        self.speed = rnd.uniform(speedRange[0], speedRange[1])
        # Stores current displacement
        self.displacement = 0

        # Randomly sets sight ability
        self.sight = rnd.uniform(sightRange[0], sightRange[1])
        # Determines sight radius dependant on the animal's sight ability (minimum is 1)
        self.sightRadius = int(maxSightRadius * self.sight) + 1

        # Randomly sets temp control ability
        self.temperatureControl = rnd.uniform(temperatureControlRange[0], temperatureControlRange[1])

        # Determines metabolic rate and water loss rate dependant on attributes
        self.metabolicRate = metabolicRateMultiplier*self.sight + metabolicRateMultiplier*self.speed + metabolicRateMultiplier*self.temperatureControl
        self.waterLoss = self.metabolicRate*2

        # Stores animal's vital levels
        self.satietyLevel = 100
        self.hydrationLevel = 100
        self.internalTemperature = 0.5
        self.thermalStress = 0

        # Stores animals's lifespan
        self.lifespan = 0

        # Boolean variable indicating whether animal is currently reproducing
        self.reproducing = False
        # Stores animal which is being reproduced with
        self.mate = None
        # Stores the number of iterations since animal last reproduced
        self.sinceReproduction = 0
        
        # Assigns colour of animal dependant on their attributes
        self.colour = np.array([255 * self.speed, 255 * self.sight  , 255 * self.temperatureControl])

        # Resets seed
        rnd.seed()

        # Stores current path
        self.path = []

        # Stores path goal node
        self.pathGoal = None

        # Boolean variable to indicate whether animal is dead or not
        self.dead = False

        # Stores current action being condcted by animal
        self.action = None
        
        # Stores cause of death of animal
        self.causeOfDeath = None

    # Function to generate animal through reproduction
    def generate_offspring(self, position, parents, mutationIntensity,  metabolicRateMultiplier, maxSightRadius):
        # Stores position of the animal
        self.position = position

        # Determines speed of the animal which is the midpoint of its parents'
        self.speed = (parents[0].speed + parents[1].speed)/2
        # Applies random mutation, and clamps speed between 0 and 1
        self.speed = max(0, min(1, self.speed + rnd.uniform(-mutationIntensity, mutationIntensity)))
        # Stores displacement of animal
        self.displacement = 0

        # Determines sight of the animal which is the midpoint of its parents'
        self.sight = (parents[0].sight + parents[1].sight)/2
        # Applies random mutation, and clamps sight between 0 and 1
        self.sight = max(0, min(1, self.sight + rnd.uniform(-mutationIntensity, mutationIntensity)))
        # Determines sight radius dependant on the animal's sight ability (minimum is 1)
        self.sightRadius = int(maxSightRadius * self.sight) + 1

        # Determines temperature control of the animal which is the midpoint of its parents'
        self.temperatureControl = (parents[0].temperatureControl + parents[1].temperatureControl)/2
        # Applies random mutation, and clamps temperature control between 0 and 1
        self.temperatureControl = max(0, min(1, self.temperatureControl + rnd.uniform(-mutationIntensity, -mutationIntensity)))

        # Determines metabolic rate and water loss rate dependant on attributes
        self.metabolicRate = metabolicRateMultiplier*self.sight + metabolicRateMultiplier*self.speed + metabolicRateMultiplier*self.temperatureControl
        self.waterLoss = self.metabolicRate*2

        # Stores animal's vital levels
        self.satietyLevel = 100
        self.hydrationLevel = 100
        self.internalTemperature = 0.5
        self.thermalStress = 0

        # Stores animals's lifespan
        self.lifespan = 0

        # Boolean variable indicating whether animal is currently reproducing
        self.reproducing = False
        # Stores animal which is being reproduced with
        self.mate = None
        # Stores the number of iterations since animal last reproduced
        self.sinceReproduction = 0
        
        # Assigns colour of animal dependant on their attributes
        self.colour = np.array([255 * self.speed, 255 * self.sight  , 255 * self.temperatureControl])

        # Stores current path
        self.path = []

        # Stores path goal node
        self.pathGoal = None

        # Boolean variable to indicate whether animal is dead or not
        self.dead = False

        # Stores current action being condcted by animal
        self.action = None
        
        # Stores cause of death of animal
        self.causeOfDeath = None
    
    def load(self, position, speed, displacement, sight, sightRadius, temperatureControl, metabolicRate, waterLoss, satietyLevel, hydrationLevel, internalTemperature, thermalStress, lifespan, sinceReproduction, path, pathGoal, action):
        # Stores position of the animal
        self.position = np.array(position)
    
        # Stores speed of the animal
        self.speed = speed
        # Stores current displacement of the animal
        self.displacement = displacement
        # Stores sight ability
        self.sight = sight
        # Stores animal's sight radius
        self.sightRadius = sightRadius

        # Stores temp control ability
        self.temperatureControl = temperatureControl

        # Stores metabolic and water loss rate
        self.metabolicRate = metabolicRate
        self.waterLoss = waterLoss

        # Stores animal's vital levels
        self.satietyLevel = satietyLevel
        self.hydrationLevel = hydrationLevel
        self.internalTemperature = internalTemperature
        self.thermalStress = thermalStress

        # Stores animals's lifespan
        self.lifespan = lifespan

        # Stores boolean variable indicating whether animal is currently reproducing
        self.reproducing = False
        # Stores animal which is being reproduced with
        self.mate = None
        # Stores the number of iterations since animal last reproduced
        self.sinceReproduction = sinceReproduction
        
        # Assigns colour of animal dependant on their attributes
        self.colour = np.array([255 * self.speed, 255 * self.sight  , 255 * self.temperatureControl])

        # Stores current path
        self.path = path

        # Stores path goal node
        self.pathGoal = pathGoal

        # Stores boolean variable indicating whether animal is dead or not
        self.dead = False

        # Stores current action being condcted by animal
        self.action = action
        
        # Stores cause of death of animal
        self.causeOfDeath = None

    # Function to evaluate health of animal based on its vital levels
    def evaluate_health(self):
        return (self.satietyLevel + self.hydrationLevel + (100 - self.thermalStress))/3
    
    # Function to set random grid square as path goal
    def set_random_goal(self):
        # Loop until appropriate path goal is determined
        while True:
            # Determines random local path goal
            localPathGoal = [rnd.randint(0, self.bottomRightVisionPosition[0] - self.topLeftVisionPosition[0] - 1), rnd.randint(0, self.bottomRightVisionPosition[1] - self.topLeftVisionPosition[1] - 1)]
            if not self.populationVision[localPathGoal[1], localPathGoal[0]]:
                # Saves global path goal
                self.pathGoal = (int(localPathGoal[0] + self.topLeftVisionPosition[0]), int(localPathGoal[1] + self.topLeftVisionPosition[1]))
                return

    # Handles organism interactions each iteration
    def handle(self, environment, environmentDimensions, populationGrid):
        # Determines top left square of animal's vision
        topLeftX, topLeftY = int(max(0, self.position[0] - self.sightRadius)), int(max(0, self.position[1] - self.sightRadius))
        self.topLeftVisionPosition = np.array([topLeftX, topLeftY])
        # Determines bottom right square of animal's vision
        bottomRightX, bottomRightY = min(environmentDimensions[0], self.position[0] + self.sightRadius + 1), min(environmentDimensions[1], self.position[1] + self.sightRadius + 1)
        self.bottomRightVisionPosition = np.array([bottomRightX, bottomRightY])
        # Extracts sub-array of the environment - which animal can interpret
        self.environmentVision = environment[topLeftY:bottomRightY, topLeftX:bottomRightX]
        # Extracts sub-array of the population grid - which animal can interpret
        self.populationVision = populationGrid[topLeftY:bottomRightY, topLeftX:bottomRightX]
        # Stores index position of animal inside its vision arrays
        localPosition = np.array([self.position[0] - topLeftX , self.position[1] - topLeftY])

        # Reduces satiety level of animal dependant on metabolic rate
        self.satietyLevel -= (self.metabolicRate + self.metabolicRate * rnd.uniform(-0.1,0.1))
        
        # Reduces hydration level of animal dependant on rate of water loss
        self.hydrationLevel -= (self.waterLoss + self.waterLoss * rnd.uniform(-0.1,0.1))

        # Determines external temperature of animal's grid square
        externalTemperature = self.environmentVision[localPosition[1], localPosition[0]].temperatureFloat
        
        # Interpolates between animal's external and internal temperature, making their internal closer to the external
        self.internalTemperature = self.internalTemperature + 0.01*(externalTemperature - self.internalTemperature)
        # Controls internal temperature, bringing it closer to their ideal temperature
        self.internalTemperature = self.internalTemperature + 0.05*(self.temperatureControl**3) * (0.5-self.internalTemperature)
        # Increases thermal stress if organisms is too hot or too cold
        if self.internalTemperature < 0.4 or self.internalTemperature > 0.6:
            self.thermalStress = self.thermalStress + 0.1*(-1/((abs(0.5-self.internalTemperature)-0.1)/0.4-1))
        # Decreases thermal stress if organism's temperature is ideal
        else:
            self.thermalStress = max(0, self.thermalStress - rnd.uniform(0.1,0.4))

        # Increments animal's iterations since reproduction
        self.sinceReproduction += 1

        # Increments animal's lifespan
        self.lifespan += 1

        # If lifespan is greater than or equal to 15000 iterations, animal has chance of dying
        if self.lifespan >= 15000:
            # Determines weight of dying
            dieWeight = ((self.lifespan-15000)/1000)**2
            # Determines whether animal dies or not
            self.dead = rnd.choices([True, False], weights = [dieWeight, 1000])[0]
            # If animal died
            if self.dead:
                # Records cause of death
                self.causeOfDeath = "Old age"
                # Ends handling
                return

        # If satiety level is less or equal to 0, then animal dies
        if self.satietyLevel <= 0:
            self.dead = True
            # Records cause of death
            self.causeOfDeath = "Starvation"
            # Ends handling
            return
        
        # If hydration level is less than or equal to 0, then animal dies
        if self.hydrationLevel <= 0 :
            self.dead = True
            # Records cause of death
            self.causeOfDeath = "Thirst"
            # Ends hadling
            return
        
        # If thermal is greater than or equal to 100, then animal dies
        if self.thermalStress >= 100:
            self.dead = True
            # Records cause of death
            self.causeOfDeath = "Thermal stress"
            # Ends handling
            return

        # If animal does have not a path, then action is revaluated
        elif not self.pathGoal and not self.reproducing:
            # If animal is finishing eating or drinking, chance of animal wandering away is higher - so that it is clearer that the animal's action is changing
            if self.action == "Eat" or self.action == "Drink":
                idleWeight = 0.001
                wanderWeight = 0.1
            else:
                # Sets regular idle and wander weights
                idleWeight = 0.1
                wanderWeight = 0.001

            # Sets eat weight as 0
            eatWeight = 0
            # If satiety level is less than 75, then animal eat weight is increased
            if self.satietyLevel < 50:
                eatWeight = -(1/2)/((50-self.satietyLevel)/50-1) - (1/2)
            # If animal is not full and already eating, then eat weight is increased
            if self.satietyLevel < 95:
                if self.action == "Eat":
                    eatWeight = (eatWeight**2+1)*6

            # Sets drink weight as 0
            drinkWeight = 0
            # If hydration level is less than 75, then animal drink weight is increased
            if self.hydrationLevel < 75:
                drinkWeight = -1/((75-self.hydrationLevel)/75-1) - 1
            # If animal is not quenched and already drinking, then drink weight is increased
            if self.hydrationLevel < 97.5:
                if self.action == "Drink":
                    drinkWeight = (drinkWeight**2+1)*6
            
            # Sets warm up weight as 0
            warmUpWeight = 0
            # If animal is cold, animal warm up weight increases
            if self.internalTemperature < 0.4:
                warmUpWeight = -1/(self.thermalStress/100-1) - 1
            
            # Sets cool down weight as 0
            coolDownWeight = 0
            # If animal is hot, animal cool down weight increases
            if self.internalTemperature > 0.6:
                coolDownWeight = -1/(self.internalTemperature/100-1) - 1

            # Sets reproduce weight as 0
            reproduceWeight = 0
            # If animals is old enough
            if self.lifespan >= 4500:
                # Evaluates and stores animal's health
                health = self.evaluate_health()
                # If animal is healthy enough
                if health > 75:
                    # Calculates reproduce weight dependant on their health and how recently the have reproduced
                    reproduceWeight += (-1/((health-75)/25-1)-1) * (self.sinceReproduction/10000)

            # Randomly decides action to be conducted by animal dependant on calculated weights
            self.action = rnd.choices(["Idle", "Wander", "Eat", "Drink", "WarmUp", "CoolDown", "Reproduce"], weights=[idleWeight, wanderWeight, eatWeight, drinkWeight, warmUpWeight, coolDownWeight, reproduceWeight])[0]
        
        # If animal is idle, then do nothing
        if self.action == "Idle":
            # Ends handling
            return

        # If animal is wandering
        if self.action == "Wander":
            # If no path goal is set
            if not self.pathGoal:
                self.set_random_goal()
            # Ends handling
            return
        
        # If animals is trying to eat
        if self.action == "Eat":
            # Check for plants in adjacent grid squares - if there are plants present, then animal consumes them
            # Checks vertically adjacent squares for plants
            for dy in [-1,1]:
                # x and y of vertically adacent square
                x, y = localPosition[0], localPosition[1] + dy
                # If vertcially adjacent square is not in animal's vision, then skip it
                if y < 0 or y > self.populationVision.shape[0] - 1:
                    continue
                # Checks and stores state of the vertcially adjacent square
                neighbourSquare = self.populationVision[y, x]
                # If plant is present on adjacent square
                if isinstance(neighbourSquare, Flora):
                    # If plant is not dead
                    if not neighbourSquare.dead:
                        # Consumes plant and absorbs energy from it
                        energyAbsorbed = neighbourSquare.consume()
                        # Increases satiety level as a result of energy absorbed (satiety level is clamped to 100)
                        self.satietyLevel = min(self.satietyLevel + energyAbsorbed, 100)
                        # Ends handling
                        return
            # Checks horizontally adjacent squares for plants 
            for dx in [-1,1]:
                # x and y of horizontally adjacent square
                x, y = localPosition[0] + dx, localPosition[1]
                # If horizontally adjacent square is not in animal's vision, then skip it
                if x < 0 or x > self.populationVision.shape[1] - 1:
                    continue
            # Checks and stores state of horizontally adjacent square
                neighbourSquare = self.populationVision[y, x]
                # If plant is present on adjacent square
                if isinstance(neighbourSquare, Flora):
                    # If plant is not dead
                    if not neighbourSquare.dead:
                        # Consumes plant and absorbs energy from it
                        energyAbsorbed = neighbourSquare.consume()
                        # Increases satiety level as a result of energy absorbed (satiety level is clamped to 100)
                        self.satietyLevel = min(self.satietyLevel + energyAbsorbed, 100)
                        # Ends handling
                        return
            
            # Finds closest food source
            closestFood = pfm.find_closest_flora(self.populationVision, localPosition, Flora, findAdjacentEmptySquare=True)
            # Sets closest food source as path goal
            if closestFood:
                self.pathGoal = (closestFood[0] + topLeftX, closestFood[1] + topLeftY)
                # Ends handling
                return
            
            # If no food in sight, sets random path goal - to search for food
            self.set_random_goal()
            # Ends handling
            return

        # If animal is trying to drink
        if self.action == "Drink":
            # Checks adjacent grid squares for water sources, if these are present, then animal will drink
            # Checks vertically adjacent squares
            for dy in [-1,1]:
                # x and y of vertically adjacent square
                x, y = localPosition[0], localPosition[1] + dy
                # If vertically adjacent square is not in animal's vision, then skip it
                if y < 0 or y > self.environmentVision.shape[0] - 1:
                    continue
                # Checks and stores state of adjacent square
                neighbourSquare = self.environmentVision[y, x]
                # If water depth of adjacent square is greater than 0, then drink
                if neighbourSquare.waterDepth > 0:
                    # Increases hydration level as a result of drinking
                    self.hydrationLevel += rnd.uniform(0.2,0.4)
                    # Ends handling
                    return
            # Checks horizontally adjacent squares
            for dx in [-1,1]:
                # x and y of horizontally adjacent square
                x, y = localPosition[0] + dx, localPosition[1]
                # If horizontally adjacent square is not in animal's vision, then skip it
                if x < 0 or x > self.populationVision.shape[1] - 1:
                    continue
                # Checks and stores state of adjacent square
                neighbourSquare = self.environmentVision[y, x]
                # If water depth of adjacent squares is greater than 0, then drink
                if neighbourSquare.waterDepth > 0:
                    # Increases hydration level as result of drinking
                    self.hydrationLevel += rnd.uniform(0.2,0.4)
                    # Ends handling
                    return
            
            # Determines closest water source
            closestWater = pfm.find_closest_water(self.environmentVision, self.populationVision, localPosition, findAdjacentEmptySquare=True)
            # Sets water source as path goal
            if closestWater:
                self.pathGoal = (closestWater[0] + topLeftX, closestWater[1] + topLeftY)
                # Ends handling
                return
            
            # If no water source in sight, sets random path goal - to search for water
            self.set_random_goal()
            # Ends handling
            return
        
        # If animal is trying to warm up
        if self.action == "WarmUp":
            # Find hottest square in sight
            hottestSquare = pfm.find_thermal_extreme(self.environmentVision, self.populationVision, extreme = "Hot")
            # Set path goal as hottest square
            if hottestSquare:
                self.pathGoal = (hottestSquare[0] + topLeftX, hottestSquare[1] + topLeftY)
                # Ends handling
                return
            # Ends handling
            return
        
        # If animal is trying to coold down
        if self.action == "CoolDown":
            # find coldest square in sight
            coldestSquare = pfm.find_thermal_extreme(self.environmentVision, self.populationVision, extreme = "Cold")
            # Set path goal as coldest square
            if coldestSquare:
                self.pathGoal = (coldestSquare[0] + topLeftX, coldestSquare[1] + topLeftY)
                # Ends handling
                return
            # Ends handling
            return

        # If animal is trying to reproduce
        if self.action == "Reproduce":
            # If animal does not currently have a mate
            if not self.mate:
                # Determine square of mate and goal square which if reached, will allow animal to reproduce with mate
                localPathGoal, mateLocalPosition = pfm.find_healthiest_mate(self.populationVision, localPosition, Fauna, findAdjacentEmptySquare = True)
                # If goal square, therefore, also square of a mate has been determined
                if localPathGoal:
                    # Stores mate object
                    self.mate =  self.populationVision[mateLocalPosition[1], mateLocalPosition[0]]
                    # Updates reproducing attribute to indicate that animal is reproducing
                    self.reproducing = True
                    # Updates mate's reproducing attribute to indicate that animal is reproducing
                    self.mate.reproducing = True
                    # Sets mate as idle, so it does not move
                    self.mate.action = "Idle"
                    # Clears path and path goal of mate so that it does not move
                    self.mate.pathGoal = None
                    self.mate.path = []
                    # Determines global path goal of animal
                    self.pathGoal = (localPathGoal[0] + topLeftX, localPathGoal[1] + topLeftY)
                    # Clears any potential current path
                    self.path = []
                    return
                
                # If no mate was found, move to random grid square - to search for mate
                self.set_random_goal()
                # Ends handling
                return
            
            # If animal does currently have a mate
            # If mate dies
            if self.mate.dead:
                # Indicate that animal is not be reproducing
                self.reproducing = False
                # Indicate that animal does not have a mate
                self.mate = None
                return
            # If animal does not have a goal, then animal has reached square where it can reproduce
            elif not self.pathGoal:
                # Updates variable storing iterations since reproduction
                self.sinceReproduction = 0
                # Indicate that animal is not reproducing
                self.reproducing = False
                # Clears any potential path
                self.path = []

                # Indicate that mate is not reproducing
                self.mate.sinceReproduction = 0
                # Updates variable storing mate's iterations since reproduction
                self.mate.reproducing = False

                # Returns mate, so that reproduction can be conducted
                return self.mate

    # Moves animal along current path and generates new paths where necessary
    def move(self):
        # If path goal exits, but no path, then path is generated
        if self.pathGoal and not self.path:
            self.path = pfm.generate_path(self.populationVision, self.environmentVision, self.position, self.pathGoal, self.topLeftVisionPosition)

        # If path exists
        if self.path:
            # Adds speed to displacement
            self.displacement += self.speed
            # Determines position of next node on path
            newPosition = self.path[0]
            # Calculates cost of moving to this next node
            dx, dy = newPosition[0] - self.position[0], newPosition[1] - self.position[1]
            displacementCost = math.sqrt(dx**2 + dy**2)
            # If next node is water, then cost is multiplied by 4
            if self.environmentVision[newPosition[1] - self.topLeftVisionPosition[1] - 1, newPosition[0] - self.topLeftVisionPosition[0] - 1].waterDepth > 0:
                displacementCost *= 4
            # If displacemt of animal is greater than displacement cost, then animal will move
            if self.displacement >= displacementCost:
                # Updates animal's position
                self.position = np.array(self.path.pop(0))
                # Resets animal's displacement 
                self.displacement = 0
                # If animal has finished path, then set path goal to nothing
                if not self.path:
                    self.pathGoal = None
        # If path goal exits, but no path (so path failed to generate)
        elif self.pathGoal:
            # If animal is reproducing (so wasn't able to find path to mate)
            if self.reproducing:
                # Indicate that animal is no longer reproducing
                self.reproducing = False
                
                # Indicate the animal's mate is no longer reproducing
                self.mate.reproducing = False

                # Sets animal's mate to none
                self.mate = None

                # Resets variable storing iterations since animal tried reproducing
                self.sinceReproduction = 0
        
        # Returns current position of animal
        return self.position
        
    # Draws the organism on the screen
    def draw(self, screen, position, gridSquareLength):
        pg.draw.rect(screen, self.colour, (position[0],position[1],gridSquareLength,gridSquareLength), border_radius=gridSquareLength//6)

# Population class
class Population:
    # Generates the initial population
    def generate(self, speciesCount, speciesSize, environment, environmentDimensions, speedRange = [0.2,0.8], sightRange = [0.2,0.8], temperatureControlRange = [0,1], metabolicRateMultiplier = 2/75, maxSightRadius = 20):
        # Ensures that variables are integers
        speciesCount, speciesSize = int(speciesCount), int(speciesSize)
        # Ensures variables are ndarrays
        self.environment, self.environmentDimensions = np.array(environment), np.array(environmentDimensions)
        # Stores metabolic rate multiplier and max sight radius
        self.metabolicRateMultiplier = metabolicRateMultiplier
        self.maxSightRadius = maxSightRadius
        
        # Validates that the number of species present in the environment and the size of these species are both greater than 2
        if speciesCount < 2:
            raise ValueError("Error: species count must be greater than 1.")
        if speciesSize < 2:
            raise ValueError("Error: species size must be greater than 1.")
        
        # Validates that speed range bounds and are within their domain and that the upper is greater than the lower
        if speedRange[0] > speedRange[1]:
            raise ValueError("Error: Upper bound of the speed range must be greater than the lower.")
        if speedRange[0] < 0:
            raise ValueError("Error: Lower bound of speed range must be greater than or equal to 0.")
        if speedRange[1] > 1:
            raise ValueError("Error: Lower bound of speed range must be lower than or equal to 1.")
        
        # Validates that sight range bounds are within their domain and that the upper is greater than the lower
        if sightRange[0] > sightRange[1]:
            raise ValueError("Error: Upper bound of the sight range must be greater than the lower.")
        if sightRange[0] < 0:
            raise ValueError("Error: Lower bound of sight range must be greater than or equal to 0.")
        if sightRange[1] > 1:
            raise ValueError("Error: Lower bound of sight range must be lower than or equal to 1.")
        
        # Validates that temperature control range bounds are within their domain and that the upper is greater than the lower
        if temperatureControlRange[0] > temperatureControlRange[1]:
            raise ValueError("Error: Upper bound of the temperature control range must be greater than the lower.")
        if temperatureControlRange[0] < 0:
            raise ValueError("Error: Lower bound of temperataure control range must be greater than or equal to 0.")
        if temperatureControlRange[1] > 1:
            raise ValueError("Error: Lower bound of temperature control range must be lower than or equal to 1.")
        
        # Validates that metabolic rate multiplier is within its domain
        if not 1/75 <= metabolicRateMultiplier <= 1/25:
            raise ValueError("Error: metabolic rate mutliplier must be between 1/75 and 1/25.")
        
        # Validates that max sight radius is within its domain
        if not 5 <= maxSightRadius <= 40:
            raise ValueError("Error: max sight radius must be between 5 and 40.")

        # Generates empty ndarray with dimensions equal to environment dimensions to position organisms in
        self.populationGrid = np.full((self.environmentDimensions[1]+1,self.environmentDimensions[0]+1), None)

        # Generates list for storing organisms
        self.organisms = []

        # Appends plants to the population grid array corresponding to their position in the environment and to the organisms list
        for y in range(self.environmentDimensions[1]):
            for x in range(self.environmentDimensions[0]):
                # Determines whether flora is present
                if self.environment[y,x].floraPresent:
                    # Creates plant object of the class Flora, generates it and appends it to both arrays
                    plant = Flora()
                    plant.generate((x,y),self.environment[y,x].temperatureFloat)
                    self.populationGrid[y,x] = plant
                    self.organisms.append(plant)
        
        # Initially positions species' in circles
        # Determines the radius 
        radius = speciesSize
        # Determines a random centre for each species circle
        centres = []
        for i in range(speciesCount):
            while True:
                x, y = rnd.randint(radius, self.environmentDimensions[0] - radius - 1), rnd.randint(radius, self.environmentDimensions[1] - radius - 1)
                # If centre is empty, then loop ends
                if self.populationGrid[y,x] == None:
                    break
            # Stores centre
            centres.append(np.array([x,y]))

        # Randomly places fauna into corresponding species circles   
        for i in range(speciesCount):
            # Sets seed, so that animals of the same species are procedurally generated the same
            speciesSeed = rnd.random()
            for j in range(speciesSize):
                while True:
                    # Determines random position in circle for fauna to be positioned (using equation of circle)
                    dx = rnd.randint(-radius, radius)
                    dyMaxMagnitude = math.floor(((radius**2)-(dx**2))**(1/2))
                    dy = rnd.randint(-dyMaxMagnitude, dyMaxMagnitude)
                    position = centres[i] + np.array([dx,dy])
                    # Cancels placement if grid square contains an organism
                    if self.populationGrid[position[1], position[0]] == None:
                        # Generates animal and positions it in grid square
                        animal = Fauna()
                        animal.generate_initial(position, speciesSeed, speedRange, sightRange, temperatureControlRange, self.metabolicRateMultiplier, self.maxSightRadius)
                        # Stores animal
                        self.populationGrid[position[1], position[0]] = animal
                        self.organisms.append(animal)
                        break
        
        # Declares the time since last iteration
        self.lastIterationTime = 0
        # Stores total iterations of the simulation of the population
        self.totalIterations = 0
    
    # Function used to save the state of the population
    def save(self, tableId):
        # Deletes the current table
        dm.delete_table(f"Population{tableId}")
        # Creates a table to store population
        dm.create_table(f"Population{tableId}",[["Type", "TEXT"],["Data", "TEXT"]])
        # Iterates through each organism in the population
        for organism in self.organisms:   
            # If flora, save the flora object - stores attributes in a dictionary
            if isinstance(organism, Flora):
                plantData = {"position": organism.position,
                            "temperatureFloat": organism.temperatureFloat,
                            "maxPlantSize": organism.maxPlantSize,
                            "currentPlantSize": organism.currentPlantSize,
                            "plantImageSize": organism.plantImageSize,
                            "maxHealth": organism.maxHealth,
                            "health": organism.health,
                            "dead": organism.dead,
                            "iterationOfDeath": organism.iterationOfDeath
                            }
                # Converts dictionary into data which can be stored in the database and inserts it into database
                jsonData = json.dumps(plantData)
                dm.insert_query(f"Population{tableId}",[["Flora", jsonData]])
            # Fauna, save the fauna object - stores attributes in a dictionary
            elif isinstance(organism, Fauna):
                animalData = {"position": [int(organism.position[0]), int(organism.position[1])],
                            "speed": organism.speed,
                            "displacement": organism.displacement,
                            "sight": organism.sight,
                            "sightRadius": organism.sightRadius,
                            "temperatureControl": organism.temperatureControl,
                            "metabolicRate": organism.metabolicRate,
                            "waterLoss": organism.waterLoss,
                            "satietyLevel": organism.satietyLevel,
                            "hydrationLevel": organism.hydrationLevel,
                            "internalTemperature": organism.internalTemperature,
                            "thermalStress": organism.thermalStress,
                            "lifespan": organism.lifespan,
                            "sinceReproduction": organism.sinceReproduction,
                            "path": organism.path,
                            "pathGoal": organism.pathGoal,
                            "action": organism.action
                            }
                # Converts dictionary into data which can be stored in the database and inserts it into database
                jsonData = json.dumps(animalData)
                dm.insert_query(f"Population{tableId}",[["Fauna", jsonData]])
        # Stores metabolic rate mutliplier, max sight radius and total iterations to the table
        dm.insert_query(f"Population{tableId}", [["metabolicRateMultiplier", self.metabolicRateMultiplier]])
        dm.insert_query(f"Population{tableId}", [["maxSightRadius", self.maxSightRadius]])
        dm.insert_query(f"Population{tableId}", [["totalIterations", self.totalIterations]])

    # Function used to load a population
    def load(self, environment, environmentDimensions, tableId):
        # Ensures variables are ndarrays
        self.environment, self.environmentDimensions = np.array(environment), np.array(environmentDimensions)

        # Generates empty ndarray with dimensions equal to environment dimensions to position organisms in
        self.populationGrid = np.full((self.environmentDimensions[1]+1,self.environmentDimensions[0]+1), None)

        # Generates list for storing organisms
        self.organisms = []

        # Selects population data from the table
        table = dm.select_query(f"Population{tableId}", [["*"]])
        for record in table:
            # If record tpe is flora
            if record[1] == "Flora":
                # Extracts plant's dictionary and uses this to create and load a 'Flora' object
                plantDictionary = json.loads(record[2])
                plant = Flora()
                plant.load(**plantDictionary)
                # Stores the plant
                self.populationGrid[plant.position[1], plant.position[0]] = plant
                self.organisms.append(plant)
            # Record type is fauan
            elif record[1] == "Fauna":
                # Extracts animal's dictionary and uses this to create and load a 'Fauna' object
                animalDictionary = json.loads(record[2])
                animal = Fauna()
                animal.load(**animalDictionary)
                # Stores the animal
                self.populationGrid[animal.position[1], animal.position[0]] = animal
                self.organisms.append(animal)
            # If record type is the metabolic rate mutliplier attribute, store it
            elif record[1] == "metabolicRateMultiplier":
                self.metabolicRateMultiplier = float(record[2])
            # If record type is the max sight radius attribute, store it
            elif record[1] == "maxSightRadius":
                self.maxSightRadius = int(record[2])
            # If record type is the total iterations attribute, store it
            elif record[1] == "totalIterations":
                self.totalIterations = int(record[2])

        self.lastIterationTime = 0

    # Processes and records important data regarding the population
    def record(self, tableId, newTable = False, returnConvertedData = False):
        # Creates the initial sums of all important statistics - used to calculate their mean
        speedSum = 0
        sightSum = 0
        temperatureControlSum = 0
        metabolicRateSum = 0
        lifespanSum = 0
        populationCount = 0
        # Iterates through all organisms
        for organism in self.organisms:
            # If organism is an animal
            if isinstance(organism, Fauna):
                # Increments the population count
                populationCount += 1
                # Add organim's attributes to the sum of the important statistics
                speedSum += organism.speed
                sightSum += organism.sight
                temperatureControlSum += organism.temperatureControl
                metabolicRateSum += organism.metabolicRate
                lifespanSum += organism.lifespan
        
        try:
            # Calculates the mean for all the important statistics
            speedMean = round(speedSum/populationCount,4)
            sightMean = round(sightSum/populationCount,4)
            temperatureControlMean = round(temperatureControlSum/populationCount,4)
            metabolicRateMean = round(metabolicRateSum/populationCount,6)
            ageMean = round(lifespanSum/populationCount,2)
        # If there is a zero division error (the population is zero)
        except ZeroDivisionError:
            # Sets all means to zero
            speedMean = 0
            sightMean = 0
            temperatureControlMean = 0
            metabolicRateMean = 0
            ageMean = 0

        # If the function is required to create a new table
        if newTable:
            # Deletes the current table
            dm.delete_table(f"FaunaData{tableId}")
            # Creates a table to store fauna data
            dm.create_table(f"FaunaData{tableId}",[["AvgSpeed","INTEGER"],["AvgSight","INTEGER"],["AvgTemperatureControl","INTEGER"],["AvgMetabolicRate","INTEGER"],["AvgAge","INTEGER"]])
        
        # Comprises statistics data into an array
        data = [speedMean, sightMean, temperatureControlMean, metabolicRateMean, ageMean]
        # Inserts this data into an array
        dm.insert_query(f"FaunaData{tableId}",[data])

        # If function is required to convert and return the data it has recorded
        if returnConvertedData:
            # Converts the average metabolic rate to a float between 0 and 1, with 1 representing the highest possible metabolic rate of that population (dependent on the metabolic rate mutliplier)
            data[3] *= 1/(3*self.metabolicRateMultiplier)
            # Converts the average age to a float between 0 and 1 (animals tend to live 15000 iterations, so average age * 1/20000 should yield a float below 1)
            data[4] *= 1/20000
            # Returns the converted data
            return data
    
    # Retrieves all record important statistics regarding the population
    def retrieve(self, tableId, convertValues = False):
        # Exrtracts the table as a 2 dimensional array - with each sub-array being a record
        table = dm.select_query(f"FaunaData{tableId}", [["AvgSpeed","AvgSight","AvgTemperatureControl","AvgMetabolicRate","AvgAge"]])

        # Creates data array, used to return data concerned with the table
        data = []
        # Iterates through all records
        for record in table:
            # If the function is required to convert the values
            if convertValues:
                # Converts record into a mutable data type
                record = list(record)
                # Ensures all values are converted to a float between 0 and 1
                record[3] *= 1/(3*self.metabolicRateMultiplier)
                record[4] *= 1/20000
            # Stores the record in the data array
            data.append(record)
        
        # Returns the data retrieved
        return data

    # Handles the population each iteration
    def handle(self, totalTime, mutationIntensity):
        # If enough time has passed since last iteration, begin next iteration
        if totalTime - self.lastIterationTime >= 1000/30:
            # Updates last iteraration time
            self.lastIterationTime = totalTime
            # Updates total iterations
            self.totalIterations += 1

            # Records current organisms - so that dead animals can be removed safely
            currentOrganisms = self.organisms
            # Iterates through each organism
            for organism in self.organisms:
                # If flora
                if isinstance(organism, Flora):
                    # Handles flora
                    organism.handle(self.totalIterations)
                # If organism is an animal
                else:
                    # Records old position of animal
                    oldPosition = organism.position
                    # Handles animal interactions and determines whether animal is reproducing - if so, its mate is stored
                    mate = organism.handle(self.environment, self.environmentDimensions, self.populationGrid)
                    # If animal is reproducing
                    if mate:
                        # Set animal's mate to none
                        organism.mate = None
                        # Generates offspring based on its parents
                        offspring = Fauna()
                        offspringPosition = mate.position
                        offspring.generate_offspring(offspringPosition, [organism, mate], mutationIntensity, self.metabolicRateMultiplier, self.maxSightRadius)
                        # Stores offspring
                        currentOrganisms.append(offspring)
                        self.populationGrid[offspringPosition[1], offspringPosition[0]] = offspring
                    # If animal dies
                    if organism.dead:
                        # Remove animal from population grid array
                        self.populationGrid[oldPosition[1], oldPosition[0]] = None
                        # Removes animal from organisms list
                        currentOrganisms.remove(organism)
                        continue
                    # Updates position - if organism moves
                    currentPosition = organism.move()
                    # Clears old position
                    self.populationGrid[oldPosition[1], oldPosition[0]] = None
                    # Moves to new position
                    self.populationGrid[currentPosition[1], currentPosition[0]] = organism
            # Updates organisms list - so that dead animals are removed
            self.organisms = currentOrganisms
        
        # Returns total iterations count
        return self.totalIterations
            
    # Draw the population on the environment
    def draw(self, screen, screenPixelDimensions, topLeft, gridSquareLength, viewChanged):
        # Determines bottom right square of the section of the environment to be displayed
        bottomRight = np.array([topLeft[0] + screenPixelDimensions[0]//gridSquareLength + 1, topLeft[1] + screenPixelDimensions[1]//gridSquareLength + 1])

        # Draws each grid square within the section of the environment
        # X,Y point to local coordinates of the section of the environment being displayed
        X, Y = 0, 0
        # Iterates through the global x,y of the environment
        for y in range(topLeft[1], bottomRight[1]):
            for x in range(topLeft[0], bottomRight[0]):
                organism = self.populationGrid[y,x]
                if organism:
                    # Determines whether organism is flora
                    if isinstance(organism, Flora):
                        # Scales flora if view has changed
                        if viewChanged:
                            organism.scale_image(gridSquareLength)
                        # Draws flora
                        organism.draw(screen, (X * gridSquareLength, Y * gridSquareLength), gridSquareLength)
                    else:
                        # Draws fauna
                        organism.draw(screen, (X * gridSquareLength, Y * gridSquareLength), gridSquareLength)
                # Increments local X pointer
                X += 1
            # Resets local X pointer and increments local Y pointer
            X, Y = 0, Y + 1

