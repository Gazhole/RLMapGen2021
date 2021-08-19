"""
A simple game. LOL.
"""

import pygame
from input_functions import handle_keys, get_inputs
from render_functions import render_all, create_sprite_map
from classes import Player, StatBlock
from map_functions import map_gen, get_visible_map_chunk
from game_states import Turn


def main():

    # Initialise pygame.
    pygame.init()

    # Set up screen.
    screen_width = 600
    screen_height = 480
    screen_surface = pygame.display.set_mode([screen_width, screen_height])

    # Set up sprites:
    SPR_PLAYER = pygame.image.load('Sprites\\player.png').convert_alpha()
    
    SPR_ORC = pygame.image.load('Sprites\\orc.png').convert_alpha()
        
    SPR_FLOOR1_VIS = pygame.image.load('Sprites\\floor1vis.png').convert_alpha()
    SPR_FLOOR2_VIS = pygame.image.load('Sprites\\floor2vis.png').convert_alpha()
    SPR_FLOOR3_VIS = pygame.image.load('Sprites\\floor3vis.png').convert_alpha()
    
    SPR_FLOOR1_HID = pygame.image.load('Sprites\\floor1hid.png').convert_alpha()
    SPR_FLOOR2_HID = pygame.image.load('Sprites\\floor2hid.png').convert_alpha()
    SPR_FLOOR3_HID = pygame.image.load('Sprites\\floor3hid.png').convert_alpha()

    SPR_DOOR1_VIS = pygame.image.load('Sprites\\door1vis.png').convert_alpha()
    SPR_DOOR2_VIS = pygame.image.load('Sprites\\door2vis.png').convert_alpha()
    SPR_DOOR3_VIS = pygame.image.load('Sprites\\door3vis.png').convert_alpha()

    SPR_DOOR1_HID = pygame.image.load('Sprites\\door1hid.png').convert_alpha()
    SPR_DOOR2_HID = pygame.image.load('Sprites\\door2hid.png').convert_alpha()
    SPR_DOOR3_HID = pygame.image.load('Sprites\\door3hid.png').convert_alpha()
    
    SPR_EXIT = pygame.image.load('Sprites\\stairs_down.png').convert_alpha()
    SPR_ENTRANCE = pygame.image.load('Sprites\\stairs_up.png').convert_alpha()


    sprites = {"player": SPR_PLAYER, 
               "floor_vis": [SPR_FLOOR1_VIS,SPR_FLOOR2_VIS,SPR_FLOOR3_VIS], 
               "door_vis": [SPR_DOOR1_VIS,SPR_DOOR2_VIS,SPR_DOOR3_VIS],
               "floor_hid": [SPR_FLOOR1_HID,SPR_FLOOR2_HID,SPR_FLOOR3_HID],
               "door_hid": [SPR_DOOR1_HID,SPR_DOOR2_HID,SPR_DOOR3_HID],
               "exit": SPR_EXIT,
               "entrance": SPR_ENTRANCE,
               "orc": SPR_ORC,
               "walls": dict()}

    # load wall tiles
    for i in range(1,512):
        try:
            sprites["walls"][i] = pygame.image.load('Sprites\\walls\\'+str(i)+".png").convert_alpha()
        except FileNotFoundError:
            pass


    # Set up view port constants for the area which will display the game map. HUD dimensions are derived from this.
    view_port_width = 600
    view_port_height = 360
    view_port_x_offset = 0
    view_port_y_offset = 50

    # Create player and map objects.
    game_map = map_gen(100,100,50,20)  # Create a game map.

    # Create an overlay of map to store variable floor and door sprites.
    floor_vis,door_vis,floor_hid,door_hid = create_sprite_map(game_map,sprites)
    tile_maps={"floor_vis": floor_vis, "door_vis": door_vis,"floor_hid": floor_hid, "door_hid": door_hid}

    player_stats = StatBlock(h=100, m=0, s=10, d=10)
    py,px = game_map.stair_in
    player = Player("Player", map_x=px, map_y=py, colour=(0, 255, 0), sprite=SPR_PLAYER, stats=player_stats)

    # List to store all the game entities. Populate with player.
    entities = list()
    entities.append(player)

    # Set the first turn as the player.
    current_turn = Turn.player

    # Main game loop.
    running = True
    while running:

        # Create a map chunk for iteration based on the rect boundaries.
        visible_map_chunk = get_visible_map_chunk(player, game_map, view_port_width, view_port_height)

        # Render the various screen elements. The placement of this determines whether player or enemies movement lag..
        render_all(screen_surface, screen_width, screen_height, view_port_width, view_port_height, view_port_x_offset,
                   view_port_y_offset, game_map, player, entities, visible_map_chunk, sprites, tile_maps)

        # Start Player Turn
        if current_turn == Turn.player:

            # Get inputs and terminate loop if necessary.
            user_input, running = get_inputs(running)

            if not user_input:
                continue  # If no input continue with game loop.

            # Process actions
            else:
                # Process user input and get actions.
                action = handle_keys(user_input)

                # Action categories.
                move = action.get("move")
                quit_game = action.get("quit")

                if quit_game:  # Triggered when ESC key is pressed.
                    running = False

                if move:  # If movement keys are pressed move player.
                    player_map_x, player_map_y = player.get_map_position()
                    dx, dy = move  # Pull relative values from action.

                    # Calculate potential new coordinates
                    destination_x = player_map_x + dx
                    destination_y = player_map_y + dy
                    
                    is_walkable = game_map.walkable[destination_y, destination_x]
                    is_door = game_map.doors[destination_y, destination_x]

                    if is_door:
                        game_map.doors[destination_y, destination_x] -= 1

                    elif is_walkable:  # Check if the tiles are walkable.
                        player.move(dx, dy)  # If the cell is empty, move player into it.

            current_turn = Turn.monster  # Set turn state to monster.

        # Start Monster Turn
        if current_turn == Turn.monster:
            
            # MONSTER STUFF
            current_turn = Turn.player  # Set to player's turn again.

    # If the main game loop is broken, quit the game.
    pygame.quit()


if __name__ == "__main__":
    main()
