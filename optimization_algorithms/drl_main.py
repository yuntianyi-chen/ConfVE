# # adapted from:
# # https://github.com/pytorch/tutorials/blob/master/intermediate_source/reinforcement_q_learning.py
# # date accessed: 2021.06.30
#
# import math
# import random
# from collections import namedtuple, deque
# from itertools import count
#
# import gif
# import gym
# import matplotlib.pyplot as plt
# import neptune.new as neptune
# import numpy as np
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# import torch.optim as optim
# import torchvision.transforms as T
# from PIL import Image
#
# # (neptune) Create run
# run = neptune.init(
#     project="common/project-rl",
#     name="training",
#     tags=["training", "CartPole", "seed"],
# )
#
# parameters = {
#     "batch_size": 128,
#     "eps_start": 0.9,
#     "eps_end": 0.05,
#     "eps_decay": 200,
#     "gamma": 0.999,
#     "num_episodes": 51,
#     "target_update": 10,
# }
#
# # (neptune) Log dict as parameters
# run["training/parameters"] = parameters
#
# gif.options.matplotlib["dpi"] = 300
# steps_done = 0
# episode_durations = []
#
# Transition = namedtuple('Transition',
#                         ('state', 'action', 'next_state', 'reward'))
#
# resize = T.Compose([T.ToPILImage(),
#                     T.Resize(40, interpolation=Image.CUBIC),
#                     T.ToTensor()])
#
#
# class ReplayMemory(object):
#     def __init__(self, capacity):
#         self.memory = deque([], maxlen=capacity)
#
#     def push(self, *args):
#         """Save a transition"""
#         self.memory.append(Transition(*args))
#
#     def sample(self, batch_size):
#         return random.sample(self.memory, batch_size)
#
#     def __len__(self):
#         return len(self.memory)
#
#
# class DQN(nn.Module):
#     def __init__(self, h, w, outputs):
#         super(DQN, self).__init__()
#         self.conv1 = nn.Conv2d(3, 16, kernel_size=5, stride=2)
#         self.bn1 = nn.BatchNorm2d(16)
#         self.conv2 = nn.Conv2d(16, 32, kernel_size=5, stride=2)
#         self.bn2 = nn.BatchNorm2d(32)
#         self.conv3 = nn.Conv2d(32, 32, kernel_size=5, stride=2)
#         self.bn3 = nn.BatchNorm2d(32)
#
#         def conv2d_size_out(size, kernel_size=5, stride=2):
#             return (size - (kernel_size - 1) - 1) // stride + 1
#         convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(w)))
#         convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(h)))
#         linear_input_size = convw * convh * 32
#         self.head = nn.Linear(linear_input_size, outputs)
#
#     def forward(self, x):
#         x = x.to(device)
#         x = F.relu(self.bn1(self.conv1(x)))
#         x = F.relu(self.bn2(self.conv2(x)))
#         x = F.relu(self.bn3(self.conv3(x)))
#         return self.head(x.view(x.size(0), -1))
#
#
# def _get_screen():
#     screen = env.render(mode='rgb_array').transpose((2, 0, 1))
#     _, screen_height, screen_width = screen.shape
#     screen = screen[:, int(screen_height*0.4):int(screen_height * 0.8)]
#     view_width = int(screen_width * 0.6)
#     cart_location = _get_cart_location(screen_width)
#     if cart_location < view_width // 2:
#         slice_range = slice(view_width)
#     elif cart_location > (screen_width - view_width // 2):
#         slice_range = slice(-view_width, None)
#     else:
#         slice_range = slice(cart_location - view_width // 2,
#                             cart_location + view_width // 2)
#     screen = screen[:, :, slice_range]
#     screen = np.ascontiguousarray(screen, dtype=np.float32) / 255
#     screen = torch.from_numpy(screen)
#     return resize(screen).unsqueeze(0)
#
#
# def _get_cart_location(screen_width):
#     world_width = env.x_threshold * 2
#     scale = screen_width / world_width
#     return int(env.state[0] * scale + screen_width / 2.0)
#
#
# @gif.frame
# def _get_screen_as_ax(screen):
#     plt.figure()
#     _, ax = plt.subplots(1, 1,)
#     ax.imshow(
#         screen.cpu().squeeze(0).permute(1, 2, 0).numpy(),
#         interpolation='none'
#     )
#     ax.axis("off")
#
#
# def _get_env_start_screen():
#     plt.figure()
#     _, ax = plt.subplots(1, 1,)
#     ax.imshow(
#         _get_screen().cpu().squeeze(0).permute(1, 2, 0).numpy(),
#         interpolation='none'
#     )
#     ax.axis("off")
#     return ax.figure
#
#
# def _plot_durations():
#     run["training/episode/duration"].log(value=episode_durations[-1], step=len(episode_durations))
#     avg = np.array(episode_durations).sum() / len(episode_durations)
#     run["training/episode/avg_duration"].log(value=float(avg), step=len(episode_durations))
#
#
# # (neptune) Log environment info as it's defined
# env_name = "CartPole-v0"
# rnd_seed = np.random.randint(low=1000000)
#
# env = gym.make(env_name).unwrapped
# env.seed(rnd_seed)
#
# run["training/env_name"] = env_name
# run["training/parameters/seed"] = rnd_seed
#
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# run["training/environment/device_name"] = device
#
# env.reset()
# init_screen = _get_screen()
# _, _, screen_height, screen_width = init_screen.shape
#
# # (neptune) Log agent metadata: number of actions from gym action space
# n_actions = env.action_space.n
# run["agent/n_actions"] = n_actions
#
# policy_net = DQN(screen_height, screen_width, n_actions).to(device)
# target_net = DQN(screen_height, screen_width, n_actions).to(device)
# target_net.load_state_dict(policy_net.state_dict())
# target_net.eval()
#
# optimizer = optim.RMSprop(policy_net.parameters())
#
# # (neptune) Add more parameters to the "training/parameters" namespace
# replay_memory = 10000
# memory = ReplayMemory(replay_memory)
# run["training/parameters/replay_memory_size"] = replay_memory
#
#
# def select_action(state):
#     global steps_done
#     sample = random.random()
#     eps_threshold = parameters["eps_end"] + (parameters["eps_start"] - parameters["eps_end"]) * \
#         math.exp(-1. * steps_done / parameters["eps_decay"])
#     steps_done += 1
#     if sample > eps_threshold:
#         with torch.no_grad():
#             return policy_net(state).max(1)[1].view(1, 1)
#     else:
#         return torch.tensor([[random.randrange(n_actions)]], device=device, dtype=torch.long)
#
#
# def optimize_model():
#     if len(memory) < parameters["batch_size"]:
#         return
#     transitions = memory.sample(parameters["batch_size"])
#     batch = Transition(*zip(*transitions))
#     non_final_mask = torch.tensor(
#         tuple(
#             map(
#                 lambda s: s is not None,
#                 batch.next_state
#             )
#         ),
#         device=device,
#         dtype=torch.bool,
#     )
#     non_final_next_states = torch.cat(
#         [s for s in batch.next_state if s is not None]
#     )
#     state_batch = torch.cat(batch.state)
#     action_batch = torch.cat(batch.action)
#     reward_batch = torch.cat(batch.reward)
#     state_action_values = policy_net(state_batch).gather(1, action_batch)
#     next_state_values = torch.zeros(parameters["batch_size"], device=device)
#     next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()
#     expected_state_action_values = (next_state_values * parameters["gamma"]) + reward_batch
#
#     criterion = nn.SmoothL1Loss()
#     loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))
#
#     run["training/parameters/criterion"] = "SmoothL1Loss"
#
#     # (neptune) Log loss, have it as a chart in neptune
#     run["training/loss"].log(float(loss.detach().cpu().numpy()))
#
#     optimizer.zero_grad()
#     loss.backward()
#     for param in policy_net.parameters():
#         param.grad.data.clamp_(-1, 1)
#     optimizer.step()
#
#
# # Main training loop
# for i_episode in range(parameters["num_episodes"]):
#     env.reset()
#
#     # (neptune) Log single image
#     if i_episode == 0:
#         run["visualizations/start_screen"].upload(neptune.types.File.as_image(_get_env_start_screen()))
#     last_screen = _get_screen()
#     current_screen = _get_screen()
#     state = current_screen - last_screen
#     cum_reward = 0
#     frames = []
#     for t in count():
#         frame = _get_screen_as_ax(current_screen)
#         frames.append(frame)
#
#         # (neptune) What my agent is looking at? Log series of images.
#         if i_episode % 10 == 0:
#             input_screen = state.detach().cpu().numpy().squeeze()
#             input_screen = (input_screen - input_screen.min()) / (input_screen.max() - input_screen.min() + 0.000001)
#             input_screen = np.transpose(input_screen, (1, 2, 0))
#
#             run["visualizations/episode_{}/input_screens".format(i_episode)].log(
#                 neptune.types.File.as_image(input_screen)
#             )
#
#         action = select_action(state)
#         _, reward, done, _ = env.step(action.item())
#         cum_reward += reward
#         reward = torch.tensor([reward], device=device)
#
#         last_screen = current_screen
#         current_screen = _get_screen()
#         if not done:
#             next_state = current_screen - last_screen
#         else:
#             next_state = None
#
#         memory.push(state, action, next_state, reward)
#         state = next_state
#
#         optimize_model()
#         if done:
#             episode_durations.append(t + 1)
#             _plot_durations()
#
#             # (neptune) Log reward as series of numbers
#             run["training/episode/reward"].log(value=cum_reward, step=i_episode)
#             if i_episode % 10 == 0:
#                 frames_path = "episode_{}.gif".format(i_episode)
#                 gif.save(
#                     frames,
#                     frames_path,
#                     duration=int(len(frames)/10),
#                     unit="s",
#                     between="startend"
#                 )
#
#                 # (neptune) Log gif to see episode recording
#                 run["visualizations/episode_{}/episode_recording".format(i_episode)].upload(
#                     neptune.types.File(frames_path)
#                 )
#                 plt.close("all")
#             break
#     if i_episode % parameters["target_update"] == 0:
#         target_net.load_state_dict(policy_net.state_dict())
#
# env.close()
#
# # (neptune) Log model weights
# torch.save(policy_net.state_dict(), 'policy_net.pth')
# run['agent/policy_net'].upload('policy_net.pth')
