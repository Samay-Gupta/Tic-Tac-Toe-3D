from .ai import GameState, MCTS
import threading
import pygame
import sys

class Player:
    def __init__(self, _id, name, is_ai) -> None:
        self.__ai = is_ai
        self.__id = _id
        self.__name = name
        self.__move = None

    def is_ai(self):
        return self.__ai

    def get_id(self):
        return self.__id

    def set_id(self, _id):
        self.__id = _id

    def get_name(self):
        return self.__name

    def set_move(self, move):
        self.__move = move

    def get_move(self, state):
        move = self.__move
        if self.__ai:
            move = MCTS.get_next_move(state, 5000)
        return move

    def __repr__(self):
        return self.__name
            

class TicTacToe_3D_Game:
    def __init__(self, p1, p2):
        self.__blank_board = tuple(tuple(0 for _ in range(i, i + 16))
                  for i in range(0, 64, 16))
        self.__state = GameState(self.__blank_board, 1)
        self.__turn_count = 0
        self.__players = (p1, p2)
        self.__winner = None
        self.__running = True
        self.__mt = None

    def play(self):
        self.__mt = threading.Thread(target=self.__play)
        self.__running = True
        self.__mt.start()

    def end(self):
        if self.__mt is not None:
            self.__running = False
            self.__mt.join()

    def get_piece(self, board_id, cell_id):
        return self.__state.get_board()[board_id][cell_id]

    def __play(self):
        while self.__running and self.__state.get_util() is None:
            move = None
            player = self.__players[self.__turn_count%2]
            while move is None:
                if not self.__running:
                    return
                move = player.get_move(self.__state)
            player.set_move(None)
            self.__turn_count += 1
            self.__state = self.__state.traverse(move)
        if self.__running:
            self.__winner = self.__state.get_util()

    def play_move(self, ind):
        player = self.__players[self.__turn_count%2]
        if not player.is_ai() and ind in self.__state.get_moves():
            player.set_move(ind)

    def get_player(self, index):
        return self.__players[index]

    def get_current_player_id(self):
        return self.__players[self.__turn_count%2].get_id()

    def get_player_by_id(self, _id):
        for player in self.__players:
            if player.get_id() == _id:
                return player

    def get_winner(self):
        return self.__winner


class TicTacToe_3D:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("3D Tic-Tac-Toe")
        self.__display = pygame.display.set_mode((1920, 1080))
        self.__running = True
        p1 = Player(1, "Sam", False)
        p2 = Player(-1, "AI", True)
        self.__game = TicTacToe_3D_Game(p1, p2)

    def play(self):
        self.__game.play()
        self.render()
        self.__game.end()
        pygame.display.quit()
        sys.exit()

    def render(self):
        font = pygame.font.SysFont("ComicSans",35)
        screen_font = pygame.font.SysFont("ComicSans", 180)
        while self.__running:
            screen = pygame.Surface((1920, 1080))
            screen.fill((255, 255, 255))
            self.trigger_event_handler()
            for i in range(4):
                board = pygame.Surface((480, 480))
                board.fill((255, 255, 255))
                for j in range(1, 4):
                    pygame.draw.line(board, (0, 0, 0), (60 + 90 * j, 60), (60 + 90 * j, 420))
                    pygame.draw.line(board, (0, 0, 0), (60, 60 + 90 * j), (420, 60 + 90 * j))
                    for k in range(16):
                        piece = self.__game.get_piece(i, k)
                        x = k%4
                        y = k//4
                        if piece == -1:
                            pygame.draw.circle(board, (0, 0, 0), (105 + 90 * x, 105 + 90 * y), 30, 1)
                        if piece == 1:
                            pygame.draw.aaline(board, (0, 0, 0), (75 + 90 * x, 75 + 90 * y), (135 + 90 * x, 135 + 90 * y), 1)
                            pygame.draw.aaline(board, (0, 0, 0), (135 + 90 * x, 75 + 90 * y), (75 + 90 * x, 135 + 90 * y), 1)
                pos_x = i * 480
                pos_y = i * 200
                screen.blit(board, (pos_x, pos_y))
            pygame.draw.aaline(screen, (0, 0, 0), (480, 0), (1920, 600))
            pygame.draw.aaline(screen, (0, 0, 0), (0, 480), (1440, 1080))

            active_id = self.__game.get_current_player_id()

            player = self.__game.get_player(0)
            player_text = f"{player.get_name()}: {'X' if player.get_id() == 1 else 'O'}"
            text_obj = font.render(player_text, 1, (0, 0, 0))
            position = text_obj.get_rect()
            position.topright = (1800, 30)
            screen.blit(text_obj, position)
            if (player.get_id() == active_id):
                pygame.draw.line(screen, (0, 0, 0), (position.left, position.bottom + 5), 
                    (position.right, position.bottom + 5))

            player = self.__game.get_player(1)
            player_text = f"{player.get_name()}: {'X' if player.get_id() == 1 else 'O'}"
            text_obj = font.render(player_text, 1, (0, 0, 0))
            position = text_obj.get_rect()
            position.bottomleft = (120, 1050)
            screen.blit(text_obj, position)
            if (player.get_id() == active_id):
                pygame.draw.line(screen, (0, 0, 0), (position.left, position.bottom + 5), 
                    (position.right, position.bottom + 5))

            winner = self.__game.get_winner()
            if winner is not None:
                text = "Tie Game!"
                color = (30, 30, 30)
                if winner == 1:
                    text = "You Won!"
                    color = (0, 255, 0)
                if winner == -1:
                    text = "You Lost!"
                    color = (255, 0, 0)
                text_obj = screen_font.render(text, 100, color)
                position = text_obj.get_rect(center=(920, 540))
                screen.blit(text_obj, position)

            self.__display.blit(screen, (0, 0))
            pygame.display.flip()


    def trigger_event_handler(self):
        self.__event_handler()

    def __event_handler(self):
        if self.__game.get_winner() is not None:
            self.__game.end()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.__mouse_click_handler(mouse_x, mouse_y)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pass
                    #self.__running = False
            if event.type == pygame.KEYUP:
                pass

    def __in_rect(self, x, y, x0, y0, w, h):
        return x0 <= x < x0 + w and y0 <= y < y0 + h
            
    def __mouse_click_handler(self, mouse_x, mouse_y):
        for i in range(4):
            for j in range(16):
                x0 = i * 480 + 60 + 90 * (j%4)
                y0 = i * 200 + 60 + 90 * (j//4)
                if self.__in_rect(mouse_x, mouse_y, x0, y0, 90, 90):
                    self.__game.play_move(16 * i + j)
    
