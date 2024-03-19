# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from MCTS import Node

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

def createTeamMCTS(firstIndex, secondIndex, isRed,
               first = 'MCTSPacmanAgent', second = 'MCTSGhostAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

NUM_SIMULATIONS = 100

class MCTSAgent(CaptureAgent):
    def __init__(self, index, role, num_simulations=100):
        super().__init__(index)
        self.role = role
        self.num_simulations = num_simulations

    def chooseAction(self, gameState):
        root = Node(state=gameState)

        # Perform MCTS simulations
        for _ in range(self.num_simulations):
            node = root
            state = gameState.deepCopy()

            # Selection phase
            while not node.isTerminal():
                if node.isFullyExpanded():
                    node = node.selectChild()
                else:
                    node = node.expand()
                    break

            # Simulation phase
            simulatedState = state.deepCopy()
            while not simulatedState.isOver():
                action = random.choice(simulatedState.getLegalActions(self.index))
                simulatedState = simulatedState.generateSuccessor(self.index, action)

            # Backpropagation phase
            while node is not None:
                node.update(simulatedState.getScore())
                node = node.parent

        # Choose the action with the highest average value
        bestAction = root.getBestAction()
        return bestAction

class OffensiveAgent(CaptureAgent):
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        foodList = self.getFood(successor).asList()
        features['successorScore'] = -len(foodList)

        # Compute distance to the nearest food
        if len(foodList) > 0:
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        # Avoid enemy ghosts
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        visibleEnemies = [a for a in enemies if not a.isPacman() and a.getPosition() is not None]
        if len(visibleEnemies) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in visibleEnemies]
            features['distanceToGhost'] = min(dists)

        # Chase enemy pacman if nearby
        visiblePacmen = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
        if len(visiblePacmen) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in visiblePacmen]
            features['distanceToPacman'] = min(dists)

        # Consider capsules
        capsules = self.getCapsules(successor)
        if len(capsules) > 0:
            dists = [self.getMazeDistance(myPos, c) for c in capsules]
            features['distanceToCapsule'] = min(dists)

        # Distance to borders
        walls = gameState.getWalls()
        height, width = walls.height, walls.width
        x, y = int(myPos[0]), int(myPos[1])
        distancesToBorders = [x, width - x, y, height - y]
        features['distanceToBorders'] = min(distancesToBorders)

        return features

    def chooseAction(self, gameState):
        root = Node(state=gameState)

        # Perform MCTS simulations
        for _ in range(NUM_SIMULATIONS):
            node = root
            state = gameState.deepCopy()

            # Selection phase
            while not node.isTerminal():
                if node.isFullyExpanded():
                    node = node.selectChild()
                else:
                    node = node.expand()
                    break

            # Simulation phase
            simulatedState = state.deepCopy()
            while not simulatedState.isOver():
                action = self.chooseBestAction(simulatedState)
                simulatedState = simulatedState.generateSuccessor(self.index, action)

            # Backpropagation phase
            while node is not None:
                node.update(simulatedState.getScore())
                node = node.parent

        # Choose the action with the highest average value
        bestAction = root.getBestAction()
        return bestAction

    def chooseBestAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        scores = []
        for action in actions:
            features = self.getFeatures(gameState, action)
            score = features['successorScore']
            if 'distanceToGhost' in features:
                score += 10 / (features['distanceToGhost'] + 1)
            if 'distanceToPacman' in features:
                score += 5 / (features['distanceToPacman'] + 1)
            if 'distanceToCapsule' in features:
                score -= 3 / (features['distanceToCapsule'] + 1)
            if 'distanceToBorders' in features:
                score -= 1 / (features['distanceToBorders'] + 1)
            scores.append(score)

        bestAction = actions[scores.index(max(scores))]
        return bestAction

class DefensiveAgent(CaptureAgent):
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        foodList = self.getFood(successor).asList()
        if len(foodList) > 0:
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        visiblePacmen = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
        if len(visiblePacmen) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in visiblePacmen]
            features['distanceToPacman'] = min(dists)

        walls = gameState.getWalls()
        height, width = walls.height, walls.width
        x, y = int(myPos[0]), int(myPos[1])
        distancesToBorders = [x, width - x, y, height - y]
        features['distanceToBorders'] = min(distancesToBorders)

        return features

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)

        scores = []
        for action in actions:
            features = self.getFeatures(gameState, action)
            score = features['distanceToFood']
            if 'distanceToPacman' in features:
                score -= 5 / (features['distanceToPacman'] + 1)
            if 'distanceToBorders' in features:
                score -= 1 / (features['distanceToBorders'] + 1)
            scores.append(score)

        bestAction = actions[scores.index(max(scores))]
        return bestAction

    
