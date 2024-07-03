import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
from stable_baselines3 import PPO
from sprites import Player, Bullet, Enemy, Wall
from PrimarySettings import *
from main import Game
import time
import copy
import math
import random

class TankTroubleEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(TankTroubleEnv, self).__init__()
        self.game = Game()
        self.game.new()

        #nagrade i penali
        self.player_reward = 0
        self.fire_reward = 4
        self.fire_penalty = 0.2
        self.move_closer_reward =3 
        self.move_away_penalty = 3
        self.turn_towards_reward = 6
        self.turn_away_penalty = 300
        self.headshot_reward = 550
        self.num_of_bullets = 50
        self.num_of_shots_per_episode = 0
        self.headshot = 0
        self.enemy_hits = 0
        self.max_num_of_steps=80
        self.current_step = 0
        self.missed_turns = 0
        self.correct_turns = 0
        self.num_of_shots_hits_per_episode = 0
        self.num_of_shots_in_game = 0
        self.episode_reward = 0
        self.num_of_resets=0
        self.isAdjusted = True
        self.isAdjusted1 = True
        self.action_space = spaces.Discrete(5) 
        self.observation_space = spaces.Box(
            low=0,
            high=1,
            shape=(7,),
            dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        '''
        if self.num_of_resets==10:
            self.num_of_resets=0
            self.game.new()
        else:
            self.game.player.position.x = random.randint(20, 1000)
            self.game.player.position.y = random.randint(20,740)
            self.game.player.rot=180
            self.num_of_resets+=1
            '''
        self.game.new()
        self.current_step = 0
        self.enemy_hits = 0
        self.num_of_shots_in_game = 0
        self.game.player_hits = 0
        self.game.enemy_hits = 0
        self.game.enemy_hits_past = 0
        self.game.player_hits_past = 0
        self.player_reward = 0
        self.game.SCORE1 = 0
        self.game.SCORE2 = 0

        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

        return self._get_obs().astype(np.float32), {}

    def step(self, action):
        prev_player_position = copy.deepcopy(self.game.player.position)
        prev_enemy_position = copy.deepcopy(self.game.enemy.position)
        prev_angle = copy.deepcopy(self.game.player.rot)
        #IF zbog baga
        if self.game.player.position.x<0 or self.game.player.position.x>1024 or self.game.player.position.y<0 or self.game.player.position.y>768 or self.game.enemy.position.x<0 or self.game.enemy.position.x>1024 or self.game.enemy.position.y<0 or self.game.enemy.position.y>768:
            self.reset()
        #akcija za naseg igraca
        player_action = ['left', 'right', 'up', 'down', 'fire'][action]
        self.game.player.set_action(player_action)
        #akcija za neprijatelja
        model = PPO.load("Enemy")
        enemy_action,_=model.predict(self._get_obs(for_enemy=True).astype(np.float32))
        self.game.enemy.set_action(['left', 'right', 'up', 'down', 'fire'][enemy_action])

        self.game.update_time()
        self.game.update()

        new_angle = copy.deepcopy(self.game.player.rot)
        obs = self._get_obs().astype(np.float32)
        reward = self._get_reward(prev_player_position,prev_enemy_position,prev_angle, new_angle, player_action)
        done = self._is_done()
        info = {}
        self.episode_reward += reward
        self.current_step += 1
        #self.num_of_shots_in_game== self.num_of_bullets
        if self.current_step >= self.max_num_of_steps:
            truncated = True
        else:
            truncated = False
        return obs, reward, done, truncated, info

    def render(self, mode='human'):
        self.game.draw()

    def close(self):
        pygame.quit()

    def _get_obs(self,for_enemy=False):
        player_data = [
            self.game.player.position.x/1024,
            self.game.player.position.y/768,
            self.game.player.rot/360,
        ]
        enemy_data = [
            self.game.enemy.position.x/1024,
            self.game.enemy.position.y/768,
            self.game.enemy.rot/360,
        ]
        angle_to_enemy = calculate_angle(self.game.player.position, self.game.enemy.position)/360

        if for_enemy:
            observation = np.array(enemy_data + player_data)
        else:
            observation = np.array(player_data + enemy_data+[angle_to_enemy])
        return observation

    def _get_reward(self,prev_player_position,prev_enemy_position, prev_angle, new_angle,action):
        self.player_reward = 0

        # Nagrada i kazna za pucanje
        if action == 'fire' and is_enemy_hit(self.game.player, prev_enemy_position):
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            self.headshot +=1
            self.player_reward+=self.headshot_reward
            self.enemy_hits += 1
            self.num_of_shots_per_episode += 1
            self.num_of_shots_in_game += 1
            return self.player_reward
        elif action == 'fire' and is_aimed_at_enemy(self.game.player, self.game.enemy):
            print("**********************************************************")
            self.player_reward += self.fire_reward
            self.num_of_shots_hits_per_episode += 1
            self.num_of_shots_per_episode += 1
            self.num_of_shots_in_game += 1
        elif action == 'fire':
            data=is_closer_to_enemy(self.game.player, self.game.enemy)
            if data[1]==True:
                self.num_of_shots_in_game += 1
                self.player_reward+=data[0]
                if data[0] > 0:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            else:
                self.num_of_shots_per_episode += 1
                self.num_of_shots_in_game += 1
                print("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")
                self.player_reward -= self.fire_penalty


        # Nagrada i kazna za približavanje neprijatelju
        if action== 'up' or action== 'down':
            new_distance_to_enemy = calculate_distance(self.game.player.position, prev_enemy_position)
            prev_distance_to_enemy = calculate_distance(prev_player_position, prev_enemy_position)
            if new_distance_to_enemy < prev_distance_to_enemy:
                self.player_reward += self.move_closer_reward
            elif new_distance_to_enemy > prev_distance_to_enemy:
                self.player_reward -= self.move_away_penalty

        # Nagrada i kazna za okretanje prema neprijatelju
        if action == 'left' or action == 'right':
            calculated_angle = calculate_angle(self.game.player.position, prev_enemy_position)
            diff_new = calculate_smallest_angle_diff(calculated_angle, new_angle)
            diff_prev = calculate_smallest_angle_diff(calculated_angle, prev_angle)
            if diff_new < diff_prev:
                self.player_reward += self.turn_towards_reward
                self.correct_turns += 1
            elif diff_new > diff_prev:
                self.player_reward -= self.turn_away_penalty
                self.missed_turns += 1
        return self.player_reward

    def _is_done(self):
        return self.game.SCORE2 == 1 or self.game.SCORE1==1 #or self.enemy_hits==3
        
    
def calculate_angle(position1, position2):
    dx = position1.x - position2.x
    dy = position1.y - position2.y
    angle = math.degrees(math.atan2(dy, dx))
    if angle < 0:
        angle += 360
    return (270 - angle) % 360

def calculate_distance(position1, position2):
    dx = position1.x - position2.x
    dy = position1.y - position2.y
    return math.sqrt(dx**2 + dy**2)

def calculate_smallest_angle_diff(angle1, angle2):
    return min(abs(angle1 - angle2), 360 - abs(angle1 - angle2))


def is_aimed_at_enemy(player, enemy):
    angle = calculate_angle(player.position, enemy.position)
    return abs(angle - player.rot) < 10

def is_enemy_hit(player, enemy_position):
    angle = calculate_angle(player.position, enemy_position)
    return abs(angle - player.rot) < 2
def is_closer_to_enemy(player, enemy):
    angle = calculate_angle(player.position, enemy.position)
    needed_rotation=abs(angle - player.rot)
    if needed_rotation < 20 and needed_rotation > 10:
        return [20/needed_rotation,True]
    return [0,False]