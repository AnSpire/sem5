import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.affinity import translate
import matplotlib.pyplot as plt
import math
import random
from generate_node import generate_nodes
from city_border import get_city_border
from roads import generate_roads
from branches import generate_branches
from houses import generate_houses
from config import CityConfig
"""
РАЗНЫЙ РАЗМЕР КВАРТАЛОВ
"""
config = CityConfig()


nodes = generate_nodes(config.GRID, config.CELL)
CITY_BORDER = get_city_border(nodes)
roads = generate_roads(nodes)
all_roads = roads

# === ЭТАП 1 — рисуем и показываем только дороги ===
if config.SHOW_LOCAL:
    plt.ion()
    fig, ax = plt.subplots(figsize=(10,10))

    for r in all_roads:
        x, y = r.xy
        ax.plot(x, y, color="black", linewidth=1)

    ax.set_aspect("equal")
    plt.show()
    plt.pause(0.1)

    # === ЭТАП 2 — дорисовываем дома ===
    houses = generate_houses(nodes, config.CELL, all_roads, ax)

    # for house in houses:
    #     x, y = house.exterior.xy
    #     ax.fill(x, y, color="brown", alpha=1, edgecolor="black", linewidth=1)

    # узлы поверх
    for row in nodes:
        for x, y in row:
            ax.scatter(x, y, color="red", s=10)

    plt.draw()
    plt.pause(15)         # обновление окна

