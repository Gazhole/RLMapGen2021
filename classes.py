import pygame
import math


# Get the entity currently occupying the destination tile. Or return None.
def get_blocking_entities(entities, destination_map_x, destination_map_y):
    for entity in entities:
        if entity.blocks and entity.map_x == destination_map_x and entity.map_y == destination_map_y:
            return entity
    return None


class Entity(pygame.sprite.Sprite):
    """
    This is the root class for all game entities.
    All entities have a name, a map location, and eventually a sprite which will be stored here too.
    """
    def __init__(self, name, map_x, map_y, colour, sprite=None, stats=None):
        super().__init__()
        # Set up flavour stuff.
        self.name = name
        self.colour = colour
        self.sprite = sprite

        # Set up map and game objects.
        self.map_x = map_x
        self.map_y = map_y
        self.blocks = True  # Does it block movement?

        # Set up graphics.
        self.surf = pygame.Surface((16, 16))

        # Stats n stuff
        self.stats = stats

        # If there is a sprite, blit it to the instance's surface. If not, just fill with a block of colour.
        if self.sprite:
            self.surf.blit(self.sprite, (0, 0))
        else:
            self.surf.fill(self.colour)

        self.rect = self.surf.get_rect()

    def get_map_position(self):
        # Simply returns the current map coordinates as integers.
        return self.map_x, self.map_y

    def move(self, dx, dy):
        # Alter position on map by the amount in the parameters.
        self.map_x += dx
        self.map_y += dy

    def attack(self, attack_target):
        damage = self.stats.s - attack_target.stats.d
        print("{} attacks {} for {} damage.".format(self.name, attack_target.name, damage))
        attack_target.take_damage(damage)

    def distance_to(self, other):
        dx = other.map_x - self.map_x
        dy = other.map_y - self.map_y
        return math.sqrt(dx ** 2 + dy ** 2)

    def take_damage(self, damage):
        self.stats.h -= damage


class Player(Entity):
    """
    Placeholder for the player class.
    """
    def __init__(self, name, map_x, map_y, colour, sprite=None, stats=None):
        super().__init__(name, map_x, map_y, colour, sprite, stats)


class StatBlock:
    def __init__(self, h, m, s, d):
        self.h = h
        self.m = m
        self.s = s
        self.d = d

        self.max_h = h
        self.max_m = m
