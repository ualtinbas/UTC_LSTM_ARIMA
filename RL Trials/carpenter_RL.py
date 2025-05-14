import gymnasium as gym
import numpy as np
import random
import time

# Time tracking
start_time = time.time()

# Define the Environment
class CarpenterEnv:
    def __init__(self):
        self.max_money = 200  # Budget constraint
        self.max_time = 80  # Available time
        self.state = (self.max_money, self.max_time, 0, 0)  # (money, time, tables, bookcases)
        self.done = False

    def reset(self):
        self.state = (self.max_money, self.max_time, 0, 0)
        self.done = False
        return self.state

    def step(self, action):
        money, time, tables, bookcases = self.state

        if action == 0:  # Build Table
            if money >= 10 and time >= 5:
                money -= 10
                time -= 5
                tables += 1
                reward = 180  # Profit from table
            else:
                reward = -50  # Penalty for invalid action
        elif action == 1:  # Build Bookcase
            if money >= 20 and time >= 4:
                money -= 20
                time -= 4
                bookcases += 1
                reward = 200  # Profit from bookcase
            else:
                reward = -50
        elif action == 2:  # Stop production
            self.done = True
            reward = 0
        else:
            reward = -100  # Invalid action

        # Update the state
        self.state = (money, time, tables, bookcases)

        if money <= 0 or time <= 0:
            self.done = True  # Stop if no more resources

        return self.state, reward, self.done

# Define actions: 0 = Build Table, 1 = Build Bookcase, 2 = Stop
actions = [0, 1, 2]

# Q-learning parameters
alpha = 0.1  # Learning rate
gamma = 0.9  # Discount factor
epsilon = 0.1  # Exploration rate
episodes = 1000  # Training iterations

# Initialize Q-table (State space is large, so we use a dictionary)
Q_table = {}

# Training loop
for episode in range(episodes):
    env = CarpenterEnv()
    state = env.reset()
    total_reward = 0

    while not env.done:
        state_key = tuple(state)  # Convert state to key for Q-table

        # Initialize state-action pair in Q-table if not already present
        if state_key not in Q_table:
            Q_table[state_key] = np.zeros(len(actions))

        # Choose action (Epsilon-Greedy)
        if np.random.rand() < epsilon:
            action = np.random.choice(actions)  # Explore
        else:
            action = np.argmax(Q_table[state_key])  # Exploit

        # Take action and observe reward
        next_state, reward, done = env.step(action)
        next_state_key = tuple(next_state)

        # Update Q-table using the Bellman Equation
        if next_state_key not in Q_table:
            Q_table[next_state_key] = np.zeros(len(actions))

        Q_table[state_key][action] = Q_table[state_key][action] + alpha * (
            reward + gamma * np.max(Q_table[next_state_key]) - Q_table[state_key][action]
        )

        state = next_state
        total_reward += reward

    if episode % 100 == 0:
        print(f"Episode {episode}: Total Profit = {total_reward}")

print("Training Complete!")

env = CarpenterEnv()
state = env.reset()
total_profit = 0

print("\nOptimal Strategy:")
while not env.done:
    state_key = tuple(state)
    action = np.argmax(Q_table.get(state_key, np.zeros(len(actions))))  # Choose best action
    next_state, reward, done = env.step(action)
    print(f"Action Taken: {'Table' if action == 0 else 'Bookcase' if action == 1 else 'Stop'} | State: {next_state} | Reward: {reward}")
    state = next_state
    total_profit += reward

print(f"\nFinal Profit: {total_profit}")

# End time tracking
end_time = time.time()

# Print total elapsed time
elapsed_time = end_time - start_time
print(f"\nTotal Execution Time: {elapsed_time:.2f} seconds")