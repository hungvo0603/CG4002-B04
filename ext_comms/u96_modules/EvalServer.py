import threading
import multiprocessing
import socket
from _socket import SHUT_RDWR

from GameState import GameState

P1 = 0
P2 = 1
BOTH = 2


class EvalServer(multiprocessing.Process):
    # Client to eval_server
    def __init__(self, ip_addr, port_num, group_id, secret_key, eval_pred, eval_relay, eval_viz, has_terminated, pred_eval_event, relay_eval_event, has_incoming_bullet_p1_out):
        super().__init__()  # init parent (Thread)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (ip_addr, port_num)
        self.group_id = group_id
        self.secret_key = secret_key
        # has received p1, p2 actions (need to change p2)
        self.has_action = [threading.Event(), threading.Event()]
        self.has_incoming_bullet_p1_out = has_incoming_bullet_p1_out

        self.gamestate = GameState(main=self)  # static
        self.has_terminated = has_terminated
        self.daemon = True
        # self.cd_shield = False
        # self.pred_eval_event = pred_eval_event
        # self.relay_eval_event = relay_eval_event

        self.eval_pred = eval_pred
        self.eval_relay = eval_relay
        self.eval_viz = eval_viz

    def run(self):
        self.conn.connect(self.server_address)
        print("[Eval server] Connection established to:", self.server_address)

        recv_thread = threading.Thread(target=self.receive_data)
        recv_thread.start()

        glove_thread = threading.Thread(target=self.process_glove)
        glove_thread.start()

        gun_thread = threading.Thread(target=self.process_gun)
        gun_thread.start()

        while not self.has_terminated.value:
            # Process if both players have done an action
            self.has_action[P1].wait()
            # self.has_action[P2].wait()

            # if self.cd_shield:
            #     print("Shield time over")
            #     self.cd_shield = False

            self.has_action[P1].clear()
            # self.has_action[P2].clear()
            print("Sending to eval...")
            self.gamestate.send_encrypted(self.conn, self.secret_key)

        self.logout()

    def receive_data(self):  # blocking call
        while not self.has_terminated.value:
            try:
                success = self.gamestate.recv_and_update(self.conn)
                # if self.gamestate.player_1.get_dict()['action'] == 'logout' and self.gamestate.player_2.get_dict()['action'] == 'logout':
                # spam logout to eveyone
                # visual_pipe_client.send(
                #     self.gamestate.get_data_plain_text('1'))
                # pipe5.send('logout')
                # server_pipe_client.send('logout')
                # ultra96_pipe_client.send('logout')
                # self.logout()
                if not success:
                    print("connection with eval server closed")
                    break
                # self.has_action[P1].clear()
                # self.has_action[P2].clear()  # need to change
                self.eval_viz.send(
                    self.gamestate.get_data_plain_text(BOTH))
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
            # self.pred_eval_event.wait()
            # print("Glove event received")
            action, player = self.eval_pred.recv()
            # self.pred_eval_event.clear()
            if player == P1 and not self.has_action[P1].is_set():
                # self.has_action[P1] = True
                self.gamestate.update_player(action, player)
                self.eval_viz.send(
                    self.gamestate.get_data_plain_text(player))

                if action == 'grenade':
                    # time.sleep(1.5)  # wait for viz reply
                    # need to change
                    # player_hit = self.eval_viz.recv()  # need to change to include player, player_hit
                    # print(
                    #     f"Data received from Visualizer {player_hit}")
                    # if player_hit != "none":
                    self.gamestate.update_player(
                        "grenade_damage", P2)
                    # self.eval_viz.send(
                    #     self.gamestate.get_data_plain_text(2))
                print(f"Player 1 action done : {action}")
                self.has_action[P1].set()

            # if player == P2 and not self.has_action[P2].is_set():
            #     # self.has_action[P2] = True
            #     self.gamestate.update_player(action, player)
            #     self.eval_viz.send(
            #         self.gamestate.get_data_plain_text(player))
            #     print(f"Player 2 action done : {action}")
            #     if action == 'grenade':
            #         # time.sleep(1.5)  # wait for viz reply
            #         # need to change
            #         if self.eval_viz.poll():
            #             player_hit = self.eval_viz.recv()  # need to change to include player, player_hit
            #             print(
            #                 f"Data received from Visualizer {player_hit}")
            #         if player_hit != "none":
            #             self.gamestate.update_player(
            #                 "grenade_damage", P1)
            #             # self.eval_viz.send(
            #             #     self.gamestate.get_data_plain_text(3))
            #     self.has_action[P2].set()

    def process_gun(self):
        while not self.has_terminated.value:
            # self.relay_eval_event.wait()
            action, player = self.eval_relay.recv()
            # self.relay_eval_event.clear()
            if player == P1 and not self.has_action[P1].is_set():
                # self.has_action[P1] = True
                self.gamestate.update_player(action, player)
                # first only action, state from eval
                self.eval_viz.send(
                    self.gamestate.get_data_plain_text(player))
                if action == "shoot":
                    # check for vest ir receiver
                    if self.has_incoming_bullet_p1_out.poll(timeout=1.5):
                        self.has_incoming_bullet_p1_out.recv()
                        self.gamestate.update_player(
                            "bullet_hit", P2)
                        # self.eval_viz.send(
                        #     self.gamestate.get_data_plain_text(player))
                        # self.has_incoming_bullet[P2].clear()
                print(f"Player 1 action done : {action}")
                self.has_action[P1].set()

            # if player == P2 and not self.has_action[P2].is_set():
            #     # self.has_action[P2] = True
            #     self.gamestate.update_player(action, player)
            #     self.eval_viz.send(
            #         self.gamestate.get_data_plain_text(player))
            #     if action == "shoot":
            #         # check for vest ir receiver
            #         if self.has_incoming_bullet[P1].wait(timeout=1.5):
            #             self.gamestate.update_player(
            #                 "bullet_hit", P1)
            #             self.eval_viz.send(
            #                 self.gamestate.get_data_plain_text(2))
            #             self.has_incoming_bullet[P1].clear()

            #     self.has_action[P2].set()
