import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

factory_count = int(input())  # the number of factories
link_count = int(input())  # the number of links between factories

graph = {}

for i in range(link_count):
    factory_1, factory_2, distance = [int(j) for j in input().split()]
    if distance in graph.keys():
        graph[distance].append((factory_1,factory_2))
    else:
        graph[distance] = [(factory_1,factory_2)]

graph = {k: graph[k] for k in sorted(graph)}

print(graph, file=sys.stderr, flush=True)

initial_enemy_base = {}

my_bombs_left = 2
enemy_bombs_left = 2

def get_factory_by_id(factories=[], entity_id=None):
    for f in factories:
        if f['entity_id'] == entity_id:
            return f

    return None


# game loop
while True:

    factories = []
    troops = []
    bombs = []
    message = ""

    entity_count = int(input())  # the number of entities (e.g. factories and troops)
    for i in range(entity_count):
        inputs = input().split()
        entity_id = int(inputs[0])
        entity_type = inputs[1]
        arg_1 = int(inputs[2])
        arg_2 = int(inputs[3])
        arg_3 = int(inputs[4])
        arg_4 = int(inputs[5])
        arg_5 = int(inputs[6])

        if entity_type == 'FACTORY':
            factories.append({
                "entity_id": entity_id,
                "owner": arg_1,         # 1=mine, -1=enemy, 0=netural
                "cyborgs": arg_2,
                "production": arg_3,    # between 0 and 3
                "blocked_left": arg_4,  # 0 means normal
                "score": float(0)
            })

        if entity_type == 'TROOP':
            troops.append({
                "entity_id": entity_id,
                "owner": arg_1,         # 1=mine, -1=enemy
                "src": arg_2,
                "dst": arg_3,
                "cyborgs": arg_4,
                "turns_left": arg_5
            })

        if entity_type == 'BOMB':
            bombs.append({
                "owner": arg_1,         # 1=mine, -1=enemy
                "src": arg_2,
                "dst": arg_3,           # only owner can see
                "turns_left": arg_4     # only owner can see
            })

    my_factories = [f for f in factories if f["owner"] == 1 and f["blocked_left"] == 0]
    my_slow_factories = [f for f in my_factories if f['production'] < 3 ]
    my_fast_factories = [f for f in my_factories if f['production'] > 0 ]
    my_slow_factories.sort(key=lambda f: f['production'])
    my_large_factories = [f for f in my_factories if f['cyborgs'] >= 10 ]

    my_ready_cyborgs = sum([f['cyborgs'] for f in my_factories])

    my_factories.sort(key=lambda f: f['cyborgs'], reverse=True)
    print(my_factories, file=sys.stderr, flush=True)

    my_production = sum([f['production'] for f in my_factories])

    my_factories_ids = [f["entity_id"] for f in my_factories]
    print(my_factories_ids, file=sys.stderr, flush=True)
    #my_troops = [t for t in troops if t["owner"] == 1]
    my_bombs = [b for b in bombs if b["owner"] == 1]

    attack_factories = [f for f in factories if f["owner"] != 1]
    attack_factories.sort(key=lambda f: f['production'], reverse=True)

    neutral_factories = [f for f in factories if f["owner"] == 0]
    neutral_factories_rich = [f for f in neutral_factories if f["production"] > 0]
    neutral_factories.sort(key=lambda f: f['production'], reverse=True)
    enemy_factories = [f for f in factories if f["owner"] == -1]

    if not initial_enemy_base:
        initial_enemy_base = enemy_factories[0]

    enemy_fast_factories = [f for f in enemy_factories if f['production'] == 3 ]
    enemy_troops = [t for t in troops if t["owner"] == -1]
    enemy_bombs = [b for b in bombs if b["owner"] == -1]


    if len(enemy_troops) == 0 and len(enemy_factories) == 0:
        break

    bomb_detected = False

    # bomb detected
    if len(enemy_bombs) > 0:
        bomb_detected = True
        enemy_bombs_left -= 1

    # handle when to send my bomb
    # possibly to the large producing factories
    if len(my_bombs) == 0 and my_bombs_left > 0 and len(enemy_fast_factories) > 0:

        bomb_src = None
        bomb_dst = None

        #determine dst
        bomb_dst = [f for f in enemy_fast_factories if f['blocked_left'] == 0]
        bomb_dst = sorted(bomb_dst,key=lambda f: f['cyborgs'], reverse=True)
        if len(bomb_dst) > 0:
            bomb_dst = bomb_dst[0]['entity_id']
            my_bombs_left -=1

            #determine closest src to dst
            for f in my_factories:
                curr_node = f['entity_id']
                for dist,paths in graph.items():
                    for path in paths:
                        if curr_node in path and bomb_dst in path:
                            bomb_src = curr_node
                            break

            if bomb_src != None and bomb_dst != None:
                message+=f"BOMB {bomb_src} {bomb_dst};MSG Live for the Swarm!;"

    # check production rate
    if my_production==0 and len(my_factories)>0:
        #increase production
        if my_factories[0]['cyborgs']>10:
            message += f"INC {my_factories[0]['entity_id']};"

    # increase production if there's factories with large cyborgs count
    if not bomb_detected and len(my_large_factories) > 0 and len(my_slow_factories) > 0:

        # TODO: sort by furthest from the enemy
        my_large_factories_ids = [i["entity_id"] for i in my_large_factories]

        increase_src = None
        # search through large factories with slowest production
        for f in my_slow_factories:
            if f['entity_id'] in my_large_factories_ids:
                increase_src = f['entity_id']
                break

        if increase_src:
            message += f"INC {increase_src};"

    # identify the shortest path to a non-taken factory
    # TODO: consider weighted score of defense and distance
    # collect all possible destination and cyborgs in a list of tuples
    # sort the list for the lowest weight

    # TODO: consider opponent forces destination and numbers
    # send troops from the non-attacked source
    # consider the amount of troops to send based

    factories_under_attack = {}

    for troop in enemy_troops:
        t = troop['dst']
        if t in my_factories_ids:
            if t in factories_under_attack.keys():
                factories_under_attack[t].append((troop['cyborgs'],troop['turns_left']))
            else:
                factories_under_attack[t] = [(troop['cyborgs'],troop['turns_left'])]

    if len(my_factories) == 0:
        message+="WAIT"
    else:

        attacked_dst = []

        for f in my_factories:

            total_attacking_cyborgs = 0

            # wait to increase
            if f['production'] < 3 and len(neutral_factories_rich) == 0:
                message += f"INC {f['entity_id']};"

            if f['entity_id'] in factories_under_attack.keys():
                print("Defense action",file=sys.stderr, flush=True)
                total_attacking_cyborgs = 0
                for troop in factories_under_attack[f['entity_id']]:
                    total_attacking_cyborgs += troop[0]

                if bomb_detected:
                    for bomb in enemy_bombs:
                        if bomb['turns_left'] > 1:
                            continue

            print("Attack action",file=sys.stderr, flush=True)
            stop_draining = False

            move_src = f
            if move_src['blocked_left'] != 0 or move_src['cyborgs'] == 0:
                continue

            to_attack = []

            if f"INC {move_src['entity_id']};" in message:
                cyborgs_left_src = move_src['cyborgs'] - 10
            else:
                cyborgs_left_src = move_src['cyborgs']

            cyborgs_left_src -= total_attacking_cyborgs

            if cyborgs_left_src < 1:
                continue

            curr_node = f['entity_id']

            potential_dst = {}
            filtered_attack_dst = []

            #identify possible cyborgs destinations
            for dist,paths in graph.items():
                for src,dst in paths:
                    if curr_node in (src, dst):
                        if src in my_factories_ids and dst not in my_factories_ids:
                            final_dst = dst
                        if dst in my_factories_ids and src not in my_factories_ids:
                            final_dst = src

                        dst_factory = get_factory_by_id(attack_factories, final_dst)
                        if dist in potential_dst.keys():
                            potential_dst[dist].append(dst_factory)
                        else:
                            potential_dst[dist] = [dst_factory]

            print(f"potential_dst for {f['entity_id']}", file=sys.stderr, flush=True)
            print(potential_dst, file=sys.stderr, flush=True)

            if potential_dst != {}:
                for dist,factories in potential_dst.items():
                    for dst in factories:
                        for f in attack_factories:
                            if dst and f:
                                if dst['entity_id'] == f['entity_id']:
                                    dst['score'] = float(dst['cyborgs'] * 0.5 + dst['production'] * 0.5 + dist)
                                    filtered_attack_dst.append(dst)

            if filtered_attack_dst != []:

                filtered_attack_dst.sort(key=lambda f: f['score'])
                print(f"filtered_attack_dst for {f['entity_id']}",file=sys.stderr,flush=True)
                print(filtered_attack_dst,file=sys.stderr,flush=True)

                for dst in filtered_attack_dst:

                    move_dst = dst

                    if move_dst['entity_id'] in [b['dst'] for b in my_bombs]:
                        continue

                    if move_src != move_dst and move_dst['entity_id']:

                        attacked_dst.append(move_dst['entity_id'])

                        move_size = move_dst['cyborgs'] + 1
                        if move_size > 0:
                            cyborgs_left_src -= move_size
                            message += f"MOVE {move_src['entity_id']} {move_dst['entity_id']} {move_size};"
                            if cyborgs_left_src <=0 or stop_draining:
                                break

            if stop_draining:
                continue

        if message == "":
            message == "WAIT;"

        message += "MSG Attack!;"

    print(message)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    # Any valid action, such as "WAIT" or "MOVE source destination cyborgs"
    #print("WAIT")
