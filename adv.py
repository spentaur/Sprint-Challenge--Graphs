from room import Room
from player import Player
from world import World

import random
from ast import literal_eval
from collections import deque

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph = literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []

"""
my code starts here
"""


class TraversalGraph:
    def __init__(self, rooms={}):
        self.rooms = rooms
        self.curr_room = None
        self.curr_room_id = None
        self.prev_room = None
        self.prev_room_id = None
        self.invert_dir = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}

    def __len__(self):
        return len(self.rooms)

    def __str__(self):
        return str(
            f"rooms: {self.rooms} \n curr_room: {self.curr_room}")

    def move_room(self, new_room, prev_room=None):
        self.curr_room = self.rooms[new_room.id]
        self.curr_room_id = new_room.id
        if prev_room:
            self.prev_room = self.rooms[prev_room.id]
            self.prev_room_id = prev_room.id
        return self

    def exploring(self):
        if '?' in self.curr_room:
            return True
        else:
            return False

    def add_and_move_room(self, new_room, prev_room=None,
                          direction_came_from=None):
        exits = new_room.get_exits()

        self.rooms[new_room.id] = {
            '?': set(direction for direction in exits)
        }
        if (direction_came_from) and (prev_room):
            self.rooms[new_room.id][self.invert_dir[direction_came_from]
                                    ] = prev_room.id
            self.rooms[prev_room.id][direction_came_from] = new_room.id
            self.rooms[prev_room.id]['?'].remove(direction_came_from)
            self.rooms[new_room.id]['?'].remove(
                self.invert_dir[direction_came_from])

            if len(self.rooms[new_room.id]['?']) == 0:
                del self.rooms[new_room.id]['?']

            if len(self.rooms[prev_room.id]['?']) == 0:
                del self.rooms[prev_room.id]['?']

        self.move_room(new_room, prev_room)
        return self

    def get_random_unseen_direction(self):
        return random.choice(list(self.curr_room['?']))

    def update_room(self):
        pass

    def room_has_unseen(self, room_id):
        return '?' in self.rooms[room_id]

    def path_to_unseen(self):
        seen = set()
        queue = [[self.curr_room]]

        while queue:
            path = queue.pop(0)
            neighbor = path[-1]
            neighbor_id = list(neighbor.values())[0]
            if neighbor_id not in seen:
                neighbor_neighbors = self.rooms[neighbor_id]
                for direction, room_id in neighbor_neighbors.items():
                    new_path = list(path)
                    if direction == '?':
                        return new_path
                    new_path.append({direction: room_id})
                    queue.append(new_path)

                # mark node as explored
                seen.add(neighbor_id)
        return 'FAIL'


previous_dir = None

trav_graph = TraversalGraph()
trav_graph.add_and_move_room(player.current_room)

while len(trav_graph) < len(room_graph):
    prev_room = player.current_room
    if trav_graph.exploring():
        # explore randomly until i hit a deadend
        random_direction = trav_graph.get_random_unseen_direction()
        player.travel(random_direction)
        trav_graph.add_and_move_room(
            player.current_room,
            prev_room,
            random_direction)
        traversal_path.append(random_direction)
    else:
        # bfs backtracking to find room with unexplored neighbors
        back_track_path = trav_graph.path_to_unseen()
        for instruct in back_track_path:
            instruct_dir = list(instruct.keys())[0]
            traversal_path.append(instruct_dir)
            prev_room = player.current_room
            player.travel(instruct_dir)
            trav_graph.move_room(player.current_room, prev_room)

"""
my code ends here
"""

# TRAVERSAL TEST - DO NOT MODIFY
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(
        f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")


#######
# UNCOMMENT TO WALK AROUND
#######
player.current_room.print_room_description(player)
while True:
    cmds = input("-> ").lower().split(" ")
    if cmds[0] in ["n", "s", "e", "w"]:
        player.travel(cmds[0], True)
    elif cmds[0] == "q":
        break
    else:
        print("I did not understand that command.")
