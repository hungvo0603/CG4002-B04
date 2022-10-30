import time
import threading
from abc import abstractmethod


class PlayerStateBase:
    def __init__(self, main):
        self.max_grenades = 2
        self.max_shields = 3
        self.bullet_hp = 10
        self.grenade_hp = 30
        self.shield_max_time = 10
        self.magazine_size = 6
        self.max_hp = 100

        self.hp = self.max_hp
        self.action = 'none'
        self.bullets = self.magazine_size
        self.grenades = self.max_grenades
        self.shield_time = 0
        self.shield_health = 0
        self.num_shield = self.max_shields
        self.num_deaths = 0

        self.shield_start_time = time.time()-30
        self.main = main
        self.shield_cd = False

    def get_dict(self):
        _player = dict()
        _player['hp'] = self.hp
        _player['action'] = self.action
        _player['bullets'] = self.bullets
        _player['grenades'] = self.grenades
        _player['shield_time'] = self.shield_time
        _player['shield_health'] = self.shield_health
        _player['num_deaths'] = self.num_deaths
        _player['num_shield'] = self.num_shield
        return _player

    def initialize(self, action, bullets_remaining, grenades_remaining,
                   hp, num_deaths, num_unused_shield,
                   shield_health, shield_time_remaining):
        self.hp = hp
        self.action = action
        self.bullets = bullets_remaining
        self.grenades = grenades_remaining
        self.shield_time = shield_time_remaining
        self.shield_health = shield_health
        self.num_shield = num_unused_shield
        self.num_deaths = num_deaths

    def initialize_from_dict(self, player_dict: dict):
        self.hp = player_dict['hp']
        self.action = player_dict['action']
        self.bullets = player_dict['bullets']
        self.grenades = player_dict['grenades']
        self.shield_time = player_dict['shield_time']
        self.shield_health = player_dict['shield_health']
        self.num_shield = player_dict['num_shield']
        self.num_deaths = player_dict['num_deaths']
        if not self.shield_cd and self.shield_time > 0:
            t = threading.Thread(target=self.timer_shield, args=())
            t.start()

    def initialize_from_player_state(self, player_state):
        self.hp = player_state.hp
        self.action = player_state.action
        self.bullets = player_state.bullets_remaining
        self.grenades = player_state.grenades_remaining
        self.shield_time = player_state.shield_time_remaining
        self.shield_health = player_state.shield_health
        self.num_shield = player_state.num_unused_shield
        self.num_deaths = player_state.num_deaths

    @abstractmethod
    def update(self, pos_self, pos_opponent, action_self,
               action_opponent, action_opponent_is_valid):
        ...

    @abstractmethod
    def update_actl(self, data):
        ...

    @abstractmethod
    def action_is_valid(self, action_self):
        ...


class PlayerStateStudent(PlayerStateBase):
    """
    This is a dummy class
    """

    def update_actl(self, new_data):
        if new_data == "glove disconnect" or new_data == "gun disconnect" or new_data == "vest disconnect" or \
                new_data == "glove connect" or new_data == "gun connect" or new_data == "vest connect":
            self.action = new_data
        if new_data == 'shoot':
            self.action = 'shoot'
            self.bullets = self.bullets-1
        if new_data == 'grenade':
            self.action = 'grenade'
            self.grenades = max(0, self.grenades-1)
        if new_data == 'reload':
            self.action = 'reload'
            if self.bullets == 0:
                self.bullets = self.magazine_size
        if new_data == 'shield':
            self.action = 'shield'
            if self.num_shield > 0 and self.shield_time <= 0:
                self.shield_health = 30
                self.shield_time = self.shield_max_time
                self.num_shield = max(0, self.num_shield-1)
                t = threading.Thread(target=self.timer_shield, args=())
                t.start()
        if new_data == 'logout':
            self.action = 'logout'
        if new_data == 'bullet_hit':
            if self.bullets == -1:
                self.bullets = 0
                pass

            if self.shield_time:
                if self.shield_health - 10 < 0:
                    leftover = 10 - self.shield_health
                    self.shield_health = 0
                    self.hp = max(self.hp-leftover, 0)
                else:
                    self.shield_health = max(self.shield_health-10, 0)
            else:
                self.hp = max(self.hp-10, 0)
        if new_data == 'grenade_damage':
            if self.shield_time:
                if self.shield_health - 30 < 0:
                    leftover = 30 - self.shield_health
                    self.shield_health = 0
                    self.hp = max(self.hp-leftover, 0)
                else:
                    self.shield_health = max(self.shield_health-30, 0)
            else:
                self.hp = max(self.hp-30, 0)
        if new_data == 'none':
            self.action = 'none'
        if new_data == 'death':
            self.action = 'none'
            self.num_deaths = self.num_deaths + 1
        if new_data == 'respawn':
            pass

    def action_is_valid(self, action_self):
        ret = True
        # this code does no sanity check
        # this is for the purpose of student release only
        return ret

    def timer_shield(self):
        self.shield_cd = True
        while self.shield_time != 0:
            time.sleep(1)
            self.shield_time = max(self.shield_time - 1, 0)
            #print(self.shield_health, self.shield_time)
        self.shield_time = 0
        self.shield_health = 0
        self.shield_cd = False
        self.main.cd_shield = True
