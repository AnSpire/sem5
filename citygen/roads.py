import random
import numpy as np
from shapely import LineString
from config import CityConfig


config = CityConfig()


def slightly_noisy_curve(p1, p2, rate: int):
    x1, y1 = p1
    x2, y2 = p2

    mid = np.array([(x1+x2)/2, (y1+y2)/2])

    angle = random.uniform(0, 2*np.pi)
    dist = random.uniform(1, 4)
    offset = np.array([np.cos(angle)*dist, np.sin(angle)*dist])

    mid = mid + offset + rate

    curve = LineString([p1, tuple(mid), p2])
    return curve.simplify(0.5)





def generate_roads(nodes):
    roads = []
    #SKIP_PROB = 0.0546  # удаляем только внутренние дороги
    SKIP_PROB = 0
    rows = len(nodes)
    cols = len(nodes[0])

    for i in range(rows):
        for j in range(cols):

            # --- горизонтальные дороги ---
            if j + 1 < cols:
                p1, p2 = nodes[i][j], nodes[i][j+1]

                is_border = (i == 0 or i == rows-1)      # верх/низ
                if not is_border and random.random() < SKIP_PROB:
                    pass  # пропускаем ВНУТРЕННЮЮ дорогу
                else:
                    roads.append(LineString([p1, p2]))


            # --- вертикальные дороги ---
            if i + 1 < rows:
                p1, p2 = nodes[i][j], nodes[i+1][j]

                is_border = (j == 0 or j == cols-1)      # левый/правый край
                if not is_border and random.random() < SKIP_PROB:
                    pass
                else:
                    if random.random() < config.CURVED_PROB:
                        #roads.append(slightly_noisy_curve(p1, p2, rate=0))
                        roads.append(LineString([p1, p2]))
                    else:
                        roads.append(LineString([p1, p2]))

    return roads