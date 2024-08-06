import json

def initialize_grid(size):
    return [json.loads('{}') for _ in range(size)]

def display_grid(grid):
    print(grid)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Initialize a 1D array of empty JSON objects.')
    parser.add_argument('size', type=int, help='Size of the array')
    
    args = parser.parse_args()
    
    grid = initialize_grid(args.size)
    display_grid(grid)
