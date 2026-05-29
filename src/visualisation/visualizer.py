from src.cli import AppConfig
from src.simul import SimulationMap
from typing import Tuple, List
import pygame
import math


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
PADDING = 60
HUB_SIZE = 40


class Visualizer:
    def __init__(self, app: AppConfig, map: SimulationMap) -> None:
        self.app = app
        self.map = map
        self._compute_scale()

    def _compute_scale(self) -> None:
        self.min_x = min(hub.coord_x for hub in self.map.hubs.values())
        self.min_y = min(hub.coord_y for hub in self.map.hubs.values())
        self.max_x = max(hub.coord_x for hub in self.map.hubs.values())
        self.max_y = max(hub.coord_y for hub in self.map.hubs.values())

    def _to_screen(self, x: int, y: int) -> Tuple[int, int]:
        range_x = (self.max_x - self.min_x)
        range_y = (self.max_y - self.min_y)
        if range_x == 0:
            new_x = WINDOW_WIDTH // 2
        else:
            new_x = int((x - self.min_x) / range_x *
                        (WINDOW_WIDTH - 2 * PADDING) + PADDING)
        if range_y == 0:
            new_y = WINDOW_HEIGHT // 2
        else:
            new_y = int((y - self.min_y) / range_y *
                        (WINDOW_HEIGHT - 2 * PADDING) + PADDING)
        return new_x, new_y

    def _build_hub_surfaces(self) -> List[Tuple]:
        hub_surfaces = []
        for hub in self.map.hubs.values():
            surface = pygame.Surface((HUB_SIZE, HUB_SIZE))
            try:
                surface.fill(hub.color if hub.color else "white")
            except ValueError:
                surface.fill("springgreen3")
            x, y = self._to_screen(hub.coord_x, hub.coord_y)
            pos = (x - HUB_SIZE // 2, y - HUB_SIZE // 2)
            hub_surfaces.append((surface, pos))
        return hub_surfaces

    def run(self) -> None:
        pygame.init()
        screen_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        hub_surfaces = self._build_hub_surfaces()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen_surface.fill(color="black")
            pygame.display.set_caption(self.app.map_path)
            for conn in self.map.connections:
                start = self._to_screen(conn.hub_1.coord_x, conn.hub_1.coord_y)
                end = self._to_screen(conn.hub_2.coord_x, conn.hub_2.coord_y)
                pygame.draw.line(screen_surface, "white", start, end)
            screen_surface.blits(hub_surfaces)
            pygame.display.update()
        pygame.quit()
