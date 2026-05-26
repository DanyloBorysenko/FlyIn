from src.cli import AppConfig
import pygame


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720


class Visualizer:
    def __init__(self, app: AppConfig) -> None:
        self.app = app

    def run(self) -> None:
        pygame.init()
        screen_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
