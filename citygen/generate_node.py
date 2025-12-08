import random
from config import CityConfig


config = CityConfig()


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

def generate_nodes(grid, base=300.0, spread=157, min_d=200, max_d=500):
    xs = random_steps(grid, base, spread)
    ys = random_steps(grid, base, spread)

    nodes = []

    for i in range(grid+1):
        row = []
        for j in range(grid+1):

            # добавляем шум
            x = xs[j] + random.uniform(-config.OFFSET, config.OFFSET)
            y = ys[i] + random.uniform(-config.OFFSET, config.OFFSET)

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