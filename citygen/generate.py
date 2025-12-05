import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.affinity import translate
import matplotlib.pyplot as plt
import math
import random
"""
РАЗНЫЙ РАЗМЕР КВАРТАЛОВ
"""

GRID = 6
m = 15
CELL = 20 * m
OFFSET = 1.7 * m
CURVED_PROB = 0.5


def random_steps(grid, base, spread):
    # base — средний размер квартала
    # spread — насколько кварталы могут отличаться
    steps = [base + random.uniform(-spread, spread) for _ in range(grid)]
    coords = [0]
    for s in steps:
        coords.append(coords[-1] + s)
    return coords


# def generate_nodes(grid, base=400, spread=157):
#     xs = random_steps(grid, base, spread)
#     ys = random_steps(grid, base, spread)
#
#     nodes = []
#     for i in range(grid+1):
#         row = []
#         for j in range(grid+1):
#             # Добавляем случайное отклонение, если хочешь шум
#             x = xs[i] + random.uniform(-OFFSET, OFFSET)
#             y = ys[j] + random.uniform(-OFFSET, OFFSET)
#             row.append((x, y))
#         nodes.append(row)
#     return nodes

def generate_nodes(grid, base=300, spread=157, min_d=200, max_d=500):
    xs = random_steps(grid, base, spread)
    ys = random_steps(grid, base, spread)

    nodes = []

    for i in range(grid+1):
        row = []
        for j in range(grid+1):

            # добавляем шум
            x = xs[j] + random.uniform(-OFFSET, OFFSET)
            y = ys[i] + random.uniform(-OFFSET, OFFSET)

            # --- регулируем сторону по X ---
            if j > 0:
                prev_x, prev_y = row[j-1]
                dx = x - prev_x

                # если сторона клетки меньше минимума → удлиняем
                if dx < min_d:
                    x = prev_x + min_d
                # если больше максимума → укорачиваем
                if dx > max_d:
                    x = prev_x + max_d

            # --- регулируем сторону по Y ---
            if i > 0:
                prev_x, prev_y = nodes[i-1][j]
                dy = y - prev_y

                if dy < min_d:
                    y = prev_y + min_d
                if dy > max_d:
                    y = prev_y + max_d

            row.append((x, y))

        nodes.append(row)

    return nodes



def get_city_border(nodes):
    rows = len(nodes)
    cols = len(nodes[0])

    # Обход сетки по периметру
    border_coords = []

    # верхняя сторона
    for j in range(cols):
        border_coords.append(nodes[0][j])

    # правая
    for i in range(1, rows):
        border_coords.append(nodes[i][cols-1])

    # нижняя (в обратном порядке)
    for j in range(cols-2, -1, -1):
        border_coords.append(nodes[rows-1][j])

    # левая
    for i in range(rows-2, 0, -1):
        border_coords.append(nodes[i][0])

    return Polygon(border_coords)


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
                    if random.random() < CURVED_PROB:
                        #roads.append(slightly_noisy_curve(p1, p2, rate=0))
                        roads.append(LineString([p1, p2]))
                    else:
                        roads.append(LineString([p1, p2]))

    return roads




BRANCH_PROB = 0.65  # вероятность появления отростка
BRANCH_MIN = 0.2  # минимальная доля длины блока
BRANCH_MAX = 0.45  # максимальная

def generate_branches(roads, city_polygon):

    branches = []

    for road in roads:
        if not isinstance(road, LineString):
            continue

        # середина дороги
        mid = road.interpolate(0.4, normalized=True)
        x, y = mid.x, mid.y

        if random.random() > BRANCH_PROB:
            continue

        dx = road.coords[1][0] - road.coords[0][0]
        dy = road.coords[1][1] - road.coords[0][1]
        nx, ny = -dy, dx
        length = math.sqrt(nx*nx + ny*ny)
        nx, ny = nx/length, ny/length

        L = CELL * random.uniform(BRANCH_MIN, BRANCH_MAX)
        if random.random() < 0.5:
            L = -L

        p2 = (x + nx*L, y + ny*L)
        branch = LineString(slightly_noisy_curve((x, y), p2, rate=random.randint(0, 6)))

        if not city_polygon.contains(branch):
            continue

        branches.append(branch)

    return branches




# ------------------------
#     ГЕНЕРАЦИЯ ДОМОВ
# ------------------------

from shapely.geometry import Polygon

from shapely.geometry import Polygon, LineString
import random
import math

def generate_houses(nodes, cell_size, roads):

    houses = []

    rows = len(nodes)-1
    cols = len(nodes[0])-1

    # параметры внутренней застройки
    SQ = cell_size * 0.11            # размер квадратного дома
    SQ_SPACING = cell_size * 0.02

    # параметры дорожных домов
    EL_W = cell_size * 0.27          # длина вдоль дороги
    EL_H = cell_size * 0.12          # ширина поперёк дороги
    ROAD_OFFSET = cell_size * 0.14   # отступ от дороги
    ROAD_SPACING = cell_size * 0.10

    EDGE_EPS = cell_size * 0.04      # насколько близко дорога должна быть к ребру квартала

    # --- основной цикл по кварталам ---
    for i in range(rows):
        for j in range(cols):

            # Берём 4 угла клетки
            p_tl = nodes[i][j]
            p_tr = nodes[i][j+1]
            p_br = nodes[i+1][j+1]
            p_bl = nodes[i+1][j]

            # Многоугольник квартала
            cell = Polygon([p_tl, p_tr, p_br, p_bl])

            # 4 ребра квартала
            edges = [
                LineString([p_tl, p_tr]),   # верх
                LineString([p_tr, p_br]),   # правый
                LineString([p_br, p_bl]),   # низ
                LineString([p_bl, p_tl])    # левый
            ]

            cell_houses = []
            # 2) Длинные дома вдоль дорог — БЕЗ random, равномерно вдоль ребра
            for edge in edges:

                (x1, y1), (x2, y2) = edge.coords[:2]
                dx, dy = x2 - x1, y2 - y1
                L = math.hypot(dx, dy)
                if L == 0:
                    continue

                ux, uy = dx / L, dy / L  # направление вдоль дороги
                nx, ny = -uy, ux  # нормаль внутрь квартала

                step = 0.023 * L  # расстояние между домами (15% от ребра)
                house_len = EL_W  # ширина дома вдоль дороги
                total = 0.3 * L  # начальный отступ слева — как ты хотел

                while total + house_len < L * 0.95:  # пока не вышли за правый край
                    # центр дома вдоль дороги
                    bx = x1 + ux * total
                    by = y1 + uy * total
                    #print(edge, bx, by, ux, uy, total)
                    #input()
                    # ПРОВЕРКА нормали — ключевой фикс!
                    testx = bx + nx * ROAD_OFFSET
                    testy = by + ny * ROAD_OFFSET
                    if not Point(testx, testy).within(cell):
                        nx, ny = -nx, -ny  # разворачиваем внутрь

                    # итоговая точка дома
                    hx = bx + nx * ROAD_OFFSET
                    hy = by + ny * ROAD_OFFSET

                    # строим дом ориентированный по дорожному направлению
                    house = Polygon([
                        (hx - ux * EL_W / 2 - nx * EL_H / 2, hy - uy * EL_W / 2 - ny * EL_H / 2),
                        (hx + ux * EL_W / 2 - nx * EL_H / 2, hy + uy * EL_W / 2 + -ny * EL_H / 2),
                        (hx + ux * EL_W / 2 + nx * EL_H / 2, hy + uy * EL_W / 2 + ny * EL_H / 2),
                        (hx - ux * EL_W / 2 + nx * EL_H / 2, hy - uy * EL_W / 2 + ny * EL_H / 2)
                    ])

                    # проверяем вписывание
                    # if house.within(cell):
                    #     houses.append(house)
                        #cell_houses.append(house)

                    houses.append(house)
                    x, y = house.exterior.xy
                    ax.fill(x, y, color="brown", alpha=1, edgecolor="black", linewidth=1)
                    ax.figure.canvas.draw_idle()
                    plt.pause(0.001)
                    total += house_len + step  # следующий дом = отступ от предыдущего

            #───────────────────────────────────────────────
            # 3) Квадратные дома в центре квартала
            NUM_SQ = random.randint(5,9)

            # берём bounding box ячейки
            min_x = min(p_tl[0],p_tr[0],p_bl[0],p_br[0])
            max_x = max(p_tl[0],p_tr[0],p_bl[0],p_br[0])
            min_y = min(p_tl[1],p_tr[1],p_bl[1],p_br[1])
            max_y = max(p_tl[1],p_tr[1],p_bl[1],p_br[1])
            for _ in range(NUM_SQ):
                for _attempt in range(15):
                    hx = random.uniform(min_x+SQ_SPACING, max_x-SQ-SQ_SPACING)
                    hy = random.uniform(min_y+SQ_SPACING, max_y-SQ-SQ_SPACING)
                    house = Polygon([
                        (hx,hy),
                        (hx+SQ,hy),
                        (hx+SQ,hy+SQ),
                        (hx,hy+SQ)
                    ])

                    if house.within(cell) \
                    and all(house.distance(h)>SQ_SPACING for h in houses):
                        houses.append(house)
                        x, y = house.exterior.xy
                        ax.fill(x, y, color="brown", alpha=1, edgecolor="black", linewidth=1)
                        ax.figure.canvas.draw_idle()
                        plt.pause(0.001)
                        cell_houses.append(house)
                        break
    print(len(houses))
    return houses





nodes = generate_nodes(GRID, CELL)
CITY_BORDER = get_city_border(nodes)
roads = generate_roads(nodes)
all_roads = roads

# === ЭТАП 1 — рисуем и показываем только дороги ===
plt.ion()
fig, ax = plt.subplots(figsize=(10,10))




for r in all_roads:
    x, y = r.xy
    ax.plot(x, y, color="black", linewidth=1)

ax.set_aspect("equal")
plt.show()
plt.pause(0.1)

# === ЭТАП 2 — дорисовываем дома ===
houses = generate_houses(nodes, CELL, all_roads)

# for house in houses:
#     x, y = house.exterior.xy
#     ax.fill(x, y, color="brown", alpha=1, edgecolor="black", linewidth=1)

# узлы поверх
for row in nodes:
    for x, y in row:
        ax.scatter(x, y, color="red", s=10)

plt.draw()
plt.pause(15)         # обновление окна


# print("Нажми Enter чтобы закрыть окно...")
# input()


