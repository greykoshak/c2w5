from abc import ABC, abstractmethod
import pygame
import random


def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


class Interactive(ABC):

    @abstractmethod
    def interact(self, engine, hero):
        pass


class AbstractObject(ABC):

    @abstractmethod
    def __init__(self):
        pass

    def draw(self, surface):
        pass


class Ally(AbstractObject, Interactive):

    def __init__(self, icon, action, position):
        self.sprite = icon
        self.action = action
        self.position = position

    def interact(self, engine, hero):
        self.action(engine, hero)


class Creature(AbstractObject):

    def __init__(self, icon, stats, position):
        self.sprite = icon
        self.stats = stats
        self.position = position
        self.calc_max_HP()
        self.hp = self.max_hp

    def calc_max_HP(self):
        self.max_hp = 5 + self.stats["endurance"] * 2


class Hero(Creature):

    def __init__(self, stats, icon):
        pos = [5, 2]
        self.start = pos
        self.level = 1
        self.exp = 0
        self.gold = 0
        super().__init__(icon, stats, pos)

    def level_up(self):
        while self.exp >= 100 * (2 ** (self.level - 1)):
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            self.calc_max_HP()
            self.hp = self.max_hp

    def draw(self, surface, sprite_size):
        surface.blit(self.sprite, (sprite_size * 5, sprite_size * 2))


class Effect(Hero):

    def __init__(self, base):
        self.base = base
        self.stats = self.base.stats.copy()
        self.apply_effect()

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.base.hp

    @hp.setter
    def hp(self, value):
        self.base.hp = value

    @property
    def max_hp(self):
        return self.base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.base.max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def sprite(self):
        return self.base.sprite

    @abstractmethod
    def apply_effect(self):
        pass


# FIXME
# add classes
class Enemy(Creature, Interactive):

    def __init__(self, icon, stats, xp, position):
        super().__init__(icon, stats, position)
        self.exp = xp

    def draw(self, surface):
        surface.blit(self.sprite, self.position)

    def interact(self, engine, hero):

        if type(engine.hero) is Batman:
            engine.hero.exp += self.exp
            engine.hero = engine.hero.base
        else:
            f_str = hero.stats["strength"] - random.randint(1, engine.level) * self.stats["strength"]
            f_endr = hero.stats["endurance"] - random.randint(1, engine.level) * self.stats["endurance"]
            f_luck = hero.stats["luck"] - random.randint(1, engine.level) * self.stats["luck"]

            summary = f_str + f_endr + f_luck

            if summary >= 0:
                engine.hero.exp += self.exp
                engine.score += 0.02 * summary

            elif summary < 0:
                engine.hero.exp += int(0.1 * self.exp)
                engine.hero.hp += int(0.2 * summary)

                if engine.hero.hp <= 0:
                    engine.score += 0.1 * engine.hero.hp
                    engine.hero.hp = 1

                elif engine.hero.hp > 0:
                    engine.score -= 0.02 * summary

        engine.hero.level_up()


class Berserk(Effect):

    def __init__(self, base):
        super().__init__(base)

    def apply_effect(self):
        self.stats["strength"] *= 2


class Blessing(Effect):

    def __init__(self, base):
        super().__init__(base)

    def apply_effect(self):
        self.stats["luck"] *= 2


class Weakness(Effect):

    def __init__(self, base):
        super().__init__(base)

    def apply_effect(self):
        self.stats["strength"] = 1
        self.stats["luck"] = 1


class Batman(Effect):

    def __init__(self, base):
        super().__init__(base)

    def apply_effect(self):
        self.stats["strength"] = 9999
