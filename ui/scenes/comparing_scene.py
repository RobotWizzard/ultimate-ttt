from multiprocessing import Process, Queue
import pygame
from .scene import Scene
from ai.agent import Agent
from ui.config import DEFAULT_FONT, SMALL_FONT
from ui.components import WinLossBar
from game.board import Board
from game.cell import Cell
from utils.utils import save_game


def simulation_worker(agent1_cls, agent1_args, agent1_kwargs,
                      agent2_cls, agent2_args, agent2_kwargs,
                      num_games: int, result_queue: Queue, save_games: bool):

    agent1 = agent_factory(agent1_cls, agent1_args, agent1_kwargs)
    agent2 = agent_factory(agent2_cls, agent2_args, agent2_kwargs)

    for _ in range(num_games):
        board = Board()
        while not board.is_terminal():
            agent = agent1 if board.to_move == Cell.X else agent2
            move = agent.choose_move(board)
            board.make_move(move)
        if save_games:
            save_game(board)
        result_queue.put(board.winner)

def agent_factory(agent_cls, args, kwargs):
    return agent_cls(*args, **kwargs)

class ComparingScene(Scene):
    def __init__(self, screen, manager,
                 agent1_name:str, agent2_name:str,
                 agent1:Agent, agent2:Agent,
                 num_games:int=1000, num_processes:int=8, save_games:bool=False):
        self.screen = screen
        self.manager = manager
        self.num_games = num_games
        self.num_processes = num_processes
        self.save_games = save_games

        self.agent1_cls = agent1.__class__
        self.agent1_args = getattr(agent1, "_args", ())
        self.agent1_kwargs = getattr(agent1, "_kwargs", {})

        self.agent2_cls = agent2.__class__
        self.agent2_args = getattr(agent2, "_args", ())
        self.agent2_kwargs = getattr(agent2, "_kwargs", {})

        self.running = True
        self.results = {"win": 0, "loss": 0, "draw": 0}
        self.games_played = 0
        
        self.win_loss_bar = WinLossBar(200, 250, 400, 50, SMALL_FONT)
        self.agent1_name_surf = DEFAULT_FONT.render(f"{agent1_name} (X)", True, (0, 0, 0))
        self.agent1_name_rect = self.agent1_name_surf.get_rect(right=self.win_loss_bar.rect.left-50,
                                                               centery=self.win_loss_bar.rect.centery)
        self.agent2_name_surf = DEFAULT_FONT.render(f"{agent2_name} (O)", True, (0, 0, 0))
        self.agent2_name_rect = self.agent2_name_surf.get_rect(left=self.win_loss_bar.rect.right+50,
                                                               centery=self.win_loss_bar.rect.centery)
        self.games_played_label_surf = DEFAULT_FONT.render(f"Games played: {self.games_played} / {self.num_games}", True, (0, 0, 0))
        self.games_played_label_rect = self.games_played_label_surf.get_rect(centerx=self.win_loss_bar.rect.centerx,
                                                                             top=self.win_loss_bar.rect.bottom+20)

        self.result_queue = Queue()
        self.processes: list[Process] = []
        self.start_processes()
    
    def start_processes(self):
        """Split work evenly among worker processes."""
        games_per_process = self.num_games // self.num_processes
        remainder = self.num_games % self.num_processes

        for i in range(self.num_processes):
            count = games_per_process + (1 if i < remainder else 0)
            if count == 0:
                continue

            p = Process(
                target=simulation_worker,
                args=(
                    self.agent1_cls, self.agent1_args, self.agent1_kwargs,
                    self.agent2_cls, self.agent2_args, self.agent2_kwargs,
                    count, self.result_queue, self.save_games
                ),
                daemon=True
            )
            p.start()
            self.processes.append(p)

    def stop_processes(self):
        for p in self.processes:
            if p.is_alive():
                p.kill()
        self.processes.clear()
    
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            self.stop_processes()

    def update(self):
        while not self.result_queue.empty():
            winner = self.result_queue.get()

            if winner == Cell.X:
                self.results["win"] += 1
            elif winner == Cell.O:
                self.results["loss"] += 1
            else:
                self.results["draw"] += 1

            self.games_played += 1
        
        self.win_loss_bar.set_results(self.results['win'], self.results['draw'], self.results['loss'])
        self.win_loss_bar.update()
        self.games_played_label_surf = DEFAULT_FONT.render(f"Games played: {self.games_played} / {self.num_games}", True, (0, 0, 0))

        if self.games_played >= self.num_games:
            self.stop_processes()
    
    def draw(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.agent1_name_surf, self.agent1_name_rect)
        self.screen.blit(self.agent2_name_surf, self.agent2_name_rect)
        self.win_loss_bar.draw(self.screen)
        self.screen.blit(self.games_played_label_surf, self.games_played_label_rect)
