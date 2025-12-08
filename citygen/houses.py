
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, Point
import random
import math
from config import CityConfig


config = CityConfig()


def generate_houses(nodes, cell_size, roads, ax):

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
                    if config.SHOW_LOCAL:
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
                        if config.SHOW_LOCAL:
                            x, y = house.exterior.xy
                            ax.fill(x, y, color="brown", alpha=1, edgecolor="black", linewidth=1)
                            ax.figure.canvas.draw_idle()
                            plt.pause(0.001)
                        cell_houses.append(house)
                        break
    print(len(houses))
    return houses