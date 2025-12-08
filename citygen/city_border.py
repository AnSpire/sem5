from shapely import Polygon

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