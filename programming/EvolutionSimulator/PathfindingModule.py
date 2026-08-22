# Imports necessary modules
import pygame as pg
import numpy as np
import heapq
import math

# Initialises pygame
pg.init()

# Used to find the eucledian distance from node to the goal
def heuristic(a, b):
        return math. sqrt(((a[0]-b[0])**2) + ((a[1]-b[1])**2))

# Determines the g cost of moving from one node to another
def cost(dx, dy):
    return math.sqrt(dx**2 + dy**2)

# Verifies whether given node is in bounds of the grid or not
def inBounds(pos, grid):
    x, y = pos
    return 0 <= x < grid.shape[1] and 0 <= y < grid.shape[0]

# Astar path finding algorithm - returns an array of node coordinates in order of the optimal path determined
def astar(grid, start, goal, modifierGrid):
    # Ensures that parameters are stored under the necessary data type
    grid, start, goal = np.array(grid), tuple(start), tuple(goal)

    # Open set of nodes to be considered
    openSet = []
    # Pushes initial node onto heap
    heapq.heappush(openSet, (heuristic(start, goal), 0, start))
    # Dictionary for determining which grid squares lead to which
    cameFrom = {}
    # Dictionary storing the smallest discovered g score for each node
    gScore = {start:0}

    # Loops through until optimal path is determined, or it is determined that no path is possible
    while openSet:
        # Sets current node as node with minimum f score in set
        current = heapq.heappop(openSet)[2]

        # If current node is at goal, optimal path has been found - this is consequently, returned
        if current == goal:
            # Determines the optimal path determined by woring backwards using the 'came from' dictionary
            path = []
            while current in cameFrom:
                path.append((int(current[0]), int(current[1])))
                current = cameFrom[current]
            # Returns optimal path - ending the pathfinding loop
            return path[::-1]

        # Iterates through all potential neighbbours surroudning current node
        for dx in range(-1,2):
            for dy in range(-1,2):
                # Excludes the current node
                if dx == 0 and dy == 0:
                    pass
                
                # Determines the overall position of the neighbour
                neighbour = (current[0] + dx, current[1] + dy)

                # Skips iteration if neighbour is an obstacle
                if inBounds(neighbour, grid):
                    if grid[neighbour[1], neighbour[0]]:
                        continue
                    # If neigbour is diagonal to current
                    if dx != 0 and dy != 0:
                        # Prevents corner cutting
                        horizontal = [current[0] + dx, current[1]]
                        if not inBounds(horizontal, grid):
                            continue
                        vertical = [current[0], current[1] + dy]
                        if not inBounds(vertical, grid):
                            continue
                        if grid[horizontal[1], horizontal[0]] or grid[vertical[1], vertical[0]]:
                            continue
                else:
                    continue
                
                # Tentative g score determined - not necsseraily optimal
                gCost = cost(dx,dy) 
                modifier = modifierGrid[neighbour[1], neighbour[0]]
                if modifier:
                    gCost *= modifier
                tentativeG = gScore[current] + gCost

                # If g score for neighbour node is smaller than smallest known g score or current g score doesn't exist
                if neighbour not in gScore or tentativeG < gScore[neighbour]:
                    # Changes or appends g score to list - corresponding to this neighbour node
                    gScore[neighbour] = tentativeG
                    # Determines f score - takes into account g score and euclidian distance from the goal
                    fScore = tentativeG + heuristic(neighbour, goal)
                    # Pushes this neighbour node onto the heap - to be considered
                    heapq.heappush(openSet, (fScore, tentativeG, neighbour))
                    # Stores which node this neighbur comes from
                    cameFrom[neighbour] = current
    
    # Returns empty array if optimal path not found
    return []

# Generates path between agent (animal) and goal  in the section of the environment provided
def generate_path(populationGrid, environmentGrid, globalAgentPos, globalGoalPos, topLeftPos):
    # Determines local position of agent in the section of the environment
    localAgentPos = (globalAgentPos[0] - topLeftPos[0], globalAgentPos[1] - topLeftPos[1])
    # Determines local position of goal in the section of the environment
    localGoalPos = (globalGoalPos[0] - topLeftPos[0], globalGoalPos[1] - topLeftPos[1])

    # Sets goal position and agent position to none - so that they are not treated as obstacles
    populationGrid[localAgentPos[1], localAgentPos[0]] = None
    populationGrid[localGoalPos[1], localGoalPos[0]] = None
    
    # Creates water grid, recording position of water, to modify pathfinding costs
    waterGrid = np.full((environmentGrid.shape[0], environmentGrid.shape[1]), None)
    # Iterates throuhg grid squares in grid
    for y in range(environmentGrid.shape[0]):
        for x in range(environmentGrid.shape[1]):
            # If square is water, record this in the water grid
            if environmentGrid[y,x].waterDepth > 0:
                waterGrid[y,x] = 4
    
    # Create the path
    path = astar(populationGrid, localAgentPos, localGoalPos, waterGrid)

    # Converts path from local to global positions of nodes
    for i in range(len(path)):
        path[i] = (path[i][0] + int(topLeftPos[0]), path[i][1] + int(topLeftPos[1]))
    
    # Returns the generated path
    return path

# Finds empty grid square closest to agent which is adjacent to the discovered objects
def find_adjacent_empty_squares(discoveredObjects, obstacleGrid, localAgentPos, returnOriginalSquare = False):
    # While there are still objects to check for adjacent empty grid squares
    while discoveredObjects:
        # Determines the node position of closest object
        closestSquare = heapq.heappop(discoveredObjects)[1]
        # Creates list for storing the adjacent empty grid squares
        adjacentEmptySquares = []

        # Checks vertically adjacent squares
        for dy in [-1,1]:
            # x and y of vertically adjacent grid square
            x, y = int(closestSquare[0]), int(closestSquare[1]) + dy
            # If square is not in grid, then skip
            if y < 0 or y > obstacleGrid.shape[0] - 1:
                continue
            # If there is no obstacle in the adjacent grid square position
            if not obstacleGrid[y,x]:
                # Determine the heuristic distance from the agent to this grid square
                distance = heuristic(localAgentPos, (x,y))
                # Pushes grid square position and its distance onto the heap
                heapq.heappush(adjacentEmptySquares, (distance,(x,y)))
        
        # Checks horizontally adjacent grid squares
        for dx in [-1,1]:
            # x and y of horizontally adjacent grid square
            x, y = closestSquare[0] + dx, closestSquare[1]
            # If square is not in grid, then skip
            if x < 0 or x > obstacleGrid.shape[1] - 1:
                continue
            # If there is no obstacle in the adjacent grid square position
            if not obstacleGrid[y,x]:
                # Determines the heuristic distance from the agent to this grid square 
                distance = heuristic(localAgentPos, (x,y))
                # Pushes grid square position and its distance onto the heap
                heapq.heappush(adjacentEmptySquares, (distance,(x,y)))
        
        # If adjacent grid squares have been discovered
        if adjacentEmptySquares:
            # If the function is required to return the original square in addition to its adjacent square
            if returnOriginalSquare:
                # Returns adjacent and original square
                return heapq.heappop(adjacentEmptySquares)[1], closestSquare
            # Return adjacent empty grid square which is shortest distance from the agent
            return heapq.heappop(adjacentEmptySquares)[1]
    # If the function is required to return the original square, return two return values, so that they can be unpacked
    if returnOriginalSquare:
        return None, None
    return

# Finds the plant with shortest heursitic distance from the agent(animal)
def find_closest_flora(populationGrid, localAgentPos, floraClass, findAdjacentEmptySquare = False):
    # Declares list for storing plants discovered within the grid
    discoveredFlora = []
    # Iterates through grid squares in grid
    for y in range(populationGrid.shape[0]):
        for x in range(populationGrid.shape[1]):
            # Stores the square state
            square = populationGrid[y,x]
            # If the square is a plant
            if isinstance(square, floraClass):
                # If the plant is not dead
                if not populationGrid[y,x].dead:
                    # Calculate heristic distance from the agent to this plant
                    distance = heuristic(localAgentPos, (x,y))
                    # Pushes grid square position and distance from agent onto the heap
                    heapq.heappush(discoveredFlora, (distance,(int(x),int(y))))
    
    # If there are plants discovered
    if discoveredFlora:
        # If the function is required to find adjacent empty grid squares
        if findAdjacentEmptySquare:
            # Finds closest grid square which is adjacent to a plant within the grid
            adjacentEmptySquare = find_adjacent_empty_squares(discoveredFlora, populationGrid, localAgentPos)
            # If adjacent empty grid square discovered
            if adjacentEmptySquare:
                # Return empty grid square which is adjacent to plant
                return adjacentEmptySquare
        # Returns closest plant if function is not required to find adjacent empty grid squares
        else:
            return heapq.heappop(discoveredFlora)[1]
    # Returns nothing if no grid square which satisfy the constraints are discovered
    return

# Finds the water source with the shortest heuristic distance from the agent (animal)
def find_closest_water(environmentGrid, populationGrid, localAgentPos, findAdjacentEmptySquare = False):
    # Declares list for storing water sources discovered in the grid
    discoveredWater = []
    # Iterates through grid squares in grid
    for y in range(environmentGrid.shape[0]):
        for x in range(environmentGrid.shape[1]):
            # Stores the state of the grid square
            square = environmentGrid[y,x]
            # If grid square is water
            if square.waterDepth > 0:
                # Calculate heuristic distance of water source from the agent
                distance = heuristic(localAgentPos, (x,y))
                # Pushes the position of the water source and its distance from the agent onto the heap
                heapq.heappush(discoveredWater, (distance,(int(x),int(y))))
    
    # If there are water sources discovered
    if discoveredWater:
        # If the function is required to find adjacent empty grid squares
        if findAdjacentEmptySquare:
            # Finds closest grid square which is adjacent to a water source within the grid
            adjacentEmptySquare = find_adjacent_empty_squares(discoveredWater, populationGrid, localAgentPos)
            # If adjacent empty grid square discovered
            if adjacentEmptySquare:
                # Return empty grid square which is adjacent to water
                return adjacentEmptySquare
        # Returns closest water if function is not required to find adjacent empty grid squares
        else:
            return heapq.heappop(discoveredWater)[1]
    # Returns nothing if no grid square which satisfy the constraints are discovered
    return

# Returns 1-temp, so that hottest squares are treated as the smallest element by the heap
def find_hot_temperature(square):
    return 1-square.temperatureFloat

# Returns temp, so that coldest squares are treated as the smallest element by the heap
def find_cold_temperature(square):
    return square.temperatureFloat

# Function for finding closest hot and cold squares in grid
def find_thermal_extreme(environmentGrid, populationGrid, extreme = "Hot"):
    # Declares list for storing the temperatures discovered in the grid
    discoveredTemperatures = []

    # If the function is required to find hot squares
    if extreme == "Hot":
        # Sets the find temp fucntion appropriately
        find_temperature = find_hot_temperature
    # Conversely, if the function is required to find cold squares
    else:
        # Sets the find temp fucntion appropriately
        find_temperature = find_cold_temperature

    # Iterates throuhg grid squares in grid
    for y in range(environmentGrid.shape[0]):
        for x in range(environmentGrid.shape[1]):
            # Stores state of square
            square = environmentGrid[y,x]
            # Determines temperature of square to be stored
            temperature = find_temperature(square)
            # Pushes grid square and its temperature onto the heap
            heapq.heappush(discoveredTemperatures, (temperature, (int(x),int(y))))
    
    # While there are grid squares with discovered temperatures left in the list
    while discoveredTemperatures:
        # Pop the grid square with the hottest or coldest tempertaure
        x, y = heapq.heappop(discoveredTemperatures)[1]
        # If the grid square is empty, return this square and end the loop
        if not populationGrid[y,x]:
            return (x,y)
    # If no grid squares with discovered temperatures are left, return nothing
    return None

def find_healthiest_mate(populationGrid, localAgentPos, faunaClass, findAdjacentEmptySquare = False):
    # Sets agent's position in the grid to none - so that it does not consider itself as a potential mate
    populationGrid[localAgentPos[1], localAgentPos[0]] = None
    # Declares list for storing potential mates discovered in the grid
    potentialMates = []
    # Iterations through the squares in the grid
    for y in range(populationGrid.shape[0]):
        for x in range(populationGrid.shape[1]):
            # Stores the state of the grid square
            square = populationGrid[y,x]
            # If square is an animal
            if isinstance(square, faunaClass):
                # Determines important factors regarding the potential mate's state
                health, lifespan, reproducing = square.evaluate_health(), square.lifespan, square.reproducing
                # Adds to potential mates list if potential mate is healthy and old enough and not currently reproducing
                if health > 50 and lifespan >= 2250 and not reproducing:
                    heapq.heappush(potentialMates, (100 - health, (int(x),int(y))))
    
    # If there are values in the potential mates list
    if potentialMates:
        # If the function is required to find an adjacent mpty grid square
        if findAdjacentEmptySquare:
            # Determines closest square adjacent to healthiest potential mate and square of potential mate
            adjacentEmptySquare, square = find_adjacent_empty_squares(potentialMates, populationGrid, localAgentPos, returnOriginalSquare = True)
            # If adjacent empty grid square has been found
            if adjacentEmptySquare:
                return adjacentEmptySquare, square
        # Returns square healthiest potential mate if function is not required to find adjacent empty grid square
        else:
            square = heapq.heappop(potentialMates)[1]
            return square, square
    # As function is expected to return two return values, two nones are returned so that they can be unpacked, if no satisfactory mate is found
    return None, None
    

