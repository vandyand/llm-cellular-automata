import json
import os
from openai_base import fetch_openai_json, gen_user_message_record, gen_message_record
import diskcache
from concurrent.futures import ThreadPoolExecutor
import random
import string

def initialize_array(size):
    return [json.loads(f'{{"index": {i}}}') for i in range(size)]

def get_cell_system_message(cell):
    index = cell['index']
    name = cell['name']
    id = cell['id']
    mission = cell['mission']
    return (
        f"You are cell {name}\n"
        f"with id: {id}\n"
        f"with index: {index}\n"
        f"with mission: {mission}\n"
        "Please respond in JSON format of your updated state according to the specified schema."
        "Please fill in any missing data."
    )

def process_json_cell(i, cell, cells, cell_t_minus_1):
    cell_n_minus_1 = cells[i-1] if i > 0 else cells[-1]
    cell_n_plus_1 = cells[i+1] if i < len(cells) - 1 else cells[0]

    if cell.get('id') or cell_n_minus_1.get('id') or cell_n_plus_1.get('id'):
        response = fetch_openai_json(
            messages=[
                gen_message_record("system", "Help the current cell achieve its mission. Please respond in JSON format representing new current cell state."),
                gen_user_message_record("Neighbor cell n-1 state (for reference):"),
                cell_n_minus_1,
                gen_user_message_record("Neighbor cell n+1 state (for reference):"),
                cell_n_plus_1,
                gen_user_message_record("Current cell t-1 state (your previous state, last timestep):"),
                cell_t_minus_1,
                gen_user_message_record("Current cell n state (your current state, current timestep):"),
                cell,
                gen_user_message_record("Please respond with new state based on provided info."),
            ],
            json_schema={}
        )
        # print(i, response, "\n\n")
        return response
    else:
        return cell

def process_json_cells(cells, cells_t_minus_1):
    results = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_json_cell, i, cell, cells, cells_t_minus_1[i]) for i, cell in enumerate(cells)]
        for future in futures:
            results.append(future.result())

    return results

def get_random_string(size=10):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(size))

if __name__ == '__main__':
    size = 11  # You can change this size as needed
    cache = diskcache.Cache('cell_cache')

    schema = {
        "type": "object",
        "properties": {
            "index": {"type": "integer"},
            "name": {"type": "string"},
            "id": {"type": "string"},
            "mission": {"type": "string"},
            "state": {"type": "string"}
        },
        "required": ["index", "name", "id", "mission", "state"]
    }

    if 'cells' in cache:
        cells = cache['cells']
        cells_t_minus_1 = cache['cells_t_minus_1']
        print("Loaded cells from cache.")
    else:
        cells = initialize_array(size)
        cells_t_minus_1 = initialize_array(size)
        print("Initialized new cells array.")

        # Example: Manually populate the cells for optimal fun for intriguing and interesting complex behavior
        cells[0] = {'index': 0, 'name': 'Alpha Cell', 'id': 'alpha-001', 'mission': 'Concatenation Mission: Concatenate the states of the neighboring cells.', 'state': get_random_string()}
        cells[1] = {'index': 1, 'name': 'Beta Blob', 'id': 'beta-002', 'mission': 'Substring Mission: Extract a substring from the concatenated states of neighbors.', 'state': get_random_string()}
        cells[2] = {'index': 2, 'name': 'Gamma Goo', 'id': 'gamma-003', 'mission': 'Palindrome Mission: Ensure the state is a palindrome.', 'state': get_random_string()}
        cells[3] = {'index': 3, 'name': 'Delta Droid', 'id': 'delta-004', 'mission': 'Length Comparison Mission: Adjust state to be shorter than the average length of neighbors.', 'state': get_random_string()}
        cells[4] = {'index': 4, 'name': 'Epsilon Entity', 'id': 'epsilon-005', 'mission': 'Prefix Mission: Add a common prefix based on neighbors.', 'state': get_random_string()}
        cells[5] = {'index': 5, 'name': 'Zeta Zapper', 'id': 'zeta-006', 'mission': 'Vowel Count Mission: Adjust state to have the same number of vowels as the average of neighbors.', 'state': get_random_string()}
        cells[6] = {'index': 6, 'name': 'Eta Echo', 'id': 'eta-007', 'mission': 'Alphabetical Order Mission: Modify state to be alphabetically between neighbors.', 'state': get_random_string()}
        cells[7] = {'index': 7, 'name': 'Theta Thunder', 'id': 'theta-008', 'mission': 'Reverse Mission: Reverse state of the combined states of neighbors.', 'state': get_random_string()}
        cells[8] = {'index': 8, 'name': 'Iota Ion', 'id': 'iota-009', 'mission': 'Pattern Matching Mission: Change state to match a pattern found in neighbors.', 'state': get_random_string()}
        cells[9] = {'index': 9, 'name': 'Kappa Knight', 'id': 'kappa-010', 'mission': 'Character Frequency Mission: Adjust state to have a similar character frequency distribution as neighbors.', 'state': get_random_string()}
        cells[10] = {'index': 10, 'name': 'Lambda Lion', 'id': 'lambda-011', 'mission': 'Random String Mission: Generate a new random string of length 10.', 'state': get_random_string()}

    # Display the initial state
    print("Initial state:", cells, "\n\n")

    # Process the cells and get new states
    new_states = process_json_cells(cells, cells_t_minus_1)

    print("New states:")
    for state in new_states:
        print(state, "\n")
    print("\n\n")

    # Update the cache with the new states
    cache['cells'] = new_states
    cache['cells_t_minus_1'] = cells
    cache.close()
