import numpy as np
import random
import csv

# Define constants
NUM_BEDS = 10
NUM_MED_PERSONNEL = 3
MED_PERSONNEL_HOURS = 2  # Each medical personnel works for 2 hours
HELICOPTER_SEATS = 4
NUM_BLOOD_UNITS = 30
NUM_EPISODES = 10000
ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.1

# Total available care time
TOTAL_CARE_TIME = NUM_MED_PERSONNEL * MED_PERSONNEL_HOURS

# Initialize casualties
class Casualty:
    def __init__(self, idx, survival_without_care, required_blood_units, required_care_time, survival_with_care):
        self.id = idx
        self.survival_without_care = survival_without_care
        self.required_blood_units = required_blood_units
        self.required_care_time = required_care_time  # In hours
        self.survival_with_care = survival_with_care
        self.is_allocated = False
        self.allocation = None  # 'bed', 'helicopter', or 'none'
        self.received_care_time = 0.0  # Amount of care time received

    def reset(self):
        self.is_allocated = False
        self.allocation = None
        self.received_care_time = 0.0

# Function to read casualties from CSV
def read_casualties_from_csv(filename):
    casualties = []
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            casualty = Casualty(
                idx=idx,
                survival_without_care=float(row['survival_without_care']),
                required_blood_units=int(row['required_blood_units']),
                required_care_time=float(row['required_care_time']),
                survival_with_care=float(row['survival_with_care'])
            )
            casualties.append(casualty)
    return casualties

# Read casualties from the CSV file
casualties = read_casualties_from_csv('casualties.csv')

NUM_CASUALTIES = len(casualties)

# **Print out the variables of each casualty**
print("Casualty Attributes:")
for casualty in casualties:
    print(f"Casualty {casualty.id}:")
    print(f"  Survival without care: {casualty.survival_without_care:.2f}")
    print(f"  Required blood units: {casualty.required_blood_units}")
    print(f"  Required care time: {casualty.required_care_time:.2f} hours")
    print(f"  Survival with care: {casualty.survival_with_care:.2f}")
    print()

# Define the environment
class Environment:
    def __init__(self):
        self.reset()

    def reset(self):
        self.available_beds = NUM_BEDS
        self.available_helicopter_seats = HELICOPTER_SEATS
        self.available_blood_units = NUM_BLOOD_UNITS
        self.casualties_waiting_for_treatment = []
        for casualty in casualties:
            casualty.reset()
        state = self.get_state()
        return state

    def get_state(self):
        # State representation includes available beds and helicopter seats
        return (self.available_beds, self.available_helicopter_seats, self.available_blood_units)

    def get_possible_actions(self):
        # Actions are tuples: (casualty_index, allocation_type)
        actions = []
        for i, c in enumerate(casualties):
            if not c.is_allocated:
                # Check if bed allocation is possible
                if self.available_beds > 0 and self.available_blood_units >= c.required_blood_units:
                    actions.append((i, 'bed'))
                # Check if helicopter allocation is possible
                if self.available_helicopter_seats > 0:
                    actions.append((i, 'helicopter'))
                # Optionally include 'none' action
                actions.append((i, 'none'))
        return actions

    def step(self, action):
        casualty_index, allocation_type = action
        casualty = casualties[casualty_index]
        reward = 0

        if casualty.is_allocated:
            # Casualty has already been allocated
            return self.get_state(), reward, all(c.is_allocated for c in casualties)

        if allocation_type == 'bed':
            if self.available_beds > 0 and self.available_blood_units >= casualty.required_blood_units:
                self.available_beds -= 1
                self.available_blood_units -= casualty.required_blood_units
                casualty.is_allocated = True
                casualty.allocation = 'bed'
                self.casualties_waiting_for_treatment.append(casualty)
                # No immediate reward; treatment happens after allocations
            else:
                # Allocation failed due to lack of resources
                # Do not mark casualty as allocated
                reward += -1  # Penalty for invalid action
        elif allocation_type == 'helicopter':
            if self.available_helicopter_seats > 0:
                self.available_helicopter_seats -= 1
                casualty.is_allocated = True
                casualty.allocation = 'helicopter'
                # Assume immediate evacuation and treatment
                survival_chance = casualty.survival_with_care
                reward += survival_chance * 10  # Amplified reward
            else:
                # Allocation failed due to lack of resources
                # Do not mark casualty as allocated
                reward += -1  # Penalty for invalid action
        elif allocation_type == 'none':
            casualty.is_allocated = True
            casualty.allocation = 'none'
            reward += 0  # No reward for not allocating care
        else:
            raise ValueError("Unknown allocation type")

        next_state = self.get_state()
        done = all(c.is_allocated for c in casualties)

        if done:
            # Simulate treatment after all allocations
            total_care_time = TOTAL_CARE_TIME
            # Sort casualties waiting for treatment by survival benefit (optional)
            self.casualties_waiting_for_treatment.sort(
                key=lambda c: c.survival_with_care - c.survival_without_care, reverse=True)
            for casualty in self.casualties_waiting_for_treatment:
                if total_care_time >= casualty.required_care_time:
                    # Casualty receives full treatment
                    casualty.received_care_time = casualty.required_care_time
                    total_care_time -= casualty.required_care_time
                    survival_chance = casualty.survival_with_care
                    reward += survival_chance * 10  # Amplified reward
                elif total_care_time > 0:
                    # Casualty receives partial treatment
                    casualty.received_care_time = total_care_time
                    total_care_time = 0
                    # Calculate survival chance based on proportion of care time received
                    proportion = casualty.received_care_time / casualty.required_care_time
                    survival_chance = casualty.survival_without_care + (casualty.survival_with_care - casualty.survival_without_care) * proportion
                    reward += survival_chance * 10  # Amplified reward
                else:
                    # No more care time available; casualty does not receive treatment
                    survival_chance = casualty.survival_without_care
                    reward += survival_chance * 1  # Minimal reward

            # Bonuses for resource utilization
            if self.available_beds == 0:
                reward += 1  # Bonus for full bed utilization
            if self.available_helicopter_seats == 0:
                reward += 1  # Bonus for full helicopter utilization
            if self.available_blood_units == 0:
                reward += 0.5  # Bonus for using all blood units
            if total_care_time == 0:
                reward += 1  # Bonus for full utilization of care time

        return next_state, reward, done

# Initialize Q-table as a nested dictionary
Q_table = {}

# Q-learning algorithm
def train_agent():
    env = Environment()
    for episode in range(NUM_EPISODES):
        state = env.reset()
        done = False

        while not done:
            state_key = state
            # Initialize Q-values for new states
            if state_key not in Q_table:
                Q_table[state_key] = {}

            possible_actions = env.get_possible_actions()

            # Initialize Q-values for new actions in the state
            for action in possible_actions:
                if action not in Q_table[state_key]:
                    Q_table[state_key][action] = 0.0

            # Epsilon-greedy action selection
            if random.uniform(0, 1) < EPSILON:
                action = random.choice(possible_actions)
            else:
                # Choose the best action from Q-table
                q_values = [Q_table[state_key][a] for a in possible_actions]
                max_q = max(q_values)
                max_actions = [a for a, q in zip(possible_actions, q_values) if q == max_q]
                action = random.choice(max_actions)

            # Take action
            next_state, reward, done = env.step(action)
            next_state_key = next_state

            # Initialize Q-values for the next state
            if next_state_key not in Q_table:
                Q_table[next_state_key] = {}

            # Get the maximum Q-value for the next state
            if Q_table[next_state_key]:
                max_future_q = max(Q_table[next_state_key].values())
            else:
                max_future_q = 0.0

            # Q-learning update
            current_q = Q_table[state_key][action]
            td_target = reward + GAMMA * max_future_q
            td_delta = td_target - current_q
            Q_table[state_key][action] += ALPHA * td_delta

            state = next_state

# Run the training
train_agent()

# Generate the recommended strategy based on the learned Q-table
def get_recommended_strategy():
    env = Environment()
    state = env.reset()
    done = False
    allocations = []

    # Open a text file for writing the output
    with open('output.txt', 'w') as file:
        while not done:
            state_key = state
            possible_actions = env.get_possible_actions()

            if state_key not in Q_table or not Q_table[state_key]:
                action = random.choice(possible_actions)
            else:
                # Initialize Q-values for new actions in the state
                for action in possible_actions:
                    if action not in Q_table[state_key]:
                        Q_table[state_key][action] = 0.0
                q_values = [Q_table[state_key][a] for a in possible_actions]
                max_q = max(q_values)
                max_actions = [a for a, q in zip(possible_actions, q_values) if q == max_q]
                action = random.choice(max_actions)

            allocations.append(action)
            state, _, done = env.step(action)

        # After allocations, simulate treatment
        total_care_time = TOTAL_CARE_TIME
        casualties_waiting = env.casualties_waiting_for_treatment
        # Sort casualties by survival benefit (optional)
        casualties_waiting.sort(key=lambda c: c.survival_with_care - c.survival_without_care, reverse=True)
        for casualty in casualties_waiting:
            if total_care_time >= casualty.required_care_time:
                casualty.received_care_time = casualty.required_care_time
                total_care_time -= casualty.required_care_time
            elif total_care_time > 0:
                casualty.received_care_time = total_care_time
                total_care_time = 0
            else:
                casualty.received_care_time = 0.0

        # Output the allocations
        bed_allocations = []
        helicopter_allocations = []
        no_care_allocations = []
        total_care_time_used = TOTAL_CARE_TIME - total_care_time

        output_lines = []

        output_lines.append("\nRecommended Strategy:")
        for casualty in casualties:
            if casualty.allocation == 'bed':
                bed_allocations.append(casualty.id)
                line = f"Casualty {casualty.id} allocated to bed:"
                print(line)
                file.write(line + '\n')
                line = f"  Required blood units: {casualty.required_blood_units}"
                print(line)
                file.write(line + '\n')
                line = f"  Required care time: {casualty.required_care_time:.2f} hours"
                print(line)
                file.write(line + '\n')
                line = f"  Received care time: {casualty.received_care_time:.2f} hours"
                print(line)
                file.write(line + '\n')
                if casualty.received_care_time > 0:
                    if casualty.received_care_time >= casualty.required_care_time:
                        line = f"  Survival chance: {casualty.survival_with_care:.2f}"
                    else:
                        proportion = casualty.received_care_time / casualty.required_care_time
                        survival_chance = casualty.survival_without_care + (casualty.survival_with_care - casualty.survival_without_care) * proportion
                        line = f"  Partial treatment survival chance: {survival_chance:.2f}"
                else:
                    line = f"  No treatment received, survival chance: {casualty.survival_without_care:.2f}"
                print(line)
                file.write(line + '\n')
            elif casualty.allocation == 'helicopter':
                helicopter_allocations.append(casualty.id)
                line = f"Casualty {casualty.id} allocated to helicopter:"
                print(line)
                file.write(line + '\n')
                line = f"  Required blood units: {casualty.required_blood_units}"
                print(line)
                file.write(line + '\n')
                line = f"  Survival with care: {casualty.survival_with_care:.2f}"
                print(line)
                file.write(line + '\n')
            elif casualty.allocation == 'none':
                no_care_allocations.append(casualty.id)
                line = f"Casualty {casualty.id} received no care:"
                print(line)
                file.write(line + '\n')
                line = f"  Survival without care: {casualty.survival_without_care:.2f}"
                print(line)
                file.write(line + '\n')

        line = f"\nTotal care time used: {total_care_time_used:.2f} hours out of {TOTAL_CARE_TIME} hours"
        print(line)
        file.write(line + '\n')
        line = f"Total blood units used: {NUM_BLOOD_UNITS - env.available_blood_units} out of {NUM_BLOOD_UNITS}"
        print(line)
        file.write(line + '\n')
        line = f"Patients allocated to beds: {bed_allocations}"
        print(line)
        file.write(line + '\n')
        line = f"Patients allocated to helicopter: {helicopter_allocations}"
        print(line)
        file.write(line + '\n')
        line = f"Patients receiving no care: {no_care_allocations}"
        print(line)
        file.write(line + '\n')

get_recommended_strategy()
