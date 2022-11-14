import gym
env = gym.make("LunarLander-v2", render_mode="human")
env.action_space.seed(42)

observation = env.reset(seed=42)

for _ in range(1000):
    observation, reward, terminated, truncated= env.step(env.action_space.sample())

    if terminated or truncated:
        observation= env.reset()

env.close()