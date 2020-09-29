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
# world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
# traversal_path = []

"""
my code starts here
"""


class TravelGraph:
    def __init__(self, room_graph, player, path=[], rooms={}):
        self.room_graph = room_graph
        self.player = player
        self.path = path
        self.rooms = {}

    def invert(self, d):
        """
        Get the opposite direction. This is useful for backtracking.
        """
        inverter = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        return inverter[d]

    def add_room(self, r):
        """
        Add the room to the graph map.
        """
        self.rooms[r] = {direction: '?' for direction in r.get_exits()}

        return self

    def seen_room(self, r):
        """
        Return whether or not i've seen the room
        """
        return r in self.rooms

    def connect_rooms(self, r1, r2, d):
        """
        Add relationship between rooms.
        """
        self.rooms[r1][d] = r2
        self.rooms[r2][self.invert(d)] = r1

    def find_unexplored_room(self, r):
        """
        BFS to find shortest path to room with unexplored paths.
        """
        s = set()
        q = deque([[r, []]])
        while q:
            room, path = q.popleft()
            if room not in s:
                s.add(room)
                for direction in self.rooms[room]:
                    if self.rooms[room][direction] == '?':
                        return path
                    else:
                        new_path = list(path)
                        new_path.append(direction)
                        next_room = self.rooms[room][direction]
                        q.append([next_room, new_path])
        return []

    def still_unseen(self):
        """
        Return whether or not there's more unseen rooms
        """
        return len(self.rooms) < len(self.room_graph)

    def get_unseen_directions(self):
        """
        Return a list of directions that are unexplored. Return false if has none.
        """
        exits = [direction for direction,
                 seen in self.rooms[self.player.current_room].items() if seen == '?']
        if len(exits) == 0:
            return False

        return random.choice(exits)

    def move_if_worth_it(self, unseen_direction):
        """
        Move forward if it's a room I haven't explored yet.
        If i have, just go back and act like it never happened.
        """
        prev_room = self.player.current_room
        self.player.travel(unseen_direction)

        next_room = self.player.current_room
        self.path.append(unseen_direction)

        if self.seen_room(next_room) == False:
            self.add_room(next_room)
        else:
            self.player.travel(self.invert(unseen_direction))
            self.path.pop()

        self.connect_rooms(prev_room, next_room, unseen_direction)

        return self

    def explore(self):
        """
        Main function that traverses the graph.
        """
        self.add_room(self.player.current_room)
        while self.still_unseen():
            unseen_direction = self.get_unseen_directions()
            if unseen_direction:
                self.move_if_worth_it(unseen_direction)
            else:
                path_to_unexplored = self.find_unexplored_room(
                    self.player.current_room)
                self.path.extend(path_to_unexplored)
                for direction in path_to_unexplored:
                    self.player.travel(direction)
        return self.path


trav_graph = TravelGraph(room_graph, player)
traversal_path = trav_graph.explore()

# Finished and it does it in 997 moves. Could be refactored.

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
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")
