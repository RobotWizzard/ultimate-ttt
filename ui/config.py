import pygame
pygame.font.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Ultimate Tic-Tac-Toe"

# --- Fonts ---
TITLE_FONT = pygame.font.SysFont("Harlow Solid", 72)
SECONDARY_TITLE_FONT = pygame.font.SysFont("Berlin Sans FB", 36)
DEFAULT_FONT = pygame.font.SysFont("Calibri", 24, True)
SMALL_FONT = pygame.font.SysFont("Calibri", 18)

# --- Colors ---
X_COLOR = (200, 0, 0)
O_COLOR = (0, 0, 200)
HIGHLIGHT_COLOR = (0, 255, 0)
LAST_MOVE_COLOR = (0, 255, 255, 150)