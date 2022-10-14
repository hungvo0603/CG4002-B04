import threading
import multiprocessing
import socket
from _socket import SHUT_RDWR
import time

from GameState import GameState

P1 = 0
P2 = 1


class EvalServer(multiprocessing.Process):
    # Client to eval_server
    def __init__(self, ip_addr, port_num, group_id, secret_key, eval_pred, eval_relay, eval_viz, has_terminated):
        super().__init__()  # init parent (Thread)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (ip_addr, port_num)
        self.group_id = group_id
        self.secret_key = secret_key
        # has received p1, p2 actions (need to change p2)
        self.has_action = [False, True]
        self.has_incoming_bullet = [False, False]
        self.gamestate = GameState(main=self)  # static
        self.has_terminated = has_terminated
        self.daemon = True
        self.cd_shield = False

        self.eval_pred = eval_pred
        self.eval_relay = eval_relay
        self.eval_viz = eval_viz
        # self.gamestate.init_players()

    def run(self):
        self.conn.connect(self.server_address)
        print("[Eval server] Connection established to:", self.server_address)
        print("[Eval server] Copy to eval: ", self.secret_key)

        send_thread = threading.Thread(target=self.process_msg)
        send_thread.start()

        self.receive_data()

    def receive_data(self):  # blocking call
        while not self.has_terminated.value:
            try:
                success = self.gamestate.recv_and_update(self.conn)
                if self.gamestate.player_1.get_dict()['action'] == 'logout' and self.gamestate.player_2.get_dict()['action'] == 'logout':
                    # spam logout to eveyone
                    # visual_pipe_client.send(
                    #     self.gamestate.get_data_plain_text('1'))
                    # pipe5.send('logout')
                    # server_pipe_client.send('logout')
                    # ultra96_pipe_client.send('logout')
                    self.logout()
                if not success:
                    print("connection with eval server closed")
                    break
                self.has_action[P1] = False
                self.has_action[P2] = True  # need to change
                self.eval_viz.send(
                    self.gamestate.get_data_plain_text(3))
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

    def failed_shot(player):
        global has_incoming_shoot
        has_incoming_shoot[player].pop()
        print("[Game engine] Shot to ", player, " has missed")

    def process_msg(self):
        while not self.has_terminated.value:
            if self.eval_pred.poll():
                action, player = self.eval_pred.recv()
                if player == P1 and not self.has_action[P1]:
                    self.has_action[P1] = True
                    self.gamestate.update_player(action, player)
                    self.eval_viz.send(
                        self.gamestate.get_data_plain_text(player))
                    print(f"Player 1 action done : {action}")
                    if action == 'grenade':
                        time.sleep(1.5)  # wait for viz reply
                        # need to change
                        # if self.eval_viz.poll():
                        #     player_hit = self.eval_viz.recv()  # need to change to include player, player_hit
                        #     print(
                        #         f"Data received from Visualizer {player_hit}")

                        self.gamestate.update_player(
                            "grenade_damage", P2)
                        self.eval_viz.send(
                            self.gamestate.get_data_plain_text(2))

                if player == P2 and not self.has_action[P2]:
                    self.has_action[P2] = True
                    self.gamestate.update_player(action, player)
                    self.eval_viz.send(
                        self.gamestate.get_data_plain_text(player))
                    print(f"Player 2 action done : {action}")
                    if action == 'grenade':
                        # time.sleep(1.5)  # wait for viz reply
                        # need to change
                        # if self.eval_viz.poll():
                        #     player_hit = self.eval_viz.recv()  # need to change to include player, player_hit
                        #     print(
                        #         f"Data received from Visualizer {player_hit}")

                        self.gamestate.update_player(
                            "grenade_damage", P1)
                        self.eval_viz.send(
                            self.gamestate.get_data_plain_text(3))

            if self.eval_relay.poll():
                action, player = self.eval_relay.recv()
                if player == P1 and not self.has_action[P1]:
                    self.has_action[P1] = True
                    self.gamestate.update_player(action, player)
                    self.eval_viz.send(
                        self.gamestate.get_data_plain_text(player))
                if action == "shoot":
                    # time.sleep(1.5)  # wait for vest
                    # Wait for vest to detect
                    # if self.eval_relay.poll():
                    #     action, player = self.eval_relay.recv()
                    self.gamestate.update_player(
                        "bullet_hit", P2)
                    self.eval_viz.send(
                        self.gamestate.get_data_plain_text(3))

                if player == P2 and not self.has_action[P2]:
                    self.has_action[P2] = True
                    self.gamestate.update_player(action, player)
                    self.eval_viz.send(
                        self.gamestate.get_data_plain_text(player))
                if action == "shoot":
                    # time.sleep(1.5)  # wait for vest
                    # Wait for vest to detect
                    # if self.eval_relay.poll():
                    #     action, player = self.eval_relay.recv()
                    self.gamestate.update_player(
                        "bullet_hit", P1)
                    self.eval_viz.send(
                        self.gamestate.get_data_plain_text(3))

            if self.cd_shield:
                print("Shield time over")
                self.cd_shield = False

            # Sends data to Eval Server if both players have done an action
            if self.has_action[0] and self.has_action[1]:
                self.has_action[0] = False
                self.has_action[1] = True  # need to change
                self.gamestate.send_encrypted(self.conn, self.secret_key)

        self.logout()
