from src.cli import AppConfig
from src.simul import Simulation, Solver
from typing import Tuple, List, Dict
import pygame


WINDOW_WIDTH = 1700
WINDOW_HEIGHT = 900
MAP_HEIGHT = WINDOW_HEIGHT * 0.75
PADDING = 60
HUB_SIZE = 40
DRON_SIZE = 35


class Visualizer:
    def __init__(self,
                 app: AppConfig,
                 simul: Simulation) -> None:
        self.app = app
        self.simul = simul
        self._compute_scale()

    def _compute_scale(self) -> None:
        self.min_x = min(hub.coord_x for hub in self.simul.hubs.values())
        self.min_y = min(hub.coord_y for hub in self.simul.hubs.values())
        self.max_x = max(hub.coord_x for hub in self.simul.hubs.values())
        self.max_y = max(hub.coord_y for hub in self.simul.hubs.values())

    def _to_screen(self, x: int, y: int) -> Tuple[int, int]:
        range_x = (self.max_x - self.min_x)
        range_y = (self.max_y - self.min_y)
        if range_x == 0:
            new_x = WINDOW_WIDTH // 2
        else:
            new_x = int((x - self.min_x) / range_x *
                        (WINDOW_WIDTH - 2 * PADDING) + PADDING)
        if range_y == 0:
            new_y = MAP_HEIGHT // 2
        else:
            new_y = int((y - self.min_y) / range_y *
                        (MAP_HEIGHT - 2 * PADDING) + PADDING)
        return new_x, new_y

    def _get_turn_movement(self, turn: int) -> str:
        line = ""
        for drone in self.simul.drones:
            if turn > 0 and turn < len(drone.steps):
                if drone.steps[turn - 1] == drone.steps[turn]:
                    continue
                line = f"{line} {drone.steps[turn].movement_str}"
        return line

    def run(self) -> None:
        turn = 0
        max_turn = self.simul.analitics.max_turn
        pygame.init()
        clock = pygame.time.Clock()
        screen_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(self.app.map_path)
        font = pygame.font.Font(size=12)
        hub_text_cache: Dict[str, Tuple[pygame.Surface, pygame.Surface]] = {}
        for name, hub in self.simul.hubs.items():
            name_surf = font.render(name, True, "white")
            zone_type_surf = font.render(hub.zone_type.value, True, "white")
            hub_text_cache[name] = (name_surf, zone_type_surf)
        dron = pygame.image.load("images/player.png")
        scaled_dron = pygame.transform.scale(
            dron, (DRON_SIZE, DRON_SIZE)).convert_alpha()
        dron_rect = scaled_dron.get_frect()
        dron_rect.center = self._to_screen(
            self.simul.start_hub.coord_x, self.simul.start_hub.coord_y)
        drones = {dron: dron_rect.copy() for dron in self.simul.drones}
        speed = 2.0
        running = True
        while running:
            clock.tick()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        turn = (turn + 1) % max_turn
                    if event.key == pygame.K_LEFT:
                        turn = turn - 1 if turn > 0 else 0
                    line = self._get_turn_movement(turn)
                    if line:
                        print(line)
            screen_surface.fill(color="grey38")
            # pygame.draw.line(screen_surface, "black",
            #                  (0, MAP_HEIGHT), (WINDOW_WIDTH, MAP_HEIGHT), 5)
            pygame.draw.rect(
                screen_surface,
                "grey48",
                (0, MAP_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT), 0, 10,)
            for conn in self.simul.connections.values():
                start = self._to_screen(conn.hub_1.coord_x, conn.hub_1.coord_y)
                end = self._to_screen(conn.hub_2.coord_x, conn.hub_2.coord_y)
                pygame.draw.line(screen_surface, conn.color, start, end)
            for hub in self.simul.hubs.values():
                surface = pygame.Surface((HUB_SIZE, HUB_SIZE))
                try:
                    surface.fill(hub.color if hub.color else "white")
                except ValueError:
                    surface.fill("springgreen3")
                hub_rec = surface.get_frect()
                hub_rec.center = self._to_screen(hub.coord_x, hub.coord_y)
                screen_surface.blit(surface, hub_rec)

                name_surf, zone_type_surf = hub_text_cache[hub.name]
                name_rec = name_surf.get_frect()
                name_rec.center = (hub_rec.midbottom[0],
                                   hub_rec.midbottom[1] + 10)
                screen_surface.blit(name_surf, name_rec)
                zone_type_rec = zone_type_surf.get_frect()
                zone_type_rec.center = (name_rec.midbottom[0],
                                        name_rec.midbottom[1] + 15)
                screen_surface.blit(zone_type_surf, zone_type_rec)
            for dron, dron_rec in drones.items():
                screen_surface.blit(scaled_dron, dron_rec)
                if turn < len(dron.steps) and turn >= 0:
                    next_x, next_y = self._to_screen(
                        dron.steps[turn].location.coord_x,
                        dron.steps[turn].location.coord_y)
                    next = pygame.math.Vector2((next_x, next_y))
                    current = pygame.math.Vector2(
                        dron_rec.center).move_towards(next, speed)
                    dron_rec.center = current
            pygame.display.update()
        pygame.quit()
