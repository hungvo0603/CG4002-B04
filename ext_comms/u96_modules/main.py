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

# Main modules
import EvalServer
import MovePredictor
import RelayLaptop
# import GameEngine
import Visualizer


import threading
import socket

import sys
from multiprocessing import Pipe


class Ultra96():
    def __init__(self, local_port, group_id, eval_port, eval_ip, secret_key):

        # Data buffer
        move_res_buffer_in, move_res_buffer_out = Pipe()  # predicted action
        move_data_buffer_in, move_data_buffer_out = Pipe()
        eval_buffer_in, eval_buffer_out = Pipe()
        viz_send_buffer_in, viz_send_buffer_out = Pipe()
        viz_recv_buffer_in, viz_recv_buffer_out = Pipe()  # bool value for grenade hit

        # Ultra96 Processes
        self.relay = RelayLaptop(local_port, group_id,
                                 move_data_buffer_in, move_res_buffer_in)
        self.eval = EvalServer(eval_ip, eval_port, group_id, secret_key)
        self.visualizer = Visualizer()
        self.predictor = MovePredictor(
            move_data_buffer_out, move_res_buffer_in)
        # self.game_engine = GameEngine()
        self.is_logout = False

    def start_processes(self):
        self.relay.start()
        self.eval.start()
        self.visualizer.start()
        self.predictor.start()
        # self.game_engine.start()

    def terminate_processes(self):
        self.relay.terminate()
        self.eval.terminate()
        self.visualizer.terminate()
        self.predictor.terminate()
        # self.game_engine.terminate()

    # Starts the program and creates relevant threads
    def start(self):
        self.start_processes()
        while not self.is_logout:
            try:
                if conn10.poll():
                    if conn10.recv() == 'logout':
                        self.is_logout = True
                        self.logout(ml_process)
            except KeyboardInterrupt:
                self.stop()


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Invalid number of arguments')
        sys.exit()

    local_port = int(sys.argv[1])
    group_id = int(sys.argv[2])
    eval_port = int(sys.argv[3])
    eval_ip = sys.argv[4]
    secret_key = sys.argv[5]

    ultra96 = Ultra96(local_port, group_id, eval_port, eval_ip, secret_key)
    ultra96.start()

    print("Program terminated, thanks for playing :D")
