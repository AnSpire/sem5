import random
import math
from shapely import LineString
from roads import slightly_noisy_curve
from config import CityConfig


config = CityConfig()


def generate_branches(roads, city_polygon):

    branches = []

    for road in roads:
        if not isinstance(road, LineString):
            continue

        # середина дороги
        mid = road.interpolate(0.4, normalized=True)
        x, y = mid.x, mid.y

        if random.random() > config.BRANCH_PROB:
            continue

        dx = road.coords[1][0] - road.coords[0][0]
        dy = road.coords[1][1] - road.coords[0][1]
        nx, ny = -dy, dx
        length = math.sqrt(nx*nx + ny*ny)
        nx, ny = nx/length, ny/length

        L = config.CELL * random.uniform(config.BRANCH_MIN, config.BRANCH_MAX)
        if random.random() < 0.5:
            L = -L

        p2 = (x + nx*L, y + ny*L)
        branch = LineString(slightly_noisy_curve((x, y), p2, rate=random.randint(0, 6)))

        if not city_polygon.contains(branch):
            continue

        branches.append(branch)

    return branches