import math
import random
from captureAgents import CaptureAgent

class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_score = 0
        self.depth = 0 if parent is None else parent.depth + 1
    
    def is_leaf(self):
        return len(self.children) == 0
    
    def is_fully_expanded(self):
        return len(self.children) == len(self.state.getLegalActions())
    
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
    

class MCTSAgent(CaptureAgent):
    def chooseAction(self, gameState):
        num_iterations = 100  # Adjust this parameter as needed
        root = Node(gameState)
        
        for _ in range(num_iterations):
            selected_node = self.select(root)
            expanded_node = self.expand(selected_node)
            simulation_result = self.simulate(expanded_node)
            self.backpropagate(expanded_node, simulation_result)
        
        best_action = root.get_best_action()
        return best_action
    
    def select(self, node):
        while not node.is_leaf():
            if not node.is_fully_expanded():
                return node.expand()
            else:
                node = node.select_child()
        return node
    
    def expand(self, node):
        actions = node.state.getLegalActions()
        random_action = random.choice(actions)
        new_state = node.state.generateSuccessor(self.index, random_action)
        child_node = Node(new_state, parent=node)
        node.add_child(child_node)
        return child_node
    
    def simulate(self, node):
        state = node.state.deep_copy()
        while not state.isGameOver():
            action = random.choice(state.getLegalActions())
            state = state.generateSuccessor(self.index, action)
        return state.getScore()
    
    def backpropagate(self, node, score):
        while node is not None:
            node.visits += 1
            node.total_score += score
            node = node.parent


