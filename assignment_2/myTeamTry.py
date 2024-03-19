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
import MCTS as mc

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

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveAgent', second = 'DefensiveAgent'):
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

NUM_SIMULATIONS = 1000  # Adjust as needed

class OffensiveAgent(CaptureAgent):
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        foodList = self.getFood(successor).asList()
        features['successorScore'] = -len(foodList)

        if len(foodList) > 0:
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        visibleEnemies = [a for a in enemies if not a.isPacman() and a.getPosition() is not None]
        if len(visibleEnemies) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in visibleEnemies]
            features['distanceToGhost'] = min(dists)

        visiblePacmen = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
        if len(visiblePacmen) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in visiblePacmen]
            features['distanceToPacman'] = min(dists)

        capsules = self.getCapsules(successor)
        if len(capsules) > 0:
            dists = [self.getMazeDistance(myPos, c) for c in capsules]
            features['distanceToCapsule'] = min(dists)

        walls = gameState.getWalls()
        height, width = walls.height, walls.width
        x, y = int(myPos[0]), int(myPos[1])
        distancesToBorders = [x, width - x, y, height - y]
        features['distanceToBorders'] = min(distancesToBorders)

        return features

    def chooseAction(self, gameState):
        mctsAgent = mc.MCTSAgent(index=self.index)
        best_action = mctsAgent.chooseAction(gameState, agent=self)
        return best_action

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
        #root = Node(gameState, self, action=None, parent=None)

        """ for _ in range(NUM_SIMULATIONS):
            selected_node = root.select()
            expanded_node = selected_node.expand()
            simulation_result = expanded_node.simulate()
            expanded_node.backpropagate(simulation_result """

        mctsAgent = mc.MCTSAgent(index=self.index)
        best_action = mctsAgent.chooseAction(gameState, agent=self)
        return best_action

    
