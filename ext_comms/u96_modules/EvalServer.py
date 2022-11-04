from multiprocessing import dummy
import threading
import multiprocessing
import socket
import time
from _socket import SHUT_RDWR
from queue import Empty
from GameState import GameState

P1 = 0
P2 = 1
BOTH = 2
ALL = 3
# put in total move (on screen) - 1
TOTAL_MOVE = 18


def clear(q):
    try:
        while not q.empty():
            q.get_nowait()
    except (Empty, EOFError) as e:
        pass


class EvalServer(multiprocessing.Process):
    # Client to eval_server
    def __init__(self, ip_addr, port_num, group_id, secret_key, eval_pred, eval_relay, eval_viz, viz_eval_p1, viz_eval_p2, has_terminated, has_incoming_bullet_p1, has_incoming_bullet_p2):
        super().__init__()  # init parent (Thread)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (ip_addr, port_num)
        self.group_id = group_id
        self.secret_key = secret_key
        # has received p1, p2 actions
        self.has_action = [threading.Event(), threading.Event()]
        self.has_shield = [threading.Event(), threading.Event()]
        self.has_incoming_bullet_p1 = has_incoming_bullet_p1
        self.has_incoming_bullet_p2 = has_incoming_bullet_p2

        self.gamestate = GameState(main=self)  # static
        self.has_terminated = has_terminated
        self.action_counter = 0
        self.daemon = True

        self.eval_pred = eval_pred
        self.eval_relay = eval_relay
        self.eval_viz = eval_viz
        self.viz_eval_p1 = viz_eval_p1
        self.viz_eval_p2 = viz_eval_p2

    def run(self):
        self.conn.connect(self.server_address)
        print("[Eval server] Connection established to:", self.server_address)

        recv_thread = threading.Thread(target=self.receive_data)
        recv_thread.start()

        glove_thread = threading.Thread(target=self.process_glove)
        glove_thread.start()

        gun_thread = threading.Thread(target=self.process_others)
        gun_thread.start()

        while not self.has_terminated.value:
            if self.action_counter >= TOTAL_MOVE:
                time.sleep(10)
                print("Logout move")
                self.gamestate.update_player("logout", P1)
                self.eval_viz.put(self.gamestate.get_data_plain_text(P1))
                self.gamestate.update_player("logout", P2)
                self.eval_viz.put(self.gamestate.get_data_plain_text(P2))
                self.gamestate.send_encrypted(self.conn, self.secret_key)
                self.logout()
                break

            # Process if both players have done an action
            print("Waiting action")
            self.has_action[P1].wait()
            self.has_action[P2].wait()

            # Set shield if got
            if self.has_shield[P1].is_set():
                self.gamestate.update_player('shield', P1)
                self.eval_viz.put(
                    self.gamestate.get_data_plain_text(P1))

            if self.has_shield[P2].is_set():
                self.gamestate.update_player('shield', P2)
                self.eval_viz.put(
                    self.gamestate.get_data_plain_text(P2))

            print("Adjusting data")
            self.gamestate.update_player('adjust_data', P1)
            self.gamestate.update_player('adjust_data', P2)

            print("Sending to eval...")
            self.gamestate.send_encrypted(self.conn, self.secret_key)

            # Clear all pending data in pipe
            print("Clearing eval queues")
            clear(self.eval_pred)
            clear(self.eval_relay)
            # clear(self.eval_viz)

        self.logout()

    def receive_data(self):  # blocking call
        while not self.has_terminated.value:
            try:
                print("[eval] get data from eval")
                success = self.gamestate.recv_and_update(self.conn)
                if not success:
                    print("connection with eval server closed")
                    break

                self.action_counter += 1
                print("action counter:", self.action_counter)
                self.eval_viz.put(
                    self.gamestate.get_data_plain_text(BOTH))

                # Clear all pending data in pipe
                print("Clearing eval queues")
                clear(self.eval_pred)
                clear(self.eval_relay)
                # clear(self.eval_viz)

                self.has_shield[P1].clear()
                self.has_shield[P2].clear()
                self.has_action[P1].clear()
                self.has_action[P2].clear()
                print("Cleared action")

            except Exception as e:
                print(e)

    def logout(self):
        try:
            self.has_terminated.value = True
            self.conn.shutdown(SHUT_RDWR)
            self.conn.close()
        except OSError:
            # connection already closed
            pass
        print("[Eval server]Connection closed")

    def process_glove(self):
        while not self.has_terminated.value:
            action, player = self.eval_pred.get()

            print("Glove action received:", action)

            if player == P1 and not self.has_action[P1].is_set():
                if action != 'shield':
                    self.gamestate.update_player(action, player)
                    self.eval_viz.put(
                        self.gamestate.get_data_plain_text(player))
                else:
                    self.has_shield[player].set()

                if action == 'grenade':
                    # wait for 2 seconds
                    is_hit = self.viz_eval_p1.get(timeout=5)
                    print(
                        f"Data received from Visualizer {is_hit}")
                    if is_hit:
                        self.gamestate.update_player(
                            "grenade_damage", P2)
                print(f"Player 1 action done : {action}")
                self.has_action[P1].set()

            if player == P2 and not self.has_action[P2].is_set():
                if action != 'shield':
                    self.gamestate.update_player(action, player)
                    self.eval_viz.put(
                        self.gamestate.get_data_plain_text(player))
                else:
                    self.has_shield[player].set()

                if action == 'grenade':
                    # uncomment on viz
                    is_hit = self.viz_eval_p2.get(timeout=5)
                    print(
                        f"Data received from Visualizer {is_hit}")
                    if is_hit:
                        self.gamestate.update_player(
                            "grenade_damage", P1)
                print(f"Player 2 action done : {action}")
                self.has_action[P2].set()

    def process_others(self):
        while not self.has_terminated.value:
            action, player = self.eval_relay.get()

            if action == "glove disconnect" or action == "gun disconnect" or action == "vest disconnect"\
                    or action == "glove connect" or action == "gun connect" or action == "vest connect":
                dummy_state = self.gamestate.get_data_plain_text(player)

                player_txt = "p1" if player == P1 else "p2"
                dummy_state[player_txt]["action"] = action
                self.eval_viz.put(dummy_state)

                print("Action received:", action, "for player", player+1)
                continue

            if player == P1 and not self.has_action[P1].is_set():
                self.gamestate.update_player(action, player)
                # first only action, state from eval
                self.eval_viz.put(
                    self.gamestate.get_data_plain_text(player))
                if action == "shoot":
                    # check for vest ir receiver
                    if self.has_incoming_bullet_p1.poll(timeout=5):
                        self.has_incoming_bullet_p1.get()
                        clear(self.has_incoming_bullet_p1)
                        self.gamestate.update_player(
                            "bullet_hit", P2)
                        print("Bullet hit for player 1")
                print(f"Player 1 action done : {action}")
                self.has_action[P1].set()

            if player == P2 and not self.has_action[P2].is_set():
                self.gamestate.update_player(action, player)
                # first only action, state from eval
                self.eval_viz.put(
                    self.gamestate.get_data_plain_text(player))
                if action == "shoot":
                    # check for vest ir receiver
                    if self.has_incoming_bullet_p2.poll(timeout=5):
                        self.has_incoming_bullet_p2.get()
                        clear(self.has_incoming_bullet_p2)
                        self.gamestate.update_player(
                            "bullet_hit", P1)
                        print("Bullet hit for player 2")
                print(f"Player 2 action done : {action}")
                self.has_action[P2].set()
