from typing import List, Tuple
import random
import math

class GameState:
    def __init__(self, board: Tuple[Tuple[int]], player: int) -> None:
        self.__keys = tuple(hash(plane) for plane in board)
        self.__player: int = player
        self.__width = len(board)
        self.__board = board
        self.__moves: Tuple[int] = self.__get_moves()
        self.__util: int = self.__get_util()
        self.__move: int = -1

    def __iter_lines(self):
        for single in self.__board:
            for i in range(0, len(single), self.__width):
                yield single[i:i + self.__width]
            for i in range(self.__width):
                yield single[i::self.__width]
            yield single[::self.__width + 1]
            yield single[self.__width - 1:len(single) - 1:self.__width - 1]
        for i in range(self.__width ** 2):
            yield tuple(single[i] for single in self.__board)
        for j in range(self.__width):
            yield tuple(self.__board[i][j * self.__width + i] 
                        for i in range(len(self.__board)))
            yield tuple(self.__board[i][(j + 1) * self.__width - 1 - i]
                        for i in range(len(self.__board)))
            yield tuple(self.__board[i][j + i * self.__width] 
                        for i in range(len(self.__board)))
            yield tuple(self.__board[i][-j - 1 - i * self.__width]
                        for i in range(len(self.__board)))
        yield tuple(self.__board[i][i * self.__width + i] 
                    for i in range(len(self.__board)))
        yield tuple(self.__board[i][i * self.__width + self.__width - 1 - i]
                    for i in range(len(self.__board)))
        yield tuple(self.__board[i][self.__width ** 2 - 
                    self.__width * (i + 1) + i]
                    for i in range(len(self.__board)))
        yield tuple(self.__board[i][self.__width ** 2 - 
                    (i * self.__width) - i - 1]
                    for i in range(len(self.__board)))

    def get_board(self):
        return self.__board

    def __get_util(self):
        for line in self.__iter_lines():
            if line == (1,) * self.__width:
                return 1
            if line == (-1,) * self.__width:
                return -1
        return 0 if len(self.__moves) == 0 else None

    def __get_moves(self):
        return tuple(j + i * self.__width ** 2 for i, single in
                enumerate(self.__board) for j, square in enumerate(single)
                if square == 0)

    def __eq__(self, other):
        return self.__keys == other.__keys

    def __hash__(self):
        return hash(self.__keys)

    def __repr__(self):
        display = "\n"
        for i in range(self.__width):
            for j in range(self.__width):
                line = self.__board[j][i * self.__width:(i + 1) * self.__width]
                start = j * self.__width ** 2 + i * self.__width
                for k, space in enumerate(line):
                    if space == 0:
                        space = start + k
                    else:
                        space = ("X" if space == 1
                                 else "O" if space == -1
                                 else "-")
                    display += "{0:>4}".format(space)
                display += " " * self.__width
            display += "\n"
        return display

    def get_util(self):
        return self.__util

    def get_move(self):
        return self.__move

    def set_move(self, move):
        self.__move = move

    def get_moves(self):
        return self.__moves

    def get_player(self):
        return self.__player

    def traverse(self, index: int):
        i, j = index // self.__width ** 2, index % self.__width ** 2
        single = self.__board[i][:j] + (self.__player,) + \
            self.__board[i][j + 1:]
        return GameState(self.__board[:i] + (single,) + self.__board[i + 1:],
            -self.__player)

class MCTS_Node:
    C = math.sqrt(2)
    def __init__(self, state, parent) -> None:
        self.__expanded = False
        self.__parent = parent
        
        self.__children = []
        self.__state = state
        self.__attempts = 0
        self.__score = 0.0

    def get_util(self):
        return self.__state.get_util()

    def get_parent(self):
        return self.__parent

    def expand_node(self):
        if not self.__expanded:
            for ind in self.__state.get_moves():
                new_node = MCTS_Node(self.__state.traverse(ind), self)
                self.__children.append(new_node)
            self.__expanded = True

    def get_win_ratio(self):
        if self.__attempts == 0:
            return 0
        return self.__score/self.__attempts

    def get_ucb_score(self, total):
        if total == 0:
            return self.get_win_ratio()
        if self.__attempts == 0:
            return self.C
        exploit = self.get_win_ratio()
        explore = math.sqrt(math.log(total)/self.__attempts)
        return exploit + self.C * explore

    def play_best_move(self):
        if not self.__expanded:
            self.expand_node()
        best_move = None
        for ind, node in enumerate(self.__children):
            ucb = node.get_ucb_score(self.__attempts)
            if node.__attempts == 0:
                best_move = [ucb, [ind]]
                break
            if best_move is None or ucb > best_move[0]:
                best_move = [ucb, [ind]]
            elif ucb == best_move[0]:
                best_move[1].append(ind)
        move = random.choice(best_move[1])
        return self.__children[move]

    def play_random_move(self):
        move = random.choice(self.__state.get_moves())
        return MCTS_Node(self.__state.traverse(move), self)

    def update_selection(self):
        selection = (-1, -1)
        if self.is_expanded:
            selection = None
            move_list = self.__state.get_moves()
            for ind, child_node in enumerate(self.__children):
                pos = move_list[ind]
                win_ratio = child_node.get_win_ratio()
                if selection is None or win_ratio > selection[1]:
                    selection = (pos, win_ratio)
        self.__state.set_move(selection[0])

    def update_score(self, winner, player):
        self.__attempts += 1
        if winner == 0:
            self.__score += 0.5
        elif winner == player:
            self.__score += 1.0

    def is_expanded(self):
        return self.__expanded
        

class MCTS:
    @staticmethod
    def get_next_move(state, iteration_count=1000):
        player = state.get_player()
        root = MCTS_Node(state, None)
        for _ in range(iteration_count):
            node = MCTS.select_node(root)
            if node.get_util() is None:
                node = MCTS.expand_frontier(node)
                node = MCTS.simulate_playout(node)
            MCTS.backpropogate(node, player)
            root.update_selection()
        if state.get_move() == -1:
            return random.choice(state.get_moves())
        return state.get_move()

    @staticmethod
    def select_node(node) -> MCTS_Node:
        while node.is_expanded():
            node = node.play_best_move()
        return node

    @staticmethod
    def expand_frontier(node) -> MCTS_Node:
        node.expand_node()
        return node.play_best_move()

    @staticmethod
    def simulate_playout(node) -> MCTS_Node:
        while node.get_util() is None:
            node = node.play_random_move()
        return node

    @staticmethod
    def backpropogate(node, root_player) -> None:
        winner = node.get_util()
        while node is not None:
            node.update_score(winner, root_player)
            node = node.get_parent()
