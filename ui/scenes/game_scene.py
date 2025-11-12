import pygame
from .scene import Scene
from ui.components import CheckboxWithLabel, Dropdown, Button, EvalBar
from ui.views import BoardView
from ui.config import DEFAULT_FONT
from game.board import Board
from ai.random_agent import RandomAgent
from ai.minimax_agent import MinimaxAgent
from ai.eval import simple_eval
from utils.cell import Cell

class GameScene(Scene):
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.agent1 = None
        self.agent2 = None
        self.board = Board()
        self.show_eval = True

        self.eval_bar = EvalBar(50, 50, 400, 30)
        self.board_view = BoardView(self.board, pos=(50, 150), size=400)       
        self.show_eval_checkbox = CheckboxWithLabel(500, 150, 32, "Show Evaluation", DEFAULT_FONT, checked=self.show_eval,
                                                    on_toggle=self.set_show_eval)
        
        self.p1_surf = DEFAULT_FONT.render("P1 (X):", True, (0, 0, 0))
        self.p1_rect = self.p1_surf.get_rect(left=500, centery=200+self.p1_surf.height//2)
        self.p1_dropdown = Dropdown((580, 200, 200, 40), ["none", "random", "minimax", "mcts"], DEFAULT_FONT,
                                    on_select=self.change_agent1)
        
        self.p2_surf = DEFAULT_FONT.render("P2 (O):", True, (0, 0, 0))
        self.p2_rect = self.p2_surf.get_rect(left=500, centery=250+self.p2_surf.height//2)
        self.p2_dropdown = Dropdown((580, 250, 200, 40), ["none", "random", "minimax", "mcts"], DEFAULT_FONT,
                                    on_select=self.change_agent2)
        
        self.new_game_button = Button((500, 505, 150, 40), "New Game", DEFAULT_FONT,
                                      on_click=self.new_game)
        self.back_button = Button((670, 505, 100, 40), "Back", DEFAULT_FONT,
                                  on_click=lambda: self.back(screen, manager)) 
    
    def back(self, screen, manager):
        from .menu_scene import MenuScene
        manager.set_scene(MenuScene(screen, manager))

    def set_show_eval(self, show:bool):
        self.show_eval = show
    
    def new_game(self):
        self.board = Board()
        self.board_view = BoardView(self.board, pos=(50, 150), size=400)
    
    def change_agent1(self, agent_type:str):
        if agent_type == "none":
            self.agent1 = None
        elif agent_type == "random":
            self.agent1 = RandomAgent()
        elif agent_type == "minimax":
            self.agent1 = MinimaxAgent(simple_eval)
        # elif agent_type == "mcts":
        #     self.agent1 = MCTSAgent()

    def change_agent2(self, agent_type:str):
        if agent_type == "none":
            self.agent2 = None
        elif agent_type == "random":
            self.agent2 = RandomAgent()
        elif agent_type == "minimax":
            self.agent2 = MinimaxAgent(simple_eval)
        # elif agent_type == "mcts":
        #     self.agent2 = MCTSAgent()

    def handle_event(self, event):
        self.show_eval_checkbox.handle_event(event)
        self.p1_dropdown.handle_event(event)
        self.p2_dropdown.handle_event(event)
        self.board_view.handle_event(event)
        self.new_game_button.handle_event(event)
        self.back_button.handle_event(event)

    def update(self):
        if not self.board.is_terminal() and self.agent1 is not None and self.board.to_move == Cell.X:
            move = self.agent1.choose_move(self.board.copy())
            if move is not None:
                self.board.make_move(*move)
        if not self.board.is_terminal() and self.agent2 is not None and self.board.to_move == Cell.O:
            move = self.agent2.choose_move(self.board.copy())
            if move is not None:
                self.board.make_move(*move)
        self.board_view.update()
        self.new_game_button.update()
        self.back_button.update()

    def draw(self):
        self.screen.fill((255, 255, 255))
        if self.show_eval:
            self.eval_bar.draw(self.screen)
        self.board_view.draw(self.screen)
        self.show_eval_checkbox.draw(self.screen)
        self.new_game_button.draw(self.screen)
        self.back_button.draw(self.screen)
        self.screen.blit(self.p1_surf, self.p1_rect)
        self.screen.blit(self.p2_surf, self.p2_rect)
        self.p2_dropdown.draw(self.screen)
        self.p1_dropdown.draw(self.screen)
