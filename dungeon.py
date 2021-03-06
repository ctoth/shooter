from logging import getLogger
logger = getLogger('dungeon')
import random
import itertools
import sys


def neighbors(n):
    x, y = n
    return (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)

    
def _AStar(start, goal):
    def heuristic(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    def reconstructPath(n):
        if n == start:
            return [n]
        return reconstructPath(cameFrom[n]) + [n]

    closed = set()
    open = set()
    open.add(start)
    cameFrom = {}
    gScore = {start: 0}
    fScore = {start: heuristic(start, goal)}

    while open:
        current = None
        for i in open:
            if current is None or fScore[i] < fScore[current]:
                current = i

        if current == goal:
            return reconstructPath(goal)

        open.remove(current)
        closed.add(current)

        for neighbor in neighbors(current):
            if neighbor in closed:
                continue
            g = gScore[current] + 1

            if neighbor not in open or g < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = g
                fScore[neighbor] = gScore[neighbor] + heuristic(neighbor, goal)
                if neighbor not in open:
                    open.add(neighbor)
    return ()


def generate(cellsX, cellsY, cellSize=5):
    # 1. Divide the map into a grid of evenly sized cells.

    class Cell(object):
        def __init__(self, x, y, id):
            self.x = x
            self.y = y
            self.id = id
            self.connected = False
            self.connectedTo = []
            self.room = None

        def connect(self, other):
            self.connectedTo.append(other)
            other.connectedTo.append(self)
            self.connected = True
            other.connected = True

    cells = {}
    for y in range(cellsY):
        for x in range(cellsX):
            c = Cell(x, y, len(cells))
            cells[(c.x, c.y)] = c
    # 2. Pick a random cell as the current cell and mark it as connected.
    current = lastCell = firstCell = random.choice(list(cells.values()))
    print(current)
    current.connected = True

    # 3. While the current cell has unconnected neighbor cells:
    def getNeighborCells(cell):
        for x, y in ((-1, 0), (0, -1), (1, 0), (0, 1)):
            try:
                yield cells[(cell.x + x, cell.y + y)]
            except KeyError:
                continue

    while True:
        unconnected = [x for x in getNeighborCells(current) if not x.connected]
        if not unconnected:
            break

        # 3a. Connect to one of them.
        neighbor = random.choice(unconnected)
        current.connect(neighbor)

        # 3b. Make that cell the current cell.
        current = lastCell = neighbor

    # 4. While there are unconnected cells:
    while [x for x in cells.values() if not x.connected]:
        # 4a. Pick a random connected cell with unconnected neighbors and connect to one of them.
        candidates = []
        connected_cells = [i for i in cells.values() if i.connected]
        #print("Connected cells" + str(connected_cells))
        for cell in connected_cells:
            neighbors = [x for x in getNeighborCells(cell) if not x.connected]
            if not neighbors:
                continue
            candidates.append((cell, neighbors))
        cell, neighbors = random.choice(candidates)
        cell.connect(random.choice(neighbors))

    # 5. Pick 0 or more pairs of adjacent cells that are not connected and connect them.
    extraConnections = random.randint((int((cellsX + cellsY) / 4)), int(((cellsX + cellsY) / 2)))
    maxRetries = 10
    while extraConnections > 0 and maxRetries > 0:
        cell = random.choice(list(cells.values()))
        neighbors = list(getNeighborCells(cell))
        if not neighbors:
            break
        neighbor = random.choice(neighbors)
        if cell in neighbor.connectedTo:
            maxRetries -= 1
            continue
        cell.connect(neighbor)
        extraConnections -= 1

    # 6. Within each cell, create a room of random shape
    rooms = []
    room_coords = []
    exits= set()
    corridors = []
    for cell in cells.values():
        width = random.randint(3, cellSize - 2)
        height = random.randint(3, cellSize - 2)
        x = (cell.x * cellSize) + random.randint(1, cellSize - width - 1)
        y = (cell.y * cellSize) + random.randint(1, cellSize - height - 1)
        room_size = (
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
        )
        room_coords.append(room_size)
        logger.info("Creating room at %d, %d of size %d by %d" % (x, y, width, height))
        floorTiles = []
        for i in range(width):
            for j in range(height):
                floorTiles.append((x + i, y + j))
        cell.room = floorTiles
        rooms.append(floorTiles)

    # 7. For each connection between two cells:
    connections = {}
    for c in cells.values():
        for other in c.connectedTo:
            connections[tuple(sorted((c.id, other.id)))] = (c.room, other.room)
    for a, b in connections.values():
        # 7a. Create a random corridor between the rooms in each cell.
        start = random.choice(a)
        end = random.choice(b)

        corridor = []
        for tile in _AStar(start, end):
            if tile not in a and not tile in b:
                corridor.append(tile)
        rooms.append(corridor)
        exits.add(corridor[0])
        exits.add(corridor[-1])
        corridors.append(corridor)
    # 8. Place staircases in the cell picked in step 2 and the lest cell visited in step 3b.
    stairsUp = random.choice(firstCell.room)
    stairsDown = random.choice(lastCell.room)

    # create tiles
    tiles = {}
    tilesX = cellsX * cellSize
    tilesY = cellsY * cellSize
    for x in range(tilesX):
        for y in range(tilesY):
            tiles[(x, y)] = "w"
    for xy in itertools.chain.from_iterable(rooms):
        tiles[xy] = "r"
        if xy in exits:
            tiles[xy] = 'e'
    # every tile adjacent to a floor is a wall
    def getNeighborTiles(xy):
        tx, ty = xy
        for x, y in ((-1, -1), (0, -1), (1, -1),
                     (-1, 0), (1, 0),
                     (-1, 1), (0, 1), (1, 1)):
            try:
                yield tiles[(tx + x, ty + y)]
            except KeyError:
                continue

    for xy, tile in dict(tiles).items():
        if not tile in ('r', 'e') and "r" in getNeighborTiles(xy):
            tiles[xy] = "w"
    tiles[stairsUp] = "u"
    tiles[stairsDown] = "d"
    return tiles, room_coords, corridors


if __name__ == "__main__":
    generate(8, 5, 8)