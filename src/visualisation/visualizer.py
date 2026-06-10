from src.cli import AppConfig
from src.simul import Simulation
from typing import Tuple, List, Dict
import pygame


WINDOW_WIDTH = 1700
WINDOW_HEIGHT = 900
MAP_HEIGHT = WINDOW_HEIGHT * 0.75
ACTUAL_FOOTER_HEIGHT = WINDOW_HEIGHT - MAP_HEIGHT
PADDING = 60
FOOTER_PADDING = 20
HUB_SIZE = 40
DRON_SIZE = 35


class Footer:
    def __init__(self, simul: Simulation, speed: int, ) -> None:
        self.font = pygame.font.Font(size=40)
        self.info_panel_font = pygame.font.Font(size=30)
        self.footer_rect = pygame.rect.FRect(
            0, MAP_HEIGHT, WINDOW_WIDTH, ACTUAL_FOOTER_HEIGHT)
        self._draw_control_panel()
        self.update_map_name(simul.name)
        self._update_drones_count(simul.analitics.drones_count)
        self._update_speed(speed)
        self._update_max_turn(simul.analitics.max_turn)
        self._update_curr_turn(0)

    def update_map_name(self, new_name: str) -> None:
        self.map_name = new_name
        self.map_name_surf = self.font.render(self.map_name, True, "yellow")
        self.map_name_rect = self.map_name_surf.get_rect()
        self.map_name_rect.midtop = (
            self.footer_rect.midtop[0],
            self.footer_rect.midtop[1] + FOOTER_PADDING)

    def _draw_control_panel(self) -> None:
        font = pygame.font.Font(size=30)
        next_prev_map_msg = "[ up | down ]  -  next | prev map"
        next_prev_turn_msg = "[ left | right ]  -  next | prev turn"
        speed_msg = "[ - | + ]  -  speed"
        restart_msg = "[ R ]  -  restart"
        space_msg = "[ SPACE ]  -  auto play"
        control_panel_msg = (f"{next_prev_turn_msg}\n{next_prev_map_msg}\n"
                             f"{space_msg}\n{restart_msg}\n{speed_msg}")
        self.control_panel_surf = font.render(
            control_panel_msg, True, "yellow")
        self.control_panel_rect = self.control_panel_surf.get_rect()
        self.control_panel_rect.midbottom = (
            self.footer_rect.midbottom[0],
            self.footer_rect.midbottom[1] - FOOTER_PADDING)

    def _update_drones_count(self, count: int) -> None:
        self.drones_count_surf = self.info_panel_font.render(
            f"drones count: {count}", True, "yellow")
        self.drones_count_rect = self.drones_count_surf.get_frect()
        self.drones_count_rect.topleft = (
            self.footer_rect.topleft[0] + FOOTER_PADDING,
            self.footer_rect.topleft[1] + FOOTER_PADDING * 3)

    def _update_speed(self, value: float) -> None:
        self.speed_surf = self.info_panel_font.render(
            f"speed: {value}", True, "yellow")
        self.speed_rect = self.speed_surf.get_frect()
        self.speed_rect.topleft = (
            self.drones_count_rect.bottomleft[0],
            self.drones_count_rect.bottomleft[1] + 5)

    def _update_max_turn(self, value: int) -> None:
        self.max_turn_surf = self.info_panel_font.render(
            f"MAX TURN: {value}", True, "yellow")
        self.max_turn_rect = self.max_turn_surf.get_frect()
        self.max_turn_rect.topleft = (
            self.speed_rect.bottomleft[0],
            self.speed_rect.bottomleft[1] + 5)

    def _update_curr_turn(self, value: int) -> None:
        self.curr_turn_surf = self.info_panel_font.render(
            f"CURRENT TURN: {value}", True, "yellow")
        self.curr_turn_rect = self.curr_turn_surf.get_frect()
        self.curr_turn_rect.topleft = (
            self.max_turn_rect.bottomleft[0],
            self.max_turn_rect.bottomleft[1] + 5)


class Visualizer:
    def __init__(self,
                 app: AppConfig,
                 simulations: List[Simulation]) -> None:
        self.app = app
        self.simulations = simulations
        self.current_map_ind = 0
        self.current_turn = 0
        self.maps_count = len(self.simulations)
        self.simul = simulations[self.current_map_ind]
        self._compute_scale()
        self.speed = 1.0
        self.speed_step = 0.5
        self.turn_duration = 1.0
        self.turn_progress = 0.0
        self.auto_play = False

    def _compute_scale(self) -> None:
        self.min_x = min(hub.coord_x for hub in self.simul.hubs.values())
        self.min_y = min(hub.coord_y for hub in self.simul.hubs.values())
        self.max_x = max(hub.coord_x for hub in self.simul.hubs.values())
        self.max_y = max(hub.coord_y for hub in self.simul.hubs.values())

    def _to_screen(self, x: float, y: float) -> Tuple[int, int]:
        range_x = (self.max_x - self.min_x)
        range_y = (self.max_y - self.min_y)
        if range_x == 0:
            new_x = WINDOW_WIDTH // 2
        else:
            new_x = int((x - self.min_x) / range_x *
                        (WINDOW_WIDTH - 2 * PADDING) + PADDING)
        if range_y == 0:
            new_y = int(MAP_HEIGHT // 2)
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
                line = f"{line} {drone.id}-{drone.steps[turn].name}"
        return line

    def _update_hub_text_cache(self) -> None:
        hub_text_cache: Dict[str, Tuple[pygame.Surface, pygame.Surface]] = {}
        for name, hub in self.simul.hubs.items():
            name_surf = self.hub_text_font.render(name, True, "white")
            zone_type_surf = self.hub_text_font.render(
                hub.zone_type.value, True, "white")
            hub_text_cache[name] = (name_surf, zone_type_surf)
        self.hub_text_cache = hub_text_cache

    def _create_drones(self) -> None:
        self.dron_rect.center = self._to_screen(
            self.simul.start_hub.coord_x, self.simul.start_hub.coord_y)
        drones_ids = list()
        for dron in self.simul.drones:
            drone_id_surf = self.drone_id_font.render(dron.id, True, "black")
            drone_id_rect = drone_id_surf.get_frect()
            drone_id_rect.midbottom = self.dron_rect.midtop
            drones_ids.append(
                (dron, self.dron_rect.copy(), drone_id_surf, drone_id_rect))
        self.drones_ids = drones_ids
        self.drones = {dron: self.dron_rect.copy()
                       for dron in self.simul.drones}

    def _reload(self) -> None:
        self.simul = self.simulations[self.current_map_ind]
        self.current_turn = 0
        self.footer.update_map_name(self.simul.name)
        self._compute_scale()
        self._update_hub_text_cache()
        self.footer._update_drones_count(self.simul.analitics.drones_count)
        self.footer._update_max_turn(self.simul.analitics.max_turn)
        self.footer._update_curr_turn(0)
        self._create_drones()
        print()

    def _execute_event(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_UP:
            self.current_map_ind = (
                self.current_map_ind - 1 if self.current_map_ind > 0 else 0)
            self._reload()
        if event.key == pygame.K_DOWN:
            self.current_map_ind = (self.current_map_ind + 1) % self.maps_count
            self._reload()
        if event.key == pygame.K_RIGHT:
            self.turn_progress = 0.0
            if self.current_turn == self.simul.analitics.max_turn:
                self._reload()
            else:
                self.current_turn = self.current_turn + 1
                self.footer._update_curr_turn(self.current_turn)
            line = self._get_turn_movement(self.current_turn)
            if line:
                print(line)
        if event.key == pygame.K_LEFT:
            self.turn_progress = 0.0
            self.current_turn = (
                self.current_turn - 1 if self.current_turn > 0 else 0)
            self.footer._update_curr_turn(self.current_turn)
            line = self._get_turn_movement(self.current_turn)
            if line:
                print(line)
        if event.key == pygame.K_r:
            self._reload()
        if event.key == pygame.K_MINUS:
            if self.speed > 0.5:
                self.turn_duration = self.turn_duration + self.speed_step
                self.speed -= self.speed_step
                self.footer._update_speed(self.speed)
        if event.key == pygame.K_EQUALS:
            if self.turn_duration > 0.5:
                self.turn_duration = self.turn_duration - self.speed_step
                self.speed += self.speed_step
                self.footer._update_speed(self.speed)
        if event.key == pygame.K_SPACE:
            if not self.auto_play:
                self.auto_play = not self.auto_play
                self.turn_progress = 0.0
                self.current_turn += 1
                self.footer._update_curr_turn(self.current_turn)
                print(self._get_turn_movement(self.current_turn))

    def _draw_footer(self) -> None:
        self.screen_surface.fill("black", self.footer.footer_rect)
        self.screen_surface.blit(
            self.footer.map_name_surf, self.footer.map_name_rect)
        self.screen_surface.blit(self.footer.control_panel_surf,
                                 self.footer.control_panel_rect)
        self.screen_surface.blit(self.footer.drones_count_surf,
                                 self.footer.drones_count_rect)
        self.screen_surface.blit(self.footer.speed_surf,
                                 self.footer.speed_rect)
        self.screen_surface.blit(self.footer.max_turn_surf,
                                 self.footer.max_turn_rect)
        self.screen_surface.blit(self.footer.curr_turn_surf,
                                 self.footer.curr_turn_rect)

    def _draw_hubs(self) -> None:
        for hub in self.simul.hubs.values():
            surface = pygame.Surface((HUB_SIZE, HUB_SIZE))
            try:
                surface.fill(hub.color if hub.color else "white")
            except ValueError:
                surface.fill("springgreen3")
            hub_rec = surface.get_frect()
            hub_rec.center = self._to_screen(hub.coord_x, hub.coord_y)
            self.screen_surface.blit(surface, hub_rec)

            name_surf, zone_type_surf = self.hub_text_cache[hub.name]
            name_rec = name_surf.get_frect()
            name_rec.center = (hub_rec.midbottom[0],
                               hub_rec.midbottom[1] + 10)
            self.screen_surface.blit(name_surf, name_rec)
            zone_type_rec = zone_type_surf.get_frect()
            zone_type_rec.center = (name_rec.midbottom[0],
                                    name_rec.midbottom[1] + 15)
            self.screen_surface.blit(zone_type_surf, zone_type_rec)

    def _draw_drones(self, delta_time: float) -> None:
        for dron, dron_rect, id_surf, id_rect in self.drones_ids:
            self.screen_surface.blit(id_surf, id_rect)
            self.screen_surface.blit(self.scaled_dron, dron_rect)
            if (self.current_turn < len(dron.steps)
               and self.current_turn >= 0):
                next_x, next_y = self._to_screen(
                    dron.steps[self.current_turn].coord_x,
                    dron.steps[self.current_turn].coord_y)
                current = pygame.math.Vector2(dron_rect.center)
                target = pygame.math.Vector2((next_x, next_y))
                distance = current.distance_to(target)
                speed = distance / (self.turn_duration - self.turn_progress)
                current = current.move_towards(target, speed * delta_time)
                dron_rect.center = current
                id_rect.midbottom = dron_rect.midtop

    def run(self) -> None:
        pygame.init()
        clock = pygame.time.Clock()
        self.screen_surface = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("FLY-IN")
        self.hub_text_font = pygame.font.Font(size=12)
        self.drone_id_font = pygame.font.Font(size=30)
        self.footer = Footer(self.simul, self.speed)
        self._update_hub_text_cache()
        dron = pygame.image.load("images/player.png")
        self.scaled_dron = pygame.transform.scale(
            dron, (DRON_SIZE, DRON_SIZE)).convert_alpha()
        self.dron_rect = self.scaled_dron.get_frect()
        self._create_drones()
        running = True
        while running:
            dt = clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    self._execute_event(event)
            self.screen_surface.fill(color="grey38")
            self._draw_footer()
            for conn in self.simul.connections.values():
                start = self._to_screen(conn.hub_1.coord_x, conn.hub_1.coord_y)
                end = self._to_screen(conn.hub_2.coord_x, conn.hub_2.coord_y)
                pygame.draw.line(self.screen_surface, conn.color, start, end)
            self._draw_hubs()
            self._draw_drones(dt)
            self.turn_progress += dt
            # if (self.auto_play
            #    and self.turn_progress > self.current_turn * self.turn_duration):
            #     self.current_turn = self.current_turn + 1
            #     self.footer._update_curr_turn(self.current_turn)
            #     line = self._get_turn_movement(self.current_turn)
            #     if line:
            #         print(line)
            pygame.display.update()
        pygame.quit()
