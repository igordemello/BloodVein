from pygame import *
import sys
from pygame.locals import QUIT
import math


#já aviso de ante mao que toda essa classe foi chines
class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_particle(self, x, y, color, velocity, lifetime, size):
        self.particles.append({
            "x": x, "y": y,
            "vx": velocity[0], "vy": velocity[1],
            "color": color,
            "life": lifetime,
            "max_life": lifetime,
            "size": size
        })

    def update(self, dt):
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

    def draw(self, surface):
        for p in self.particles:
            alpha = int(255 * (p["life"] / p["max_life"]))
            color = (*p["color"][:3], alpha)
            s = Surface((p["size"], p["size"]), SRCALPHA)
            draw.circle(s, color, (p["size"] // 2, p["size"] // 2), p["size"] // 2)
            surface.blit(s, (p["x"] - p["size"] // 2, p["y"] - p["size"] // 2))