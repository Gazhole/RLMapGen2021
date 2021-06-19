# -*- coding: utf-8 -*-


'''
TO DO
'''

# min room size?

# Item placement
# Mob placement
# Output of dungeon schematics.
# Schematic decoding functions (re-usable).



'''
IMPORTS
'''

import numpy as np
from random import choice, randint, seed, random, shuffle
from math import sqrt



'''
DISPLAY
'''

def print_map(m):
    
    for y in range(0,m.h):
        print("")
        for x in range(0,m.w):

            door = m.doors[y,x]
            tile = m.walkable[y,x]
            stair_in = m.stair_in == (y,x)
            stair_out = m.stair_out == (y,x)
            
            if door:
                char = "+"
            elif stair_in:
                char = "<"
            elif stair_out:
                char = ">"
            elif tile == 1:
                char = " "
            else:
                char = "#"
                
       
            print(char,end=" ")

'''
TOP LEVEL FUNCTIONS
'''

def main() -> None:
    m = map_gen(width=50,height=50,num_areas=25,room_max_size=10)
    print_map(m)


def map_gen(width,height,num_areas=False,room_max_size=False):
    
    
    '''
    COOL MAPS:
        0.5338059017751996
        0.518796779726087
        0.6651387457508565
        0.5407171628896985
        0.7575976643019975
        
        
    '''
    
    rng = random()
    seed(0.5407171628896985)
    seed(rng)
    print(rng)
        
    if not num_areas:
        num_areas = int((width + height) / 4)

    if not room_max_size:
        room_max_size = 10

    m = GameMap(width,height)

    
    '''
    PLACE ROOMS
    1 - Place a room in the middle of the map.
    2 - Pick a wall on one edge of that room, and a tile on that wall.
    3 - Pick a cardinal direction.
    4 - If viable, create a door at that location.
    5 - In the same direction, create a room/corridor on the other side of the door.
    6 - Check that room/corridor will fit (doesnt intersect another area).
    7 - If it will fit, carve out a basic room, or paste in a prefab of same size.
    8 - Pick another random wall from any existing areas and repeat steps 2-7.
    '''    
    place_rooms(m,num_areas,room_max_size)


    '''
    FIX DEAD ENDS
    9 - Now find any dead end corridors.
    10 - If a dead end is separated from a room by a single wall tile, knock thru.
    11 - If 10 not possible fill the dead end with wall.
    12- Repeat step 11 until all dead ends are gone.
    '''      
    fix_dead_ends(m)


    '''
    MAKE LOOPS
    13 - Get all tiles in a wall of a cardinal direction.
    14 - Run through those tiles and look for ones aligned on the opposing wall
    15 - Check whether the straight line between them is not intersecting a room
    16 - Check whether the tiles are a good walkable distance away from eachother
    17 - Dig them out
    18 - If any of the above is false, move to the next tile.
    19 - If its not possible from S->N walls, try E->W.
    20 - If this also is not possible, look for rooms separated by a single wall.
    21 - If any are found, knock through assuming they are a good walking distance.
    '''
    make_loops(m)

    
    '''
    PLACE STAIRS
    
    '''
    
    place_stairs(m)


    '''
    REMOVE DOORS IN CORRIDORS
    
    '''

    remove_doors_in_corridors(m)
    
    return m


    

    
'''
MAP GENERATION
'''

def place_rooms(m,num,room_max_size):
    # Load in all prefabs
    prefab_pool = load_prefabs()
    
    # Place rooms & corridors
    for i in range(num):
        add_area(m, room_max_size, prefab_pool)


def add_area(m, room_max_size, prefab_pool):
    placed = False
    is_first_room = not m.rooms
    
    while not placed:
        
        
        # What type of area?
        mode = choice(["corridor", "room"])        
        if not is_first_room:
            seed_room = choice(m.rooms)            
            if seed_room.w == 1 or seed_room.h == 1:
                mode = "room"

        # Which direction?
        dx, dy = choice([(0,1), (0,-1), (1,0), (-1,0)])

        # Room size
        rw,rh = gen_room_size(mode,room_max_size,dx,dy)

        # Check if we have a prefab of the same size, put them in a list
        matching_prefabs = get_matching_prefabs(prefab_pool, rw, rh)
        if matching_prefabs:
            prefab_template = choice(matching_prefabs)
        else:
            prefab_template = False
        
        
        # Get the position of the area
        if is_first_room:

            rx1, ry1, rx2, ry2 = first_room_coords(m.w,m.h,rw,rh)
        
        else:  # If this is not the first room, find a wall and join one on

            wall = choice(seed_room.walls)
                
            door_y,door_x = choice(wall)  # A random coord from a random wall
        
            # Pick a random tile along the new room wall for the entrance
            x_off,y_off = get_door_offsets(dx,dy,rw,rh,prefab_template)        
            
            rx1, ry1, rx2, ry2 = next_room_coords(rw,rh,dx,dy,door_x,door_y,
                                                  x_off, y_off)


        # Create the room object from a prefab, or basic empty room if no match
        if prefab_template:
            r = PreFab(rx1, ry1, rx2, ry2, prefab_template)
        else:
            r = Room(rx1, ry1, rx2, ry2)
        
        
        # Try to place it
        placed = m.carve_room(r)
        
        
        # Door stuff
        if placed and not is_first_room:
            place_door(door_x, door_y, m)
        
            
        # Remove prefab from pool if used
        if placed and prefab_template:
            prefab_pool.remove(prefab_template)


def gen_room_size(mode,room_max_size,direction_x=False,direction_y=False):
    
    if mode == "corridor":
        if direction_x != 0:
            w = randint(6,12)
            h = 1
            
        if direction_y != 0:
            w = 1
            h = randint(6,12)
        
    else:
        w = randint(3,room_max_size)
        h = randint(3,room_max_size)
            
    return w,h


def first_room_coords(map_w, map_h, room_w, room_h):
    room_x1 = int(map_w/2) - int(room_w / 2)
    room_y1 = int(map_h/2) - int(room_h / 2)
    
    room_x2 = room_x1 + room_w
    room_y2 = room_y1 + room_h
    
    return room_x1, room_y1, room_x2, room_y2


def next_room_coords(room_w, room_h, direction_x, direction_y, door_x, door_y, 
                    offset_x, offset_y):
    # Set the starting coord of new room next to door in the chosen
    # direction, and offset the room position so not always in (0,0)
    
    if direction_x < 0:
        room_x1 = 1 + door_x + (1 * direction_x) + offset_x
    else:
        room_x1 = door_x + (1 * direction_x) + offset_x
    
    if direction_y < 0:
        room_y1 = 1 + door_y + (1 * direction_y) + offset_y
    else:
        room_y1 = door_y + (1 * direction_y) + offset_y            
    
    
    # Other boundary is start + w/h
    if direction_x < 0:
        room_x2 = room_x1 - room_w
    else:
        room_x2 = room_x1 + room_w
        
    if direction_y < 0:
        room_y2 = room_y1 - room_h
    else:
        room_y2 = room_y1 + room_h

    return room_x1, room_y1, room_x2, room_y2



def get_prefab_entrance(prefab_template, direction_x, direction_y):
 
    if not direction_x:
        if direction_y == 1:
            y = 0
        if direction_y == -1:
            y = prefab_template.h-1

        x = randint(0,prefab_template.w-1)
        while not prefab_template.walkable[y,x]:
            x = randint(0,prefab_template.w-1)
        
        return x


    if not direction_y:
        if direction_x == 1:
            x = 0
        if direction_x == -1:
            x = prefab_template.w-1
        
        y = randint(0,prefab_template.h-1)
        while not prefab_template.walkable[y,x]:
            y = randint(0,prefab_template.h-1)
    
        return y


def get_door_offsets(direction_x, direction_y, room_w, room_h, prefab_template):
    # If the dx/dy is zero we can offset where the door enters new room
    if not direction_x:
        if prefab_template:
            offset_x = -get_prefab_entrance(prefab_template, direction_x, direction_y)
        else:
            offset_x = -randint(0,room_w-1)
    else:
        offset_x = 0
    
    if not direction_y:
        if prefab_template:
            offset_y = -get_prefab_entrance(prefab_template, direction_x, direction_y)
        else:
            offset_y = -randint(0,room_h-1)
    else:
        offset_y = 0

    return offset_x, offset_y



def fix_dead_ends(m):
    # Potential loops from dead ends    
    ploop_ids = [105,135,300,450]
    ploops = get_matching_tiles(m, ploop_ids)
    while ploops:
        for ploop in ploops:
            y,x = ploop
            place_door(x,y,m)
            
        ploops = get_matching_tiles(m, ploop_ids)

    # Fill remaining dead ends.
    dead_end_ids = [18,19,22,23,24,25,48,52,88,89,144,208,276,304,308,400,464]
    dead_ends = get_matching_tiles(m,dead_end_ids)
    while dead_ends:
        for dend in dead_ends:
            y,x = dend
            create_wall_tile(x,y,m)
            
        dead_ends = get_matching_tiles(m, dead_end_ids)


def make_loops(m):

    func = [make_v_loops, make_h_loops]

    shuffle(func)

    f1 = func[0]
    f2 = func[1]
    
    loop_made = f1(m)

    if not loop_made:
        loop_made = f2(m)

    if not loop_made:
        join_rooms(m)        


def make_v_loops(m):

    # pick a tile in south wall
    # do any tiles in a north wall share the same x coordinate (opposite)
    # check whether the straight line between them is not intersecting a room
    # check whether the tiles are a good walkable distance away from eachother
    # dig them out
    # if any of the above is false, move to the next tile.
    
    s_walls = get_matching_tiles(m, [7])
    n_walls = get_matching_tiles(m, [448])
    
    for s_tile in s_walls:
        sy,sx = s_tile
        for n_tile in n_walls:
            ny,nx = n_tile
            
            if dist_between(sx, sy, nx, ny) <= 20:
                if sx == nx and line_of_dig(m, sx, sy, nx, ny):
                    if calc_dijkstra(m, sx, sy)[ny,nx] >= 50:
                        place_door(sx, sy, m)
                        place_door(nx, ny, m)
                        for y in range(min(sy,ny), max(sy,ny)+1):
                            m.walkable[y,sx] = 1
                        return True
    return False


def make_h_loops(m):    
    e_walls = get_matching_tiles(m, [73])
    w_walls = get_matching_tiles(m, [292])
    
    for e_tile in e_walls:
        ey,ex = e_tile
        for w_tile in w_walls:
            wy,wx = w_tile
            
            if dist_between(ex, ey, wx, wy) <= 20:
                if ey == wy and line_of_dig(m, ex, ey, wx, wy):
                    if calc_dijkstra(m, ex, ey)[wy,wx] >= 50:
                        place_door(ex, ey, m)
                        place_door(wx, wy, m)
                        for x in range(min(ex,wx), max(ex,wx)+1):
                            m.walkable[ey,x] = 1
                        return True
    return False


def line_of_dig(m,x1,y1,x2,y2):
    frst=True
    
    if dist_between(x1,y1,x2,y2)==1:
        return True
    
    if x1 < x2:
        sx,dx=1,x2-x1
    else:
        sx,dx=-1,x1-x2
        
        
    if y1<y2:
        sy,dy=1,y2-y1
    else:
        sy,dy=-1,y1-y2
        
    err = dx-dy
   	
    while not(x1==x2 and y1==y2):
        
        if not frst and is_walkable(x1,y1,m):
            return False
        
        frst,e2=False,err*2
		
        if e2>-dy:
            err-=dy
            x1+=sx
            
        if e2<dx:
            err+=dx
            y1+=sy
            
    return True
        

def join_rooms(m):    
    # Knock through some extra doors.
    # Use Dijkstra to find the tiles which are furthest apart in steps
    # but still separated by a single wall.
    # Take the tile either side of the wall, calc dist > 10 and knock if true

    v_walls = get_matching_tiles(m, [365,297,108])
    if v_walls:
        for tile in v_walls:

            ty,tx = tile
            
            lx = tx
            ly = ty-1
            
            rx = tx
            ry = ty+1
            
            dijk = calc_dijkstra(m, lx, ly)
            distance = dijk[ry,rx]
            
            if distance > 20:    
                place_door(tx,ty,m)                
                
                
    h_walls = get_matching_tiles(m, [455,387,198])        
    if h_walls:
        for tile in h_walls:

            ty,tx = tile
            
            ax = tx-1
            ay = ty

            bx = tx+1
            by = ty
            
            dijk = calc_dijkstra(m, ax, ay)
            distance = dijk[by,bx]
                            
            if distance > 20:
                place_door(tx,ty,m)


def remove_doors_in_corridors(m):
    # Removes doors in the middle of a corridor, also from top of U loops.
    targets = [56,146,61,376,406,211,60,312,57,120,150,147,210,402]

    cand = get_matching_tiles(m, targets)

    for tile in cand:
        y,x = tile
        if m.doors[y,x]:
            m.doors[y,x] = 0



def place_stairs(m):
    
    in_y,in_x = 1,1
    while get_tile_id(m,in_x,in_y) != 511:
        in_y,in_x = randint(2,m.h-2),randint(2,m.w-2)
    
    
    dijk = calc_dijkstra(m, in_x, in_y)
        
    far_dist = 0
    far_y = in_y
    far_x = in_x
    for y in range(1,m.h):
        for x in range(1,m.w):
            if is_walkable(x, y, m) and get_tile_id(m, x, y) == 511:
                new_dist = dijk[y,x]
                if new_dist > far_dist:
                    far_dist = new_dist
                    far_y = y
                    far_x = x

    m.stair_in = (in_y,in_x)
    m.stair_out = (far_y,far_x)
    


'''
DIJKSTRA
'''

def calc_dijkstra(m,tx,ty):
    dijk = np.full(shape=(m.h,m.w), fill_value=-1, dtype=int)
    cells = list()
    cell_queue = list()
    step = 0
    
    cells.append((ty, tx))
    dijk[ty,tx] = 0

    x_mod = [0,1,0,-1]
    y_mod = [-1,0,1,0]
    
    while len(cells) > 0:
        step += 1
        cell_queue = list()
       
        for c in cells:
            cy,cx = c
            for i in range(0,4):
                dx = cx + x_mod[i]
                dy = cy + y_mod[i]
                
                if in_bounds(dx, dy, m) and dijk[dy,dx] == -1:
                    dijk[dy,dx] = step
                    if is_walkable(dx,dy,m):
                        cell_queue.append((dy, dx))
        cells = [c for c in cell_queue]
    
    return dijk



'''
BITMASK
'''

def get_matching_tiles(m,ids):
    # Return a list of all (y,x) coordinates in map which match tile ids
    tiles = list()

    for x in range(1,m.w-1):
        for y in range(1,m.h-1):
            if get_tile_id(m,x,y) in ids:
                tiles.append((y,x))
    
    return tiles


def get_tile_id(m,x,y):
    # Tile ID is the sum of the 3x3 grid of masked values as to whether 
    # the tile and surrounding tiles are walkable.
    cell = get_cell(m,x,y)
    mask = get_mask(cell)
     
    tid = 0
    
    for row in mask:
        for val in row:
            tid += val
            
    return tid


def get_mask(cell):
    # 3x3 masked map of walkable tiles of cell and surrounding 8 cells.
    # If walkable, that mask position applies, if not, it is 0
    #mask = np.array([[1,2,4],
    #                 [8,16,32],
    #                 [64,128,256]])

    mask = np.array([[64,8,1],
                     [128,16,2],
                     [256,32,4]])
    
    results = np.zeros(shape=(3,3), dtype=int)
        
    for x in range(0,3):
        for y in range(0,3):
            results[y,x] = cell[y,x] * mask[y,x]
    
    return results
            

def get_cell(m,tx,ty):
    # 3x3 walkable map of the selected cell and 8 surrounding cells. 
    return np.array([[m.walkable[y,x] for y in range(ty-1,ty+2)] for x in range(tx-1,tx+2)])


 
'''
MAP FUNCTIONS
'''

class GameMap():
    def __init__(self,w,h):
        # Dimensions
        self.w = w
        self.h = h

        self.rooms = list()  # Holds Room objects.
        self.walls = list()  # Holds lists of (y,x) coords for all room walls.
        
        # Numpy int arrays for map derived from rooms.
        self.walkable = np.zeros(shape=(h,w), dtype=int)
 
        # Numpy int arrays which are unique to map
        self.doors = np.zeros(shape=(h,w), dtype=int)
        
        self.stair_in = False
        self.stair_out = False
 
    
    # Take a Room object and, if viable, carve that room into the map.     
    def carve_room(self,r):
        if not room_blocked(r,self):
            r.carve(self)  # Copy room info for walkable/entity placement.
            self.walls.extend(r.walls)  # Pull out walls to aid procgen.
            self.rooms.append(r)  # Add room object to collection in map.

            return True
        else:
            return False
        

# Take a coordinate and check if it actually exists within map boundaries.
def in_bounds(x,y,m):
    return (x > 0 and x < m.w) and (y > 0 and y < m.h)


def is_walkable(x,y,m):
    return in_bounds(x,y,m) and m.walkable[y,x]


# Is the coord in bounds and check that it is still a wall then we can carve it
def can_carve(x,y,m):
    return in_bounds(x,y,m) and not m.walkable[y,x]


def dist_between(fx,fy,tx,ty):
    dx = fx-tx
    dy = fy-ty
    return sqrt(dx*dx+dy*dy)


def get_walkable_tile(m):
    x,y = 0,0
    
    while not is_walkable(x,y,m):
        x = randint(0,m.w)
        y = randint(0,m.h)
        
    return y,x


def place_door(x,y,m):
    
    m.walkable[y,x] = 1
    
    x_mod = [0,1,0,-1,-1,1,-1,1]
    y_mod = [-1,0,1,0,-1,-1,1,1]
    
    adj_door = False
    for i in range(0,8):
        dx = x + x_mod[i]
        dy =y + y_mod[i]
        
        if m.doors[dy,dx]:
            adj_door = True
            m.doors[dy,dx] = 0
        
    if not adj_door:
        m.doors[y,x] = 1    


def create_wall_tile(x,y,m):
    m.walkable[y,x] = 0
    m.doors[y,x] = 0


'''
ROOMS FUNCTIONS
'''

class Room():
    def __init__(self,x1,y1,x2,y2):
        # Make x1 and y1 be always the lowest coords
        lo_x = min(x1,x2)
        hi_x = max(x1,x2)
        
        lo_y = min(y1,y2)
        hi_y = max(y1,y2)
        
        # Bounding        
        self.x1 = lo_x
        self.y1 = lo_y
        self.x2 = hi_x
        self.y2 = hi_y

        # Dimensions
        self.w = hi_x - lo_x
        self.h = hi_y - lo_y
        
        # Numpy int arrays which will dictate same array contents in map object
        self.walkable = np.zeros(shape=(self.h,self.w), dtype=int)

        # Update walkable array based on dimensions of room.
        self.make_walkable()
        
        # List of (y,x) coordinates representing the walls of this room
        self.walls = get_walls(self)
        

        
        
    def make_walkable(self):
        for y in range(0,self.h):
            for x in range(0,self.w):
                self.walkable[y,x] = 1  # 1 is walkable 0 is not.
                
                
    # Carve / paste this room into the game map.
    def carve(self,m):
        
        for y in range(self.y1, self.y2):
            for x in range(self.x1, self.x2):
                
                # Copy own array contents into map array of same attribute.                
                
                m.walkable[y,x] = self.walkable[y-self.y1,x-self.x1]
                

# Prefab room, rather than just being a square this takes user input in terms
# of walkable / preset items and mobs, and can contain any design.
class PreFab(Room):
    def __init__(self,x1,y1,x2,y2,template):
        super().__init__(x1,y1,x2,y2)
        
        # Replace the rooms auto-generated arrays with the user-provided ones
        self.walkable = template.walkable
        self.walls = get_walls(self)


# If any coord within the proposed boundary of the room is not a wall, reject
def room_blocked(r,m):
    for y in range(r.y1-1,r.y2+1):
        for x in range(r.x1-1,r.x2+1):
            if not can_carve(x,y,m):
                return True
    return False


# Create a list of (y,x) coordinates for each wall in a room.
# It's y,x to match the indexing of numpy arrays.
def get_walls(r):
    
    n = [(r.y1-1,x) for x in range(r.x1,r.x2) if r.walkable[r.y1-r.y1,x-r.x1]]
    e = [(y,r.x2) for y in range(r.y1,r.y2) if r.walkable[y-r.y1,r.x2-r.x1-1]]
    s = [(r.y2,x) for x in range(r.x1,r.x2) if r.walkable[r.y2-r.y1-1,x-r.x1]]
    w = [(y,r.x1-1) for y in range(r.y1,r.y2) if r.walkable[y-r.y1,r.x1-r.x1]]

    return [n,e,s,w]


def get_center_of_room(room):
    return room.y1 + int(room.h / 2), room.x1 + int(room.w / 2)



'''
PREFABS
'''

class Template():
    def __init__(self, prefab_string):
        
        tiles_walkable = {"#": 0,
                          ".": 1}
        
        walk_map = np.array([[tiles_walkable.get(char,0) for char in row]
                             for row in prefab_string.strip("\r\n").split()]).transpose()
        
        self.h = len(walk_map)
        self.w = len(walk_map[0])

        self.walkable = np.array(walk_map)
        

def get_matching_prefabs(prefab_pool,w,h):
    
    matching = [pf for pf in prefab_pool if pf.w == w and pf.h == h]
    
    return matching


def load_prefabs():

    prefab_pool = list()
    
    ### w 10 x h 10
    
    prefab_pool.append(Template(
    """\
    ..........
    .##....##.
    .##....##.
    ..........
    ....##....
    ....##....
    ..........
    .##....##.
    .##....##.
    ..........
    """))
    
    prefab_pool.append(Template(
    """\
    ####..####
    ####..####
    ####..####
    ###....###
    ..........
    ..........
    ###....###
    ####..####
    ####..####
    ####..####
    """))
    
    prefab_pool.append(Template(
    """\
    ####..####
    ####..####
    ###....###
    ##......##
    ..........
    ..........
    ##......##
    ###....###
    ####..####
    ####..####
    """))
    
    prefab_pool.append(Template(
    """\
    #######.##
    #######.##
    ..........
    ###.###.##
    #.....#.##
    #.....#.##
    #.......##
    #.....#.##
    #.....#.##
    #######.##
    """))
    
    prefab_pool.append(Template(
    """\
    ##.#######
    ##.#######
    ##........
    ###.###.##
    #.....#.##
    #.....#.##
    ......#.##
    #.....#.##
    #.....#.##
    #######.##
    """))
    
    
    
    ### w 10 x h 9
    
    prefab_pool.append(Template(
    """\
    #######.##
    ..........
    ##.#######
    #.....####
    #......###
    #.......##
    ##......##
    ###.....##
    ######.###
    """))
    
    prefab_pool.append(Template(
    """\
    ###.###.##
    #.....#.##
    #.....#.##
    #.......##
    #.....#.##
    #.....#.##
    #######.##
    ..........
    #######.##
    """))
    
    
    
    ### w 10 x h 7
    
    prefab_pool.append(Template(
    """\
    #######.##
    #######.##
    ..........
    ##.#######
    ##.#######
    ##.#######
    ##.#######
    """))
    
    prefab_pool.append(Template(
    """\
    ##.#######
    ##.#######
    ..........
    #######.##
    #######.##
    #######.##
    #######.##
    """))
    
    prefab_pool.append(Template(
    """\
    ##.#######
    ##.#######
    ..........
    ##.#######
    ##.#######
    ##.#######
    ##.#######
    """))
    
    prefab_pool.append(Template(
    """\
    #######.##
    #######.##
    ..........
    #######.##
    #######.##
    #######.##
    #######.##
    """))
    
    
    
    ### w 10 x h 6
    
    prefab_pool.append(Template(
    """\
    #######.##
    #######.##
    #######.##
    ..........
    ##.#######
    ##.#######
    """))
    
    
    
    ### w 10 x h 5
    
    prefab_pool.append(Template(
    """\
    ##.#######
    ##.#######
    .......###
    ##.###....
    ##.#######
    """))
    
    
    
    ### w 9 x h 9
    
    prefab_pool.append(Template(
    """\
    .........
    .........
    .........
    ...###...
    ...###...
    ...###...
    .........
    .........
    .........
    """))
    
    prefab_pool.append(Template(
    """\
    .........
    .###.###.
    .#.....#.
    .#.....#.
    ....#....
    .#.....#.
    .#.....#.
    .###.###.
    .........
    """))
    
    prefab_pool.append(Template(
    """\
    .........
    .........
    ..##.##..
    ..#...#..
    .........
    ..#...#..
    ..##.##..
    .........
    .........
    """))
    
    prefab_pool.append(Template(
    """\
    .........
    .##...##.
    .##...##.
    .........
    .........
    .........
    .##...##.
    .##...##.
    .........
    """))
    
    prefab_pool.append(Template(
    """\
    ####.####
    ####.####
    ####.####
    ###...###
    .........
    ###...###
    ####.####
    ####.####
    ####.####
    """))
    
    prefab_pool.append(Template(
    """\
    ####.####
    ####.####
    ###...###
    ##.....##
    .........
    ##.....##
    ###...###
    ####.####
    ####.####
    """))
    
    prefab_pool.append(Template(
    """\
    ####.####
    ####.####
    ##.....##
    ##.....##
    .........
    ##.....##
    ##.....##
    ####.####
    ####.####
    """))
    
    
    
    ### w 9 x h 5
    
    prefab_pool.append(Template(
    """\
    #####.###
    #####.###
    .........
    #####.###
    #####.###
    """))
    
    prefab_pool.append(Template(
    """\
    ####.####
    ###...###
    .........
    ###...###
    ####.####
    """))
    
    
    
    ### w 7 x h 7
    
    prefab_pool.append(Template(
    """\
    ##...##
    #.....#
    .......
    .......
    .......
    #.....#
    ##...##
    """))
    
    
    
    ### w 6 x h 6
    
    prefab_pool.append(Template(
    """\
    ##..##
    #....#
    ......
    ......
    #....#
    ##..##
    """))
    
    
    
    ### w 5 x h 5
    
    prefab_pool.append(Template(
    """\
    ##.##
    #...#
    .....
    #...#
    ##.##
    """))
    
    return prefab_pool


'''
RUN
'''

if __name__ == "__main__":
    main()