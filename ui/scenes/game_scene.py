import pygame
from .scene import Scene
from ui.components import CheckboxWithLabel, Dropdown, Button, EvalBar
from ui.views import BoardView
from ui.config import DEFAULT_FONT, SMALL_FONT
from game.board import Board
from game.cell import Cell
from ai import AiManager, RandomAgent, MinimaxAgent, MctsAgent, MctsValueAgent
from ai.eval import simple_eval, complex_eval
from utils.utils import decode_move, save_game

class GameScene(Scene):
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.agent1 = None
        self.agent2 = None
        self.board = Board()
        self.show_eval = True

        self.to_move = self.board.to_move
        self.ai_manager = AiManager(self.board, MinimaxAgent(complex_eval, time_limit=0.1))
        self.ai_manager.start()

        self.eval_bar = EvalBar(50, 50, 400, 30)
        self.board_view = BoardView(self.board, pos=(50, 150), size=400)       
        self.show_eval_checkbox = CheckboxWithLabel(500, 150, 32, "Show Evaluation (P1)", DEFAULT_FONT, checked=self.show_eval,
                                                    on_toggle=self.set_show_eval)
        
        self.p1_surf = DEFAULT_FONT.render("P1 (X):", True, (0, 0, 0))
        self.p1_rect = self.p1_surf.get_rect(left=500, centery=220)
        self.p1_dropdown = Dropdown((580, 200, 200, 40), 
                                    ["none", "random", "minimax_simple", "minimax_complex",
                                     "mcts_random", "mcts_heuristic", "mcts_learning"],
                                    DEFAULT_FONT, on_select=self.change_agent1)
        
        self.p2_surf = DEFAULT_FONT.render("P2 (O):", True, (0, 0, 0))
        self.p2_rect = self.p2_surf.get_rect(left=500, centery=270)
        self.p2_dropdown = Dropdown((580, 250, 200, 40), 
                                    ["none", "random", "minimax_simple", "minimax_complex",
                                     "mcts_random", "mcts_heuristic", "mcts_learning"],
                                    DEFAULT_FONT, on_select=self.change_agent2)
        
        self.new_game_button = Button((500, 445, 150, 40), "New Game", DEFAULT_FONT,
                                      on_click=self.new_game)
        self.save_game_button = Button((500, 505, 150, 40), "Save Game", DEFAULT_FONT,
                                      on_click=self.check_and_save_game)
        self.back_button = Button((670, 505, 100, 40), "Back", DEFAULT_FONT,
                                  on_click=lambda: self.back(screen, manager))
        
        self.save_game_warning = False
        self.save_game_surf = SMALL_FONT.render("*Only complete games can be saved.", True, (200, 0, 0))
        self.save_game_rect = self.save_game_surf.get_rect(left=self.save_game_button.rect.x,
                                                           top=self.save_game_button.rect.bottom+5)
    
    def check_and_save_game(self):
        if self.board.is_terminal():
            save_game(self.board)
        else:
            self.save_game_warning = True

    def back(self, screen, manager):
        self.ai_manager.stop()
        from .menu_scene import MenuScene
        manager.set_scene(MenuScene(screen, manager))

    def set_show_eval(self, show:bool):
        self.show_eval = show
        self.ai_manager.update_board(self.board)
    
    def new_game(self):
        self.board = Board()
        self.board_view = BoardView(self.board, pos=(50, 150), size=400)
    
    def change_agent1(self, agent_type:str):
        if agent_type == "none":
            self.agent1 = None
        elif agent_type == "random":
            self.agent1 = RandomAgent()
        elif agent_type == "minimax_simple":
            self.agent1 = MinimaxAgent(simple_eval)
        elif agent_type == "minimax_complex":
            self.agent1 = MinimaxAgent(complex_eval)
        elif agent_type == "mcts_random":
            self.agent1 = MctsAgent(use_heuristic=False)
        elif agent_type == "mcts_heuristic":
            self.agent1 = MctsAgent(use_heuristic=True)
        elif agent_type == "mcts_learning":
            self.agent1 = MctsValueAgent()

    def change_agent2(self, agent_type:str):
        if agent_type == "none":
            self.agent2 = None
        elif agent_type == "random":
            self.agent2 = RandomAgent()
        elif agent_type == "minimax_simple":
            self.agent2 = MinimaxAgent(simple_eval)
        elif agent_type == "minimax_complex":
            self.agent2 = MinimaxAgent(complex_eval)
        elif agent_type == "mcts_random":
            self.agent2 = MctsAgent(use_heuristic=False)
        elif agent_type == "mcts_heuristic":
            self.agent2 = MctsAgent(use_heuristic=True)
        elif agent_type == "mcts_learning":
            self.agent2 = MctsValueAgent()

    def handle_event(self, event):
        self.show_eval_checkbox.handle_event(event)
        self.p1_dropdown.handle_event(event)
        self.p2_dropdown.handle_event(event)
        self.board_view.handle_event(event)
        self.save_game_button.handle_event(event)
        self.new_game_button.handle_event(event)
        self.back_button.handle_event(event)

    def update(self):
        if self.board.to_move != self.to_move:
            self.to_move = self.board.to_move
            if self.show_eval:
                self.ai_manager.update_board(self.board)
        
        if not self.board.is_terminal() and self.agent1 is not None and self.board.to_move == Cell.X:
            move = self.agent1.choose_move(self.board.copy())
            if move is not None:
                self.board.make_move(move)
        if not self.board.is_terminal() and self.agent2 is not None and self.board.to_move == Cell.O:
            move = self.agent2.choose_move(self.board.copy())
            if move is not None:
                self.board.make_move(move)

        if self.show_eval:
            analysis = self.ai_manager.get_analysis()
            if analysis:
                score1, line1 = analysis[0]
                line1 = list(map(lambda x: str(decode_move(x)), line1))
                self.eval_bar.set_line1((score1, line1))
                self.eval_bar.set_value(score1)
                if len(analysis) >= 2:
                    score2, line2 = analysis[1]
                    line2 = list(map(lambda x: str(decode_move(x)), line2))
                    self.eval_bar.set_line2((score2, line2))
                else:
                    self.eval_bar.set_line2((0.0, []))

        self.board_view.update()
        self.save_game_button.update()
        self.new_game_button.update()
        self.back_button.update()

    def draw(self):
        self.screen.fill((255, 255, 255))
        if self.show_eval:
            self.eval_bar.draw(self.screen)
        if self.save_game_warning:
            self.screen.blit(self.save_game_surf, self.save_game_rect)
        self.board_view.draw(self.screen)
        self.show_eval_checkbox.draw(self.screen)
        self.save_game_button.draw(self.screen)
        self.new_game_button.draw(self.screen)
        self.back_button.draw(self.screen)
        self.screen.blit(self.p1_surf, self.p1_rect)
        self.screen.blit(self.p2_surf, self.p2_rect)
        self.p2_dropdown.draw(self.screen)
        self.p1_dropdown.draw(self.screen)
