import concurrent.futures
import threading
import time
import pygame
from .scene import Scene
from ai.agent import Agent
from ui.config import DEFAULT_FONT
from ui.components import WinLossBar
from game.board import Board
from game.cell import Cell

class ComparingScene(Scene):
    def __init__(self, screen, manager, agent1_name:str, agent2_name:str,
                 agent1:Agent, agent2:Agent, num_games:int=1000, num_threads:int=4):
        self.screen = screen
        self.manager = manager
        self.num_games = num_games
        self.agent1 = agent1
        self.agent2 = agent2
        self.num_threads = num_threads

        self.running = True
        self.lock = threading.Lock()
        self.results = {"win": 0, "loss": 0, "draw": 0}
        self.games_played = 0
        
        self.title_surf = pygame.font.SysFont("Berlin Sans FB", 36).render("Comparing...", True, (0, 0, 0))
        self.title_rect = self.title_surf.get_rect(left=50, top=50)
        self.agent_names_surf = DEFAULT_FONT.render(f"{agent1_name} vs {agent2_name}", True, (0, 0, 0))
        self.agent_names_rect = self.agent_names_surf.get_rect(left=50, top=self.title_rect.bottom+50)
        self.win_loss_bar = WinLossBar(50, self.agent_names_rect.bottom+20, 400, 50, pygame.font.SysFont("Calibri", 16))
        self.games_played_label_surf = DEFAULT_FONT.render(f"Games played: {self.games_played} / {self.num_games}", True, (0, 0, 0))
        self.games_played_label_rect = self.games_played_label_surf.get_rect(left=50, top=self.win_loss_bar.rect.bottom+20)

        self.thread = threading.Thread(target=self.run_simulations, daemon=True)
        self.thread.start()
    
    def run_simulations(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [executor.submit(self.simulate_game) for _ in range(self.num_games)]

            for future in concurrent.futures.as_completed(futures):
                if not self.running:
                    break
                winner = future.result()
                with self.lock:
                    if winner == Cell.X:
                        self.results['win'] += 1
                    elif winner == Cell.O:
                        self.results['loss'] += 1
                    else:
                        self.results["draw"] += 1
                    self.games_played += 1

    def simulate_game(self):
        board = Board()
        while not board.is_terminal():
            agent = self.agent1 if board.to_move == Cell.X else self.agent2
            move = agent.choose_move(board)
            board.make_move(*move)
        time.sleep(0.1)
        return board.winner
    
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

    def update(self):
        self.win_loss_bar.set_results(self.results['win'], self.results['draw'], self.results['loss'])
        self.win_loss_bar.update()
        self.games_played_label_surf = DEFAULT_FONT.render(f"Games played: {self.games_played} / {self.num_games}", True, (0, 0, 0))
    
    def draw(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.title_surf, self.title_rect)
        self.screen.blit(self.agent_names_surf, self.agent_names_rect)
        self.win_loss_bar.draw(self.screen)
        self.screen.blit(self.games_played_label_surf, self.games_played_label_rect)
