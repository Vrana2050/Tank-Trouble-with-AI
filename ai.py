import gym
from tank_trouble_env import TankTroubleEnv
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.evaluation import evaluate_policy
import os
import json


def save_progress(episodes_completed, episode_reward,num_of_shots_per_episode,shots_hit,headshot,correct_turns,incorrect_turns, filename="progress300KSuperTrain.json"):
        data = {
            "episodes_completed": episodes_completed,
            "episode_reward": episode_reward,
            "num_of_shots_per_episode": num_of_shots_per_episode,
            "shots_hit": shots_hit,
            "headshots": headshot,
            "correct_turns": correct_turns,
            "incorrect_turns": incorrect_turns
        }
        with open(filename, "a") as f:
            json.dump(data, f)
            f.write("\n")

MODEL_PATH = "Enemy.zip"


if os.path.exists(MODEL_PATH):
    env = TankTroubleEnv()

    # Učitavanje sačuvanog modela
    IsSuperTraining = False
    if IsSuperTraining:  
        def dynamic_adjustment(env, episodes_completed, total_episodes):
            progress = episodes_completed / total_episodes
        model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0002)
        model.set_parameters("ppo_tank_trouble")
        total_episodes = 100
        episodes_completed = 0
        for _ in range(total_episodes):
                model.learn(total_timesteps=3000, reset_num_timesteps=False)
                episodes_completed += 1
                save_progress(episodes_completed, env.episode_reward,env.num_of_shots_per_episode,env.num_of_shots_hits_per_episode,env.headshot,env.correct_turns,env.missed_turns)
                env.episode_reward = 0
                env.correct_turns = 0
                env.missed_turns = 0
                env.num_of_shots_per_episode = 0
                env.num_of_shots_hits_per_episode = 0
                env.headshot = 0
                #dynamic_adjustment(env, episodes_completed, total_episodes)
    
            # Cuvanje modela
        model.save("ppo_tank_trouble_super_training")

    else:
        model = PPO.load("Enemy")
        for i_episode in range(20):
            observation, _ = env.reset()
            done = False
            t = 0
            while not done:
                env.render()
                action,_= model.predict(observation)
                observation, reward, done, _, info = env.step(action)
                t += 1
                if done:
                    print(f"Episode finished after {t} timesteps")
                    break
            print("Episode reward", env.episode_reward)          
        env.close()
else:
    
    env = TankTroubleEnv()

    # Provera okruženja
    check_env(env)

    # Kreiranje PPO modela
    model = PPO(
    "MlpPolicy", 
    env, 
    verbose=1,
    )
    def dynamic_adjustment(env, episodes_completed, total_episodes):

        progress = episodes_completed / total_episodes
        if progress >=0.25 and env.isAdjusted==False:
            env.isAdjusted = True
            env.max_num_of_steps = 160
        if progress >=0.5 and env.isAdjusted1==False:
            env.isAdjusted1 = True
            env.max_num_of_steps = 80
        '''
        if progress >=0.35 and env.isAdjusted==False and progress<0.65:
            env.isAdjusted = True
            env.fire_reward += 10
            env.fire_penalty += 7
            env.turn_towards_reward+=6
            env.move_towards_reward+=6
            env.move_away_penalty+=6
            env.turn_away_penalty+=6
            env.headshot_reward += 100 
            env.max_num_of_steps = 280
            env.num_of_bullets = 40
        if progress >=0.65 and env.isAdjusted1==False:
            env.isAdjusted1 = True
            env.num_of_bullets = 30
            env.fire_reward += 10
            env.fire_penalty += 13
            env.headshot_reward += 100
            env.turn_towards_reward+=8
            env.move_towards_reward+=8
            env.move_away_penalty+=8
            env.turn_away_penalty+=8 
            env.max_num_of_steps = 100
            '''

    total_episodes = 200
    episodes_completed = 0
    for _ in range(total_episodes):
        model.learn(total_timesteps=3000, reset_num_timesteps=False)
        episodes_completed += 1
        save_progress(episodes_completed, env.episode_reward,env.num_of_shots_per_episode,env.num_of_shots_hits_per_episode,env.headshot)
        env.episode_reward = 0
        env.num_of_shots_per_episode = 0
        env.num_of_shots_hits_per_episode = 0
        env.headshot = 0
        dynamic_adjustment(env, episodes_completed, total_episodes)
    
    # Cuvanje modela
    model.save("ppo_tank_trouble")

   