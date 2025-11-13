from .scene import Scene
from ui.components import TextInput, Dropdown, Button
from ui.config import DEFAULT_FONT
from ai import RandomAgent, MinimaxAgent
from ai.eval import simple_eval


class CompareConfigScene(Scene):
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.agent1 = RandomAgent()
        self.agent2 = RandomAgent()

        self.agent1_label_surf = DEFAULT_FONT.render("Agent 1:", True, (0, 0, 0))
        self.agent1_label_rect = self.agent1_label_surf.get_rect(left=50, top=50)
        self.agent1_dropdown = Dropdown((180, 50, 200, 40), ["random", "minimax", "mcts"], on_select=self.change_agent1)

        self.agent2_label_surf = DEFAULT_FONT.render("Agent 2:", True, (0, 0, 0))
        self.agent2_label_rect = self.agent1_label_surf.get_rect(left=50, top=130)
        self.agent2_dropdown = Dropdown((180, 130, 200, 40), ["random", "minimax", "mcts"], on_select=self.change_agent2)

        self.n_label_surf = DEFAULT_FONT.render("Number of games:", True, (0, 0, 0))
        self.n_label_rect = self.n_label_surf.get_rect(left=50, centery=210+self.n_label_surf.get_height()//2)
        self.text_input = TextInput((self.n_label_rect.right+20, 210, 100, 40), text="1000", on_submit=self.check_input)
        self.warning_surf = DEFAULT_FONT.render("*Number of games must be a positive integer", True, (200, 0, 0))
        self.warning_rect = self.warning_surf.get_rect(left=50, top=250)
        self.show_warning = False

        self.start_button = Button((50, 500, 100, 40), "Start", on_click=self.start_compare)
    
    def check_input(self, input):
        try:
            int(input)
            self.show_warning = False
        except ValueError:
            self.show_warning = True
    
    def change_agent1(self, agent_name):
        if agent_name == "random":
            self.agent1 = RandomAgent()
        elif agent_name == "minimax":
            self.agent1 = MinimaxAgent(simple_eval)
        else:  #TODO: add mcts
            pass
    
    def change_agent2(self, agent_name):
        if agent_name == "random":
            self.agent2 = RandomAgent()
        elif agent_name == "minimax":
            self.agent2 = MinimaxAgent(simple_eval)
        else:  #TODO: add mcts
            pass
    
    def start_compare(self):
        try:
            num_games = int(self.text_input.text)
            if num_games <= 0:
                self.show_warning = True
                return
        except ValueError:
            self.show_warning = True
            return
        from .comparing_scene import ComparingScene
        comparing_scene = ComparingScene(self.screen, self.manager, self.agent1_dropdown.get_text(), self.agent2_dropdown.get_text(),
                                         self.agent1, self.agent2, num_games)
        self.manager.set_scene(comparing_scene)
        
    def handle_event(self, event):
        self.text_input.handle_event(event)
        self.agent1_dropdown.handle_event(event)
        self.agent2_dropdown.handle_event(event)
        self.start_button.handle_event(event)
    
    def update(self):
        self.text_input.update()
        self.start_button.update()
    
    def draw(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.n_label_surf, self.n_label_rect)
        self.text_input.draw(self.screen)
        if self.show_warning:
            self.screen.blit(self.warning_surf, self.warning_rect)
        self.screen.blit(self.agent1_label_surf, self.agent1_label_rect)
        self.screen.blit(self.agent2_label_surf, self.agent2_label_rect)
        self.agent2_dropdown.draw(self.screen)
        self.agent1_dropdown.draw(self.screen)
        self.start_button.draw(self.screen)
