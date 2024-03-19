from captureAgents import CaptureAgent
from capture import GameState
import random, time, util
from game import Directions
import game
import numpy as np

import math
import random

class Node:
    def __init__(self, gamestate, agent, action, parent=None):
        # by default, nodes are initialised as leaves and as non-terminal states
        self.leaf = True
        self.is_terminal = False
        
        self.state = gamestate.deepCopy()
        self.parent = parent
        self.action = action
        self.children = []
        self.legalActions = [act for act in gamestate.getLegalActions(agent.index) if act != 'Stop']
        self.unexploredActions = self.legalActions[:]
        self.visits = 0
        self.total_score = 0
        self.depth = 0 if parent is None else parent.depth + 1
        self.agent = agent
    
    def is_leaf(self):
        return len(self.children) == 0
    
    def is_fully_expanded(self):
        return len(self.children) == len(self.legalActions)
    
    def add_child(self, child): # da capire
        self.children.append(child)
    
    def select_child(self):
        exploration_factor = 1.4  # Adjust this parameter as needed
        best_child = None
        best_score = float('-inf')
        
        for child in self.children:
            exploitation = child.total_score / child.visits if child.visits != 0 else 0
            exploration = math.sqrt(math.log(self.visits) / child.visits) if child.visits != 0 else float('inf')
            score = exploitation + exploration * exploration_factor
            if score > best_score:
                best_score = score
                best_child = child
        
        return best_child
    

    def get_best_action(self): # da capire
        best_child = max(self.children, key=lambda x: x.visits)
        return best_child.action #best_child.state.last_action
    
    def get_Rewards(self):
        current_pos = self.state.getAgentPosition(self.agent.index)
        if current_pos == self.state.getInitialAgentPosition(self.agent.index):
            reward = -100
        else:
            reward = self.get_features() * self.get_weights()
        return reward
    
        
    def get_features(self):
        state = self.state
        if self.agent == 'pacman':
            features = util.Counter()
            successor = state.getSuccessor(state, self.action)
            foodList = self.getFood(successor).asList()    
            features['successorScore'] = -len(foodList)#self.getScore(successor)

            # Compute distance to the nearest food

            if len(foodList) > 0: # This should always be True,  but better safe than sorry
                myPos = successor.getAgentState(self.index).getPosition()
                minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
                features['distanceToFood'] = minDistance
                return features
        else:
            features = util.Counter()
            successor = state.generateSuccessor(state, self.action)
            # Computes distance to invaders we can see
            enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
            features['numInvaders'] = len(invaders)
            if len(invaders) > 0:
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                features['invaderDistance'] = min(dists)

                if self.action == Directions.STOP: features['stop'] = 1
                rev = Directions.REVERSE[self.state.getAgentState(self.index).configuration.direction]
                if self.action == rev: features['reverse'] = 1

                return features

    def get_weights(self):
        if self.agent == 'pacman':
            return {'successorScore': 100, 'distanceToFood': -1}
        else:
            return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
        
    

class MCTSAgent(CaptureAgent):
    def chooseAction(self, gameState, agent):
        num_iterations = 1000  # Adjust this parameter as needed
        root = Node(gameState, agent, action = None, parent=None)
        
        for _ in range(num_iterations):
            selected_node = self.select(root)
            expanded_node = self.expand(selected_node)
            simulation_result = self.simulate(expanded_node)
            self.backpropagate(expanded_node, simulation_result)
        
        best_action = root.get_best_action()
        return best_action
    
    def select(self, node):
        node_selected = node
        while not node.is_leaf():
            if not node.is_fully_expanded():
                return node.expand()
            else:
                node_selected = node.select_child()
        return node_selected
    
    def expand(self, node):
        current_state = node.state.deepCopy()
        actions = node.unexploredActions
        random_action = random.choice(actions)
        node.unexploredActions.remove(random_action)
        new_state = current_state.generateSuccessor(node.agent.index, random_action)
        child_node = Node(new_state, agent = node.agent, action = random_action, parent=None)
        node.add_child(child_node)
        return child_node
    
    def simulate(self, node):
        state = node.state.deepCopy()
        reward = 0
        while not node.is_terminal:

            random_action = random.choice(node.legalActions)

            state = state.generateSuccessor(node.agent.index, random_action)

            node = Node(state, agent = node.agent, action = random_action, parent=node)

            reward += node.get_Rewards()

        return reward
    
    def backpropagate(self, node, score):
        while node is not None:
            node.visits += 1
            node.total_score += score
            node = node.parent




