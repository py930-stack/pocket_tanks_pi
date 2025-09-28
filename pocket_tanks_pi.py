#!/usr/bin/env python3
"""
Pocket Tanks (Lite) – Raspberry Pi 4 / Pygame
------------------------------------------------
A compact artillery game inspired by "Pocket Tanks" designed to run well on
Raspberry Pi 4 with Python 3.9+ and pygame-ce (or pygame). Two tanks take turns
setting an angle and power to lob shells over a destructible terrain. Includes
basic wind, explosions, and an optional simple AI for Player 2.

Controls (hot-seat):
  Player 1:  Left/Right = angle, Up/Down = power, Space = fire
  Player 2:  A/D = angle, W/S = power, Left Ctrl = fire
  General:   N = New match, R = Regen terrain, T = toggle AI for P2, ESC = Quit

Author: Neal Baker-Yadav
License: MIT
"""
import math
import random
import sys
from dataclasses import dataclass
from typing import Optional, Tuple

import pygame

# ---------- Config ----------
WIDTH, HEIGHT = 960, 540
FPS = 60
GRAVITY = 0.22
WIND_MAX = 0.18
GROUND_COLOR = (30, 30, 30)
SKY_COLOR = (160, 205, 255)
HUD_COLOR = (20, 20, 20)
WHITE = (245, 245, 245)
BLUE = (80, 120, 220)
ORANGE = (255, 160, 80)
GREEN = (100, 200, 120)


@dataclass
class Tank:
    x: int
    color: Tuple[int, int, int]
    angle: float = 45.0
    power: float = 26.0
    alive: bool = True
    facing: int = 1

    def draw(self, surf: pygame.Surface, y_ground: int):
        body = pygame.Rect(self.x - 14, y_ground - 12, 28, 12)
        pygame.draw.rect(surf, self.color, body, border_radius=3)
        rad = math.radians(self.angle if self.facing == 1 else (180 - self.angle))
        length = 18
        x1, y1 = self.x, y_ground - 12
        x2, y2 = x1 + int(math.cos(rad) * length), y1 - int(math.sin(rad) * length)
        pygame.draw.line(surf, self.color, (x1, y1), (x2, y2), 3)
        pygame.draw.circle(surf, self.color, (self.x, y_ground - 14), 4)


@dataclass
class Shell:
    x: float
    y: float
    vx: float
    vy: float
    alive: bool = True

    def step(self, wind: float):
        self.x += self.vx
        self.y += self.vy
        self.vx += wind * 0.02
        self.vy += GRAVITY
        if self.x < -20 or self.x > WIDTH + 20 or self.y > HEIGHT + 40:
            self.alive = False


class Terrain:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), flags=pygame.SRCALPHA).convert_alpha()
        self.generate()

    def generate(self):
        self.surface.fill((0, 0, 0, 0))
        baseline = int(self.height * 0.65)
        points = []
        for x in range(self.width):
            h = (math.sin(x * 0.008) * 30
                 + math.sin(x * 0.022 + 1.3) * 20
                 + math.sin(x * 0.0045 + 2.0) * 45)
            jitter = random.uniform(-6, 6)
            y = baseline - int(h + jitter)
            points.append((x, max(120, min(self.height - 1, y))))
        poly = [(0, self.height)] + points + [(self.width - 1, self.height)]
        pygame.draw.polygon(self.surface, GROUND_COLOR + (255,), poly)

    def destroy(self, x: int, y: int, radius: int):
        pygame.draw.circle(self.surface, (0, 0, 0, 0), (x, y), radius)

    def ground_y_at(self, x: int) -> int:
        x = max(0, min(self.width - 1, x))
        for y in range(self.height):
            if self.surface.get_at((x, y)).a > 0:
                return y
        return self.height

    def collides(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.surface.get_at((x, y)).a > 0

    def draw(self, screen: pygame.Surface):
        screen.blit(self.surface, (0, 0))


class Game:
    def __init__(self, ai_for_p2: bool = False):
        pygame.init()
        flags = pygame.SCALED | pygame.RESIZABLE
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        pygame.display.set_caption("Pocket Tanks (Lite) – Pygame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("DejaVu Sans", 16)

        self.terrain = Terrain(WIDTH, HEIGHT)
        self.wind = random.uniform(-WIND_MAX, WIND_MAX)

        self.p1 = Tank(x=int(WIDTH * 0.12), color=BLUE, angle=45, power=28, facing=1)
        self.p2 = Tank(x=int(WIDTH * 0.88), color=ORANGE, angle=45, power=28, facing=-1)
        self.tank_positions_on_ground()

        self.turn = 1
        self.shell: Optional[Shell] = None
        self.ai_for_p2 = ai_for_p2
        self.scores = [0, 0]

    def tank_positions_on_ground(self):
        for t in (self.p1, self.p2):
            t.y_ground = self.terrain.ground_y_at(t.x)

    def reset_round(self, regen_terrain=False):
        if regen_terrain:
            self.terrain.generate()
        self.wind = random.uniform(-WIND_MAX, WIND_MAX)
        self.shell = None
        self.p1.alive = self.p2.alive = True
        self.tank_positions_on_ground()
        self.turn = 1

    def spawn_shell(self, tank: Tank):
        angle = math.radians(tank.angle if tank.facing == 1 else (180 - tank.angle))
        speed = tank.power * 0.8
        x0 = tank.x + math.cos(angle) * 18
        y0 = tank.y_ground - 12 - math.sin(angle) * 18
        vx = math.cos(angle) * speed
        vy = -math.sin(angle) * speed
        self.shell = Shell(x0, y0, vx, vy)

    def update(self):
        if self.shell and self.shell.alive:
            self.shell.step(self.wind)
            ix, iy = int(self.shell.x), int(self.shell.y)
            if 0 <= ix < WIDTH and 0 <= iy < HEIGHT and self.terrain.collides(ix, iy):
                self.explode(ix, iy)
                self.shell.alive = False
            for idx, t in enumerate((self.p1, self.p2)):
                if t.alive:
                    dist = math.hypot(t.x - self.shell.x, (t.y_ground - 10) - self.shell.y)
                    if dist < 16:
                        self.explode(ix, iy)
                        self.scores[0 if idx == 1 else 1] += 30
                        self.shell.alive = False
                        break
            if self.shell and not self.shell.alive:
                self.turn = 2 if self.turn == 1 else 1
                self.shell = None
                self.tank_positions_on_ground()
        else:
            if self.ai_for_p2 and self.turn == 2:
                self.simple_ai_fire()

    def explode(self, x: int, y: int):
        radius = 24
        self.terrain.destroy(x, y, radius)
        for i, t in enumerate((self.p1, self.p2)):
            d = math.hypot(t.x - x, (t.y_ground - 10) - y)
            if d < radius + 4:
                if (self.turn == 1 and i == 1) or (self.turn == 2 and i == 0):
                    self.scores[self.turn - 1] += int(40 * (1.0 - d / (radius + 4)))

    def simple_ai_fire(self):
        target_x = self.p1.x
        best_angle = None
        best_dist = 1e9
        power = random.uniform(24, 30)
        for _ in range(10):
            ang = random.uniform(30, 80)
            rad = math.radians(180 - ang)
            vx = math.cos(rad) * power * 0.8
            vy = -math.sin(rad) * power * 0.8
            x, y = float(self.p2.x), float(self.p2.y_ground - 12)
            for _ in range(240):
                x += vx
                y += vy
                vx += self.wind * 0.02
                vy += GRAVITY
                if y >= HEIGHT or x < 0 or x > WIDTH:
                    break
                if y >= self.terrain.ground_y_at(int(x)):
                    break
            d = abs(x - target_x)
            if d < best_dist:
                best_dist = d
                best_angle = ang
        if best_angle is not None:
            self.p2.angle = best_angle
            self.p2.power = power
            self.spawn_shell(self.p2)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if self.turn == 1:
            if keys[pygame.K_LEFT]:
                self.p1.angle = max(5, self.p1.angle - 0.8)
            if keys[pygame.K_RIGHT]:
                self.p1.angle = min(85, self.p1.angle + 0.8)
            if keys[pygame.K_UP]:
                self.p1.power = min(40, self.p1.power + 0.4)
            if keys[pygame.K_DOWN]:
                self.p1.power = max(12, self.p1.power - 0.4)
        else:
            if keys[pygame.K_a]:
                self.p2.angle = min(85, self.p2.angle + 0.8)
            if keys[pygame.K_d]:
                self.p2.angle = max(5, self.p2.angle - 0.8)
            if keys[pygame.K_w]:
                self.p2.power = min(40, self.p2.power + 0.4)
            if keys[pygame.K_s]:
                self.p2.power = max(12, self.p2.power - 0.4)

    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit(0)
            if e.key == pygame.K_n:
                self.reset_round(regen_terrain=True)
            if e.key == pygame.K_r:
                self.terrain.generate()
                self.tank_positions_on_ground()
            if e.key == pygame.K_t:
                self.ai_for_p2 = not self.ai_for_p2
            if self.turn == 1 and e.key == pygame.K_SPACE and not self.shell:
                self.spawn_shell(self.p1)
            if self.turn == 2 and e.key == pygame.K_LCTRL and not self.shell:
                self.spawn_shell(self.p2)

    def draw_hud(self):
        hud = pygame.Surface((WIDTH, 96))   # make HUD taller (was 64)
        hud.fill(HUD_COLOR)
        self.screen.blit(hud, (0, 0))
    
        def txt(s, x, y, color=WHITE):
            img = self.font.render(s, True, color)
            self.screen.blit(img, (x, y))
    
        # Top row: title + stats
        txt("Pocket Tanks (Lite) – Pygame", 10, 8)
        txt(f"Wind: {self.wind:+.2f}", 280, 8)
        txt(f"P1 Angle: {self.p1.angle:4.1f}  Power: {self.p1.power:4.1f}", 410, 8, BLUE)
        txt(f"P2 Angle: {self.p2.angle:4.1f}  Power: {self.p2.power:4.1f}", 700, 8, ORANGE)
        txt(f"Score  P1:{self.scores[0]}  P2:{self.scores[1]}", 620, 28)
        turn_str = "P1" if self.turn == 1 else "P2 (AI)" if self.ai_for_p2 and self.turn == 2 else "P2"
        txt(f"Turn: {turn_str}", 820, 28, GREEN)
    
        # Bottom rows: controls (split nicely)
        txt("[P1] Arrows=angle/power  Space=Fire", 10, 48)
        txt("[P2] A/D,W/S  LCtrl=Fire", 10, 66)
        txt("N:New  R:Regen  T:AI  ESC:Quit", 10, 84)


    def render(self):
        self.screen.fill(SKY_COLOR)
        self.terrain.draw(self.screen)
        if self.p1.alive:
            self.p1.draw(self.screen, self.p1.y_ground)
        if self.p2.alive:
            self.p2.draw(self.screen, self.p2.y_ground)
        if self.shell and self.shell.alive:
            pygame.draw.circle(self.screen, (20, 20, 20), (int(self.shell.x), int(self.shell.y)), 2)
        self.draw_hud()
        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)
            for e in pygame.event.get():
                self.handle_event(e)
            self.handle_input()
            self.update()
            self.render()


def main():
    ai = "--ai" in sys.argv
    Game(ai_for_p2=ai).run()


if __name__ == "__main__":
    main()
