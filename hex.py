import sys, pygame, time, math

# Number of hexagons on each axis
n_x, n_y = 20, 20
# Radius of and gap between hexagons
r, g = 20, 5

width = int(n_x*(1.5*r+g)+0.5*r+g)+160
height = int(n_y*(2*0.866*r+g)+0.866*r+2*g)
size = width, height
black = 0, 0, 0
grey = 100, 100, 100, 100
white = 255, 255, 255
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255

# Coordinates from index
xord = lambda xi    : (1.5 * xi + 1) * r + (xi + 1) * g
yord = lambda yi, xi: (2*0.866 * yi + 1 + xi % 2) * r + (yi + 1) * g
# Index from coordinates
xi = lambda xord    : (xord - r - g) / (1.5 * r + g)
yi = lambda yord, xi: (yord - (1 + round(xi) % 2) * r - g) / (2*0.866 * r + g)

class HexGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        for i in range(n_x):
            for j in range(n_y):
                self.nodes[(i,j)] = True
        for i in range(n_x):
            for j in range(n_y):
                self.add_hex_edges(i, j)

    def add_hex_edges(self, x, y):
        node_edges = []
        if x % 2 == 0:
            if y > 0:
                if self.nodes[(x, y-1)]: node_edges.append((x, y-1))
                if x > 0:
                    if self.nodes[(x-1, y-1)]: node_edges.append((x-1, y-1))
                if x < n_x - 1:
                    if self.nodes[(x+1, y-1)]: node_edges.append((x+1, y-1))
            if y < n_y - 1:
                if self.nodes[(x, y+1)]: node_edges.append((x, y+1))
            if x > 0:
                if self.nodes[(x-1, y)]: node_edges.append((x-1, y))
            if x < n_x - 1:
                if self.nodes[(x+1, y)]: node_edges.append((x+1, y))
        else:
            if y < n_y - 1:
                if self.nodes[(x, y+1)]: node_edges.append((x, y+1))
                if x > 0:
                    if self.nodes[(x-1, y+1)]: node_edges.append((x-1, y+1))
                if x < n_x - 1:
                    if self.nodes[(x+1, y+1)]: node_edges.append((x+1, y+1))
            if y > 0:
                if self.nodes[(x, y-1)]: node_edges.append((x, y-1))
            if x > 0:
                if self.nodes[(x-1, y)]: node_edges.append((x-1, y))
            if x < n_x - 1:
                if self.nodes[(x+1, y)]: node_edges.append((x+1, y))
        self.nodes[(x,y)] = True
        self.edges[(x,y)] = node_edges

    def remove_hex_edges(self, x, y):
        for node in self.edges[(x,y)]:
            self.edges[node].remove((x,y))
        self.nodes[(x,y)] = False
        self.edges[(x,y)] = []

    def route(self, start, end):
        x0, y0 = start
        x1, y1 = end

        prev = [[None for j in range(n_y)] for i in range(n_x)]
        dist = [[-1 for j in range(n_y)] for i in range(n_x)]
        dist[x0][y0] = 0
        queue = [start]

        while queue:
            curr = queue.pop(0)
            for node in self.edges[curr]:
                if prev[node[0]][node[1]] is None:
                    queue.append(node)
                if dist[node[0]][node[1]] == -1 or \
                   dist[node[0]][node[1]] > dist[curr[0]][curr[1]]:
                    dist[node[0]][node[1]] = dist[curr[0]][curr[1]] + 1
                    prev[node[0]][node[1]] = curr

        if prev[x1][y1] is None:
            return None

        route = []
        curr = end
        while curr != start:
            curr = prev[curr[0]][curr[1]]
            route.insert(0, curr)
        route.pop(0)
        
        return route

class Buttons:
    def __init__(self, graph):
        self.graph = graph
        self.current = white
        self.start_point = None
        self.end_point = None
        self.font = pygame.font.SysFont(None, 24)
        self.draw()

    def draw(self):
        pygame.draw.rect(screen, black, 
            pygame.Rect((width-130, 45), (130, 50)))
        pygame.draw.rect(screen, grey if self.current == white else black, 
            pygame.Rect((width-130, 95), (100, 30)))
        pygame.draw.rect(screen, grey if self.current == green else black, 
            pygame.Rect((width-130, 145), (100, 30)))
        pygame.draw.rect(screen, grey if self.current == blue else black, 
            pygame.Rect((width-130, 195), (100, 30)))
        pygame.draw.rect(screen, black, 
            pygame.Rect((width-130, 245), (100, 30)))
        screen.blit(self.font.render('Find Route', True, red), (width-120, 50))
        screen.blit(self.font.render('On / Off', True, white), (width-120, 100))
        screen.blit(self.font.render('Start Point', True, green), (width-120, 150))
        screen.blit(self.font.render('End Point', True, blue), (width-120, 200))
        screen.blit(self.font.render('RESET', True, white), (width-120, 250))

    def press(self, y):
        if 45 <= y <= 75:
            return self.route()
        if 95 <= y <= 125:
            self.current = white
            self.draw()
        if 145 <= y <= 175:
            self.current = green
            self.draw()
        if 195 <= y <= 225:
            self.current = blue
            self.draw()
        if 245 <= y <= 275:
            return 'reset'
        
    def route(self):
        if self.start_point is None or self.end_point is None:
            screen.blit(pygame.font.SysFont(None, 16).render(
                'Select Start and End', True, red), (width-120, 70))
            return
        route = self.graph.route(self.start_point, self.end_point)
        if route is None:
            pygame.draw.rect(screen, black, 
                pygame.Rect((width-130, 45), (130, 50)))
            screen.blit(pygame.font.SysFont(None, 16).render(
                'No Route Available', True, red), (width-120, 70))
            return
        return route


def draw_hex_from_coords(centre, colour):
    x, y = centre
    pygame.draw.polygon(screen, colour, [
        (x-r,     y), 
        (x-r*0.5, y-r*0.866), 
        (x+r*0.5, y-r*0.866),
        (x+r,     y),
        (x+r*0.5, y+r*0.866),
        (x-r*0.5, y+r*0.866)
    ])

def draw_hex(centre, colour):
    if centre is None:
        return
    x, y = centre
    draw_hex_from_coords((xord(x), yord(y, x)), colour)

def draw_hover_circle(centre):
    if centre is None:
        return
    x, y = centre
    pygame.draw.circle(screen, grey, (xord(x), yord(y, x)), 0.8*r)


def get_hex_under_mouse():
    # Gives the index of which hexagon the mouse is over
    def dist_from_centre(x,y):
        return math.sqrt((x-round(x))**2 + (y-round(y))**2)

    xord, yord = pygame.mouse.get_pos()
    x = xi(xord)
    y = yi(yord, x)

    if dist_from_centre(x,y) > 0.4: return None
    if round(x) < 0 or round(x) > n_x - 1: return None
    if round(y) < 0 or round(y) > n_y - 1: return None
    return round(x), round(y)

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(size)
    screen.fill(black)

    graph = HexGraph()
    buttons = Buttons(graph)

    for i in range(n_x):
        for j in range(n_y):
            draw_hex((i, j), white)
            # font = pygame.font.SysFont(None, 16)
            # img = font.render(str(len(graph.edges[(i,j)])), True, black)
            # screen.blit(img, (xord(i), yord(j, i)))

    route = []
    hover_prev = None
    hover_prev_colour = white
    while True:
        hover = get_hex_under_mouse()
        if hover != hover_prev:
            draw_hex(hover_prev, hover_prev_colour)
        if hover is not None:
            draw_hover_circle(hover)
            hover_prev = hover
            hover_prev_colour = white if graph.nodes[hover] else black
            if hover == buttons.start_point:
                hover_prev_colour = green
            if hover == buttons.end_point:
                hover_prev_colour = blue
            if hover in route:
                hover_prev_colour = red

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN: 
                if hover is not None:
                    if buttons.current == white:
                        graph.remove_hex_edges(*hover)
                        draw_hex(hover, black)
                    elif buttons.current == green:
                        draw_hex(buttons.start_point, white)
                        buttons.start_point = hover
                        draw_hex(hover, green)
                    elif buttons.current == blue:
                        draw_hex(buttons.end_point, white)
                        buttons.end_point = hover
                        draw_hex(hover, blue)
                else:
                    x, y = pygame.mouse.get_pos()
                    if width - 130 <= x <= width - 30:
                        route = buttons.press(y)
                        if route is None:
                            route = [] 
                        else:
                            for node in route:
                                draw_hex(node, red)
        
        pygame.display.flip()