# Process:
# - ml model, comm visualiser, comm eval, comm relay
# To try:
# debug mqtt connection error -> temp failure in name resolution (try to change broker to mosquitto, update in viz code too), broken pipe -> relay
# try send data see still got duplicate action on p1 and p2?
# shoot start timer for vest to receive data -> shoot needs to have time window for the vest data to come in (if timeout -> miss bullet)
# pkt[0]: type of sender (0: imu sensor (glove)-> give ml, 1: ir receiver(vest), 2: shoot(gun))
# need to send data to viz cause got test wo eval server (if action is invalid dont send to viz)
# implement logout

# Todo:
# 2 player -> wait for both player action to come before send to eval/do anything (cant have player with "none" action)
# 2 player: can either have shield first then damage or vice versa
# continue action after the broken pipe nonetype error or the mqqt temp name resolution error too
# try out hivemq


from Crypto.Cipher import AES
from paho.mqtt import client as mqtt_client
from Crypto.Util.Padding import pad
from Crypto import Random
import threading
import base64
import socket
from _socket import SHUT_RDWR
import sys
import json
import time
from multiprocessing import Pipe

mqtt_broker = "test.mosquitto.org"  # 'broker.emqx.io'  # Public broker
mqtt_port = 1883

DEFAULT_STATE = {
    "hp": 100,
    "action": "none",
    "bullets": 6,
    "grenades": 2,
    "shield_time": 0,
    "shield_health": 0,
    "num_deaths": 0,
    "num_shield": 3
}

INITIAL_STATE = {
    "p1": DEFAULT_STATE,
    "p2": DEFAULT_STATE
}

BULLET_DAMAGE = 10
GRENADE_DAMAGE = 30
SHIELD_TIME = 10
SHIELD_HEALTH = 30

# pkt[0]: type of sender (0: imu sensor (glove)-> give ml, 1: ir receiver(vest), 2: shoot(gun))
GLOVE = 0
VEST = 1
GUN = 2
SHOT_FIRED = 188
SHOT_HIT = 161

# state_lock = threading.Lock()
curr_state = INITIAL_STATE
shield_start = {"p1": None, "p2": None}  # both player has no shield
has_incoming_shoot = {"p1": Queue(), "p2": Queue()}


def read_state():
    # state_lock.acquire()
    data = curr_state
    # state_lock.release()
    return data


def input_state(data):
    global curr_state
    # state_lock.acquire()
    curr_state = data
    # state_lock.release()


# Data buffer
move_res_buffer = Queue()  # predicted action
move_data_buffer = Queue()  # data relayed from internal comms
eval_buffer = Queue()  # game state
viz_send_buffer = Queue()  # game state
viz_recv_buffer = Queue()  # bool value for grenade hit

# Connections
has_terminated = False


# Game engine logic


def opp_player(player):
    if player == "p1":
        return "p2"
    else:
        return "p1"


def revive_player(state, player):
    state[player]["hp"] = 100
    state[player]["num_deaths"] += 1
    state[player]["num_shield"] = 3
    state[player]["grenades"] = 2
    state[player]["bullets"] = 6
    return state


def failed_shot(player):
    global has_incoming_shoot
    has_incoming_shoot[player].pop()
    print("[Game engine] Shot to ", player, " has missed")


def execute_action(player, action):
    global has_incoming_shoot
    state = read_state()
    other_player = opp_player(player)

    # do sth based on action ["grenade", "reload", "logout", "shield"]
    state[player]["action"] = action

    # Recalculate shield time
    if shield_start[player]:
        time_elapsed = time.time() - shield_start[player]
        if time_elapsed >= SHIELD_TIME:
            shield_start[player] = None
            state[player]["shield_time"] = 0
            state[player]["shield_health"] = 0
        else:
            state[player]["shield_time"] = SHIELD_TIME - int(time_elapsed)

    if shield_start[other_player]:
        time_elapsed = time.time() - shield_start[other_player]
        if time_elapsed >= SHIELD_TIME:
            shield_start[other_player] = None
            state[other_player]["shield_time"] = 0
            state[other_player]["shield_health"] = 0
        else:
            state[other_player]["shield_time"] = SHIELD_TIME - \
                int(time_elapsed)

    # Execute action
    if action == "grenade":
        if state[player]["grenades"]:
            state[player]["grenades"] -= 1
        else:
            print("[Game engine] Cannot ", action, ". Only have ", state[player]
                  ["grenades"],  " grenade")
    elif action == "reload":
        if state[player]["bullets"] <= 0:
            state[player]["bullets"] = 6
        else:
            print("[Game engine] Cannot ", action, ". Still have ", state[player]
                  ["bullets"],  "bullets")
    elif action == "shoot":
        if state[player]["bullets"] <= 0:
            print("[Game engine] Cannot ", action, ".  Player has ", state[player]
                  ["bullets"],  "bullet")
        else:
            state[player]["bullets"] -= 1

            # Start timer to vest data to come
            has_incoming_shoot[other_player].put(threading.Timer(
                2, failed_shot, other_player))  # 2s response for vest response
    elif action == "shield":
        if not shield_start[player] and state[player]["num_shield"]:
            state[player]["shield_time"] = SHIELD_TIME
            state[player]["shield_health"] = SHIELD_HEALTH
            state[player]["num_shield"] -= 1
            shield_start[player] = time.time()
        else:
            print("[Game engine] ", int(
                time.time() - shield_start[player]),  " seconds after previous shield")
    elif action == "vest":  # this vest is already opposite player's vest
        # ignore if no existing timer for shoot
        if not has_incoming_shoot[player].empty():
            print("[Game engine] Player ", player, " has been hit")
            has_incoming_shoot[player].get().cancel()

            if state[player]["shield_health"]:
                state[player]["shield_health"] -= BULLET_DAMAGE

                if state[player]["shield_health"] < 0:
                    state[player]["hp"] += state[player]["shield_health"]
                    state[player]["shield_health"] = 0
            else:
                state[player]["hp"] -= BULLET_DAMAGE
    elif action == "logout":
        print("[Game engine] Player ", player, " has logged out")
    else:
        print("[Game engine] Unknown action: ", action)

    # Revive player if dead
    if state[other_player]["hp"] <= 0:
        state = revive_player(state, other_player)

    if state[player]["hp"] <= 0:
        state = revive_player(state, player)

    return state


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Invalid number of arguments')
        sys.exit()

    local_port = int(sys.argv[1])
    group_id = int(sys.argv[2])
    eval_port = int(sys.argv[3])
    eval_ip = sys.argv[4]
    secret_key = sys.argv[5]

    # Connection to visualizer
    recv_client = Mqtt("cg4002/4/u96_viz20")
    pub_client = Mqtt("cg4002/4/viz_u9620")

    # Receive messages
    recv_client.subscribe()
    recv_client.client.loop_start()

    # Publish messages
    pub_thread = threading.Thread(target=pub_client.publish, daemon=True)
    pub_thread.start()

    # Connection to relay
    conn_relay = Server(local_port, group_id)
    # conn_relay.setup_connection()
    conn_relay.start()

    # Connection to eval_server
    conn_eval = Client(eval_ip, eval_port, group_id, secret_key)
    conn_eval.start()

    # ML stuff
    model_pred = MovePredictor()
    model_pred.start()

    # Game engine (main thread)
    while not has_terminated:
        try:
            if not move_res_buffer.empty():
                action = move_res_buffer.get()
                print("[Game engine] Received action:", action)
                state = read_state()
                state = execute_action("p1", action)

                if state["p1"]["action"] == "logout":
                    has_terminated = True

                print("[Game engine] Resulting state:", state)

                if action != "grenade":
                    eval_buffer.put(state)
                    # print("[Game engine] Sent to eval:", state)

                state["sender"] = "u96"
                viz_send_buffer.put(state)
                print("[Game engine] Sent to visualiser:", state)

            if not viz_recv_buffer.empty():
                # Visualizer sends player that is hit by grenade
                player_hit = viz_recv_buffer.get()
                # print("[Game engine] Received from visualiser:", player_hit)
                state = read_state()
                if player_hit != "none":
                    # minus health based on grenade hit
                    if state[player_hit]["shield_health"]:
                        state[player_hit]["shield_health"] -= GRENADE_DAMAGE

                        if state[player_hit]["shield_health"] < 0:
                            state[player_hit]["hp"] += state[player_hit]["shield_health"]
                            state[player_hit]["shield_health"] = 0
                    else:
                        state[player_hit]["hp"] -= GRENADE_DAMAGE

                    # Revive player if dead
                    if state[player_hit]["hp"] <= 0:
                        state = revive_player(state, player_hit)

                input_state(state)
                eval_buffer.put(state)
                # print("[Game engine] Sent to curr state and eval:", state)
        except KeyboardInterrupt:
            print("[Game Engine] Keyboard interrupt")
            has_terminated = True
            break

    # Terminate all connections
    if(conn_relay):
        conn_relay.end_client_connection()
        print(conn_relay)
    if(conn_eval):
        conn_eval.end_client_connection()
    if(recv_client):
        recv_client.terminate()
        print(recv_client)
    if(pub_client):
        pub_client.terminate()

    print("Program terminated, thanks for playing :D")
