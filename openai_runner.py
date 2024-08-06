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

def process_json_cell(json_schema, i, cell, cells, cell_t_minus_1):
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
            json_schema=json_schema
        )
        cell['state'] = response['state']
        return cell
    else:
        return cell

def process_json_cells(json_schema, cells, cells_t_minus_1):
    results = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_json_cell, json_schema, i, cell, cells, cells_t_minus_1[i]) for i, cell in enumerate(cells)]
        for future in futures:
            results.append(future.result())

    return results

def get_random_string(size=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))

def get_random_mission():
    with open('missions.json') as f:
        missions = json.load(f)
    return random.choice(missions)

if __name__ == '__main__':
    size = 11  # You can change this size as needed
    cache = diskcache.Cache('cell_cache')

    schema = {
        "type": "object",
        "properties": {
            "index": {"type": "integer"},
            "name": {"type": "string"},
            "id": {"type": "string"},
            "mission": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["name", "description"]
            },
            "state": {"type": "string"}
        },
        "required": ["state"]
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
        cells[0] = {'index': 0, 'name': 'Alpha Cell', 'id': 'alpha-001', 'mission': get_random_mission(), 'state': get_random_string()}
        cells[1] = {'index': 1, 'name': 'Beta Blob', 'id': 'beta-002', 'mission': get_random_mission(), 'state': get_random_string(3)}
        cells[2] = {'index': 2, 'name': 'Gamma Goo', 'id': 'gamma-003', 'mission': get_random_mission(), 'state': get_random_string()}
        cells[3] = {'index': 3, 'name': 'Delta Droid', 'id': 'delta-004', 'mission': get_random_mission(), 'state': get_random_string()}
        cells[4] = {'index': 4, 'name': 'Epsilon Entity', 'id': 'epsilon-005', 'mission': get_random_mission(), 'state': get_random_string()}
        cells[5] = {'index': 5, 'name': 'Zeta Zapper', 'id': 'zeta-006', 'mission': get_random_mission(), 'state': get_random_string()}
        cells[6] = {'index': 6, 'name': 'Eta Echo', 'id': 'eta-007', 'mission': get_random_mission(), 'state': get_random_string()}
        cells[7] = {'index': 7, 'name': 'Theta Thunder', 'id': 'theta-008', 'mission': get_random_mission(), 'state': get_random_string()}
        cells[8] = {'index': 8, 'name': 'Iota Ion', 'id': 'iota-009', 'mission': get_random_mission(), 'state': get_random_string()}
        cells[9] = {'index': 9, 'name': 'Kappa Knight', 'id': 'kappa-010', 'mission': get_random_mission(), 'state': get_random_string()}
        cells[10] = {'index': 10, 'name': 'Lambda Lion', 'id': 'lambda-011', 'mission': get_random_mission(), 'state': get_random_string()}

        for cell in cells:
            print(cell['mission']['name'], "->", cell['state'], "\n")

    # Display the initial state
    # print("Initial state:", cells, "\n\n")

    # Process the cells and get new states
    new_states = process_json_cells(schema, cells, cells_t_minus_1)

    print("New states:")
    for state in new_states:
        print(state['mission']['name'], "->", state['state'],"\n")
    print("\n\n")

    # Update the cache with the new states
    cache['cells'] = new_states
    cache['cells_t_minus_1'] = cells
    cache.close()
