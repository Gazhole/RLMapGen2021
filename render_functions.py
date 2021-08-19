import pygame
import random
from map_functions import dist_between, is_walkable, get_tile_id, in_bounds

# Set up colours.
CLR_WHITE = (255, 255, 255)
CLR_BLACK = (0, 0, 0)
CLR_BLUE = (0, 0, 255)
CLR_RED = (255, 0, 0)
CLR_GREEN = (0, 255, 0)
CLR_YELLOW = (255, 255, 0)


def map_coords_to_pixels(map_x, map_y):
    """
    Simple conversion function to transform map coordinates into screen coordinates for drawing sprites.
    :param map_x: (int) The map coordinate x axis (tiles)
    :param map_y: (int) The map coordinate y axis (tiles)
    :return: pixes
    """
    return int(map_x * 16), int(map_y * 16)


def render_all(screen_surface, screen_width, screen_height, view_port_width, view_port_height, view_port_x_offset,
               view_port_y_offset, game_map, player, entities, visible_map_chunk, sprites, tile_maps):
    """

    :param screen_surface: obj - the main pygame drawing surface.
    :param screen_width: int - screen width in pixels
    :param screen_height: int - screen height in pixels
    :param view_port_width: int - width in pixels of the screen segment which displays the map
    :param view_port_height: int - height in pixels of the screen segment which displays the map
    :param view_port_x_offset: int - pixels to shift view port to the left.
    :param view_port_y_offset: int - pixels to shift view port down.
    :param game_map: game map object
    :param player: player object
    :param entities: list - tracking all entities in game.
    :return:
    """

    # Set the background colour of the window to black.
    screen_surface.fill(CLR_BLACK)

    # Invoke individual draw functions.
    render_map(screen_surface, view_port_x_offset, view_port_y_offset, game_map, visible_map_chunk, sprites, tile_maps, player)
    render_entities(screen_surface, view_port_x_offset, view_port_y_offset, entities, visible_map_chunk)
    render_bottom_hud(screen_surface, screen_width, screen_height, view_port_width, view_port_height, view_port_x_offset, view_port_y_offset, player)
    render_top_hud(screen_surface, screen_width, screen_height, view_port_width, view_port_height, view_port_x_offset, view_port_y_offset, player)

    # Refresh the display.
    pygame.display.flip()

    # Clear the entities
    clear_entities(screen_surface, view_port_x_offset, view_port_y_offset, entities, visible_map_chunk)


def render_top_hud(screen_surface, screen_width, screen_height, view_port_width, view_port_height, view_port_x_offset, view_port_y_offset, player):
    hud_screen_x1 = view_port_x_offset
    hud_screen_x2 = view_port_x_offset + view_port_width
    hud_screen_y1 = 0
    hud_screen_y2 = view_port_y_offset

    hud_width = hud_screen_x2 - hud_screen_x1
    hud_height = hud_screen_y2 - hud_screen_y1

    draw_element(screen_surface, hud_screen_x1, hud_screen_y1, hud_width, hud_height, CLR_BLUE)


def render_bottom_hud(screen_surface, screen_width, screen_height, view_port_width, view_port_height, view_port_x_offset, view_port_y_offset, player):
    hud_screen_x1 = view_port_x_offset
    hud_screen_x2 = view_port_x_offset + view_port_width
    hud_screen_y1 = view_port_y_offset + view_port_height
    hud_screen_y2 = screen_height

    hud_width = hud_screen_x2 - hud_screen_x1
    hud_height = hud_screen_y2 - hud_screen_y1

    draw_element(screen_surface, hud_screen_x1, hud_screen_y1, hud_width, hud_height, CLR_BLUE)


    
def line_of_sight(m,x1,y1,x2,y2):
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
        
        if not frst and not is_walkable(x1,y1,m):
            return False
        
        if m.doors[y1,x1]:
            return False
        
        frst,e2=False,err*2
		
        if e2>-dy:
            err-=dy
            x1+=sx
            
        if e2<dx:
            err+=dx
            y1+=sy
            
    return True


def get_wall_tile(m,x,y,sprites):
    walls = sprites.get("walls")
    tid = get_tile_id(m,x,y)
    return walls.get(tid,None)


def render_map(screen_surface, view_port_x_offset, view_port_y_offset, game_map, visible_map_chunk, sprites, tile_maps, player):
    map_chunk_x1 = visible_map_chunk.x1
    map_chunk_y1 = visible_map_chunk.y1
       
    #Tile maps
    FLOOR_VIS = tile_maps.get("floor_vis")
    DOOR_VIS = tile_maps.get("door_vis")
    FLOOR_HID = tile_maps.get("floor_hid")
    DOOR_HID = tile_maps.get("door_hid")
    
    # Draw walls (blocked tiles).
    for x, y in visible_map_chunk:
        
        if in_bounds(x,y,game_map):
            
            los = line_of_sight(game_map, player.map_x, player.map_y, x, y)
            
            if los:
                SPR_FLOOR = FLOOR_VIS.get(str(x)+str(y))
                SPR_DOOR = DOOR_VIS.get(str(x)+str(y))
                SPR_IN = sprites.get("entrance")
                SPR_OUT = sprites.get("exit")
                SPR_WALL = get_wall_tile(game_map, x, y, sprites)
    
                game_map.explored[y, x] = 1
                
            else:
                if game_map.explored[y, x]:
                    SPR_FLOOR = FLOOR_HID.get(str(x)+str(y))
                    SPR_DOOR = DOOR_HID.get(str(x)+str(y))                
                    SPR_IN = sprites.get("entrance")
                    SPR_OUT = sprites.get("exit")
                    SPR_WALL = get_wall_tile(game_map, x, y, sprites)
    
                else:    
                    SPR_FLOOR = None
                    SPR_DOOR = None
                    SPR_IN = None
                    SPR_OUT = None
                    SPR_WALL = None
    
    
    
            if x < game_map.w and y < game_map.h:
                
                is_wall = not game_map.walkable[y, x]
                is_door = not is_wall and game_map.doors[y, x]
                is_entry = (y,x) == game_map.stair_in 
                is_exit = (y,x) == game_map.stair_out
                
                
                if is_entry:
                    tile_sprite = SPR_IN
                                    
                elif is_exit:
                    tile_sprite = SPR_OUT
                            
                elif is_door: 
                    tile_sprite = SPR_DOOR
    
                elif not is_wall:  # If it's floor
                    tile_sprite = SPR_FLOOR
                
                # Wall tiles - autotiler goes here
                else:
                    tile_sprite = SPR_WALL
    
            # Calculate screen position for tile. Draw it!
            tile_screen_x, tile_screen_y = map_coords_to_pixels(x - map_chunk_x1, y - map_chunk_y1)
            draw_element(screen_surface, tile_screen_x + view_port_x_offset, tile_screen_y + view_port_y_offset, 16, 16, CLR_BLACK, tile_sprite)


def render_entities(screen_surface, view_port_x_offset, view_port_y_offset, entities, visible_map_chunk):
    map_chunk_x1 = visible_map_chunk.x1
    map_chunk_y1 = visible_map_chunk.y1

    # Iterate through entities and blit it's surface to the screen.
    for entity in entities:
        entity_screen_x, entity_screen_y = map_coords_to_pixels(entity.map_x - map_chunk_x1, entity.map_y - map_chunk_y1)
        screen_surface.blit(entity.surf, (entity_screen_x + view_port_x_offset, entity_screen_y + view_port_y_offset))


def draw_element(screen_surface, screen_x, screen_y, element_width, element_height, colour, sprite=None):
    element_surface = pygame.Surface((element_width, element_height))

    # If there is a sprite, blit it to the element's surface - if not just fill with block colour.
    if sprite:
        element_surface.blit(sprite, (0, 0))
    else:
        element_surface.fill(colour)

    screen_surface.blit(element_surface, (screen_x, screen_y))


def clear_entities(screen_surface, view_port_x_offset, view_port_y_offset, entities, visible_map_chunk):
    map_chunk_x1 = visible_map_chunk.x1
    map_chunk_y1 = visible_map_chunk.y1

    # Iterate through entities and clear it.
    for entity in entities:
        entity_screen_x, entity_screen_y = map_coords_to_pixels(entity.map_x - map_chunk_x1, entity.map_y - map_chunk_y1)
        clear_element(screen_surface, entity_screen_x, entity_screen_y, 16, 16)


def clear_element(screen_surface, screen_x, screen_y, element_width, element_height, colour=CLR_BLACK):
    element_surface = pygame.Surface((element_width, element_height))
    element_surface.fill(colour)
    screen_surface.blit(element_surface, (screen_x, screen_y))


def create_sprite_map(game_map,sprites):
    
    floor_vis_spr = sprites.get("floor_vis")
    door_vis_spr = sprites.get("door_vis")
    floor_hid_spr = sprites.get("floor_hid")
    door_hid_spr = sprites.get("door_hid")
    
    floor_vis_map = dict()
    door_vis_map = dict()
    floor_hid_map = dict()
    door_hid_map = dict()
    
    w = game_map.w + 1
    h = game_map.h + 1
    
    for y in range(h):
        for x in range(w):
            floor_idx = random.randint(0,len(floor_vis_spr)-1)
            door_idx = random.randint(0,len(door_vis_spr)-1)
            
            floor_vis_map[str(x)+str(y)] = floor_vis_spr[floor_idx]
            floor_hid_map[str(x)+str(y)] = floor_hid_spr[floor_idx]
           
            door_vis_map[str(x)+str(y)] = door_vis_spr[door_idx]
            door_hid_map[str(x)+str(y)] = door_hid_spr[door_idx]
            
    return floor_vis_map,door_vis_map,floor_hid_map,door_hid_map