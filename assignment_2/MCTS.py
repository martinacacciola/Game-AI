from captureAgents import CaptureAgent
from capture import GameState
import random, time, util
from game import Directions
import game
import numpy as np
from util import nearestPoint
import copy

import math
import random
import sys
#python capture.py -r baselineTeam -b myTeamTry

class Node:
    def __init__(self, gamestate, agent, action, state = None, parent=None, root=False):
        # by default, nodes are initialised as leaves and as non-terminal states
        self.leaf = True
        self.is_terminal = False
        self.root = root

        self.gamestate = gamestate.deepCopy()
        self.parent = parent
        self.action = action
        self.children = []
        self.agent = agent
        self.index = agent.index
        if state is None:
            self.state = self.gamestate.getAgentPosition(self.index)
        else:
            self.state = state
        self.legalActions = self.gamestate.getLegalActions(self.index)
        self.unexploredActions = copy.deepcopy(self.legalActions)
        self.visits = 1
        self.total_score = 0
        self.depth = 0 if parent is None else parent.depth + 1
        
    def is_leaf(self):
        return len(self.children) == 0
    
    def is_fully_expanded(self):
        return len(self.children) == len(self.legalActions)
    
    def add_child(self, child): # da capire
        self.children.append(child)
    
    def select_child(self):
        #exploration_factor = 1.4  # Adjust this parameter as needed
        exploration_factor = 2.5
        best_child = None
        best_score = float('inf')
        
        for child in self.children:
            exploitation = child.total_score / child.visits if child.visits != 0 else 0
            exploration = math.sqrt(math.log(self.visits) / child.visits) if child.visits != 0 else float('-inf')
            score = exploitation + exploration * exploration_factor
            if score < best_score:
                best_score = score
                best_child = child

        
        return best_child
    

    def get_best_action(self): # da capire
        best_child = max(self.children, key=lambda x: x.visits)    
        return best_child.action #best_child.state.last_action
    
        
    def get_Rewards(self,action=None, pacman=False):
        current_pos = self.gamestate.getAgentPosition(self.index)
        if current_pos == self.gamestate.getInitialAgentPosition(self.index):
            reward = 1000
        else:
            reward = self.get_features(action=None, pacman=pacman)

            # Check if Pacman agent reached a power capsule on the enemy field
            if pacman and self.agent.is_over_half(current_pos, self.gamestate) and self.reached_power_capsule(current_pos):
                reward += 500  # Reward for reaching power capsule on the enemy field
    
        return reward
    
        
    def get_features(self,action=None, pacman=False):
        our_location = self.agent.find_self(self.gamestate)
        if pacman == True: # we are pacman
            successor = self.agent.difference_after_movement(our_location, action)
            food_list = self.find_food(self.gamestate)
            closest_food_dist = self.closest_food_distance(successor, food_list)
            closest_opponent_dist = self.closest_opponent_distance(successor, self.find_opponents(self.gamestate))
            if successor in food_list:
                action_value = -1000
                return action_value
            elif successor in self.find_opponents(self.gamestate):
                action_value = 1000
                return action_value
            else:
                action_value = 3*closest_food_dist - closest_opponent_dist
            return action_value

        else:
            successor = self.agent.difference_after_movement(our_location, action)
            foodList = self.find_food(self.gamestate)    
            closest_opponent, closest_food = self.closest_opponent_to_food(foodList, self.find_opponents(self.gamestate))
            if successor in self.find_opponents(self.gamestate):
                action_value = 1000
                return action_value
            elif successor in foodList:
                action_value = -500
                return action_value
            else:
                action_value = self.agent.getMazeDistance(successor, closest_opponent) - 0.2 * self.agent.getMazeDistance(successor, closest_food)
            return action_value
        
    def find_food(self, gameState):
        """
        Finds the location of all our food pallets in the game
        @param gameState: the current game state
        @return: a list of all the food pallets in the game
        """
        food_locations = []

        food = self.agent.getFood(gameState)
        x = 0
        for row in food:
            y = 0
            for cel in row:
                if cel:
                    food_locations.append((x, y))
                y += 1
            x += 1
        
        return food_locations
    
    def reached_power_capsule(self, position):
        """
        Checks if the Pacman agent has reached a power capsule located on the enemy field.
        @param position: The position of the Pacman agent.
        @return: True if the Pacman agent has reached a power capsule on the enemy field, False otherwise.
        """
        capsules = self.agent.getCapsules(self.gamestate)
        for capsule in capsules:
            if self.agent.is_over_half(capsule, self.gamestate) and position == capsule:
                return True
        return False
    
    def find_opponents(self, gameState):
        """
        Finds the location of all the opponents in the game
        @param gameState: the current game state
        @return: a list of all the opponents in the game
        """
        opponents = []
        opponent_index = self.agent.getOpponents(gameState)
        for index in opponent_index:
            opponents.append(gameState.getAgentPosition(index))

        return opponents
    
    def closest_opponent_to_food(self, food_locations, opponents_location):
        min_distance = float('inf')
        closest_opponent = None
        closest_food = None
        for food_loc in food_locations:
            for opp_loc in opponents_location:
                dist = self.agent.getMazeDistance(food_loc, opp_loc)
                if dist < min_distance:
                    min_distance = dist
                    closest_opponent = opp_loc
                    closest_food = food_loc
        return closest_opponent, closest_food
    
    def closest_food_distance(self, our_location, food_locations):
        min_distance = float('inf')
        for food_loc in food_locations:
            dist = self.agent.getMazeDistance(our_location, food_loc)
            if dist < min_distance:
                min_distance = dist
        return min_distance

    def closest_opponent_distance(self, our_location, opponents_location):
        min_distance = float('inf')
        for opp_loc in opponents_location:
            dist = self.agent.getMazeDistance(our_location, opp_loc)
            if dist < min_distance:
                min_distance = dist
        return min_distance
    


class MCTSAgent(CaptureAgent):
    def __init__(self, index, **kwargs):
        super().__init__(index, **kwargs)
        self.food_eaten = 0  # Initialize the number of food pellets eaten by Pacman

    def chooseAction(self, gameState, pacman = False):

        num_iterations = 10  # Adjust this parameter as needed
        root = Node(gameState, agent=self, action = None, state = None, parent=None, root = True)
        self.pacman = pacman
        
        for _ in range(num_iterations):

            print("index: {}".format(self.index))
            selected_node = self.select(root)
            expanded_node = self.expand(selected_node)
            simulation_result = self.simulate(expanded_node)
            self.backpropagate(expanded_node, simulation_result)
        
           
        best_action = root.get_best_action()
        print("best action: {}".format(best_action))
        return best_action
    
    def select(self, node):
        node_selected = node
        while not node.is_leaf():
            if not node.is_fully_expanded():
                return self.expand(node)
            else:
                node_selected = node.select_child()
                break
        return node_selected
    
    def expand(self, node):
        if node.is_terminal:
            return node
        actions = node.unexploredActions
        if actions == []:
            return node
        random_action = random.choice(actions)
        node.unexploredActions.remove(random_action)
        new_state = self.difference_after_movement(node.gamestate.getAgentPosition(self.index), random_action)
        new_gamestate = node.gamestate.generateSuccessor(self.index, random_action)
        child_node = Node(gamestate = new_gamestate, state = new_state, agent = self, action = random_action, parent=node)
        node.add_child(child_node)
        return child_node
    

    def simulate(self, node):
        current_node = node
        total_reward = 0
        max_steps = 15
        steps = 0

        while steps < max_steps and not current_node.is_terminal:

            random_action = random.choice(current_node.legalActions)
            print("random action: {}".format(random_action))
            new_state = self.difference_after_movement(current_node.gamestate.getAgentPosition(self.index), random_action)
            new_gamestate = current_node.gamestate.generateSuccessor(self.index, random_action)
            current_node = Node(gamestate=new_gamestate, state=new_state, agent=node.agent, action=random_action, parent=current_node)
            reward = current_node.get_Rewards(action=random_action, pacman=self.pacman)
            
            # Update total_reward based on the reward obtained from the current action
            total_reward += reward
            
            # If Pacman collected food and returned to its original side, gain points
            if reward > 0 and self.is_over_half(new_state, new_gamestate):
                food_collected = self.getFoodEaten(new_gamestate)
                score_increment = food_collected * 1  # Each food pellet is worth 1 points
                total_reward += score_increment
                print("Pacman returned with {} food pellets, gained {} points.".format(food_collected, score_increment))
            
            steps += 1
            print("total reward: {}".format(total_reward))

        return total_reward


    def backpropagate(self, node, score):
        current_node = node 
        i = 0
        while current_node.root is False and i < 100:
            current_node.visits += 1
            current_node.total_score += score
            current_node = current_node.parent
            i += 1
            
    def is_over_half(self, position, gameState):
        """
        Checks if the agent is over the half of the board
        @param position: the position of the agent
        @param gameState: the current game state
        @return: True if the agent is over the half of the board, False otherwise
        """
        food = self.getFood(gameState)
        if self.red:
            if position[0] <= len(food[0])-1:
                return False
            else:
                return True
        else:
            if position[0] >= len(food[0]):
                return False
            else:
                return True

    def difference_after_movement(self, pos1, action):
        if action == "North":
            return (pos1[0], pos1[1] + 1)
        elif action == "South":
            return (pos1[0], pos1[1] - 1)
        elif action == "East":
             return (pos1[0] + 1, pos1[1])
        elif action == "West":
            return (pos1[0] - 1, pos1[1])
        else:
            return pos1

    def find_self(self, gameState):
        """
        Finds the location of our agent in the game
        @param gameState: the current game state
        @return: the location of our agent
        """
        return gameState.getAgentPosition(self.index)

    def getFoodEaten(self, gameState):
        """
        Returns the number of food pellets eaten by the agent
        @param gameState: the current game state
        @return: the number of food pellets eaten by the agent
        """
        return gameState.data.agentStates[self.index].numCarrying
       


