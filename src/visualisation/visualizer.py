from src.cli import AppConfig
from src.simul import SimulationMap
import pygame


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720


class Visualizer:
    def __init__(self, app: AppConfig, map: SimulationMap) -> None:
        self.app = app
        self.map = map
        self._compute_offsets()
        self._update_coord()

    def _compute_offsets(self) -> None:
        min_x = min(hub.coord_x for hub in self.map.hubs.values())
        min_y = min(hub.coord_y for hub in self.map.hubs.values())
        self.x_offset = -min_x if min_x < 0 else 0
        self.y_offset = -min_y if min_y < 0 else 0

    def _update_coord(self) -> None:
        for hub in self.map.hubs.values():
            hub.coord_x = hub.coord_x + self.x_offset
            hub.coord_y = hub.coord_y + self.y_offset

    def run(self) -> None:
        pygame.init()
        screen_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen_surface.fill(color="red")
            pygame.display.set_caption(self.app.map_path)
            pygame.display.update()
        pygame.quit()
