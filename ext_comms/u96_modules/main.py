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
from EvalServer import EvalServer
from MovePredictor import MovePredictor
from RelayLaptop import RelayLaptop
from Visualizer import Visualizer

import sys
from multiprocessing import Pipe, Value
import time

# Data buffer
relay_pred, pred_relay = Pipe(duplex=True)  # internal data, data
pred_eval, eval_pred = Pipe(duplex=True)  # data, action
relay_eval, eval_relay = Pipe(duplex=True)  # internal data, action
# eval_in = Queue()  # action
viz_eval, eval_viz = Pipe(duplex=True)  # player_hit, state
# viz_recv_buffer_in, viz_recv_buffer_out = Pipe()  # bool value for grenade hit
has_terminated = Value('i', False)


# class Ultra96():


# def start_processes(self):
#     self.relay.start()
#     self.predictor.start()
#     self.eval.start()
#     self.visualizer.start()


# def terminate_processes(self):
#     self.relay.terminate()
#     self.eval.terminate()
#     self.visualizer.terminate()
#     self.predictor.terminate()


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Invalid number of arguments')
        sys.exit()

    local_port = int(sys.argv[1])
    group_id = int(sys.argv[2])
    eval_port = int(sys.argv[3])
    eval_ip = sys.argv[4]
    secret_key = sys.argv[5]

    # ultra96 = Ultra96(local_port, group_id, eval_port,
    #                   eval_ip, secret_key, has_terminated)
    # ultra96.start_processes()

    # Ultra96 Processes
    relay = RelayLaptop(local_port, group_id,
                        relay_pred, relay_eval, has_terminated)
    predictor = MovePredictor(
        pred_relay, pred_eval, has_terminated)
    eval = EvalServer(eval_ip, eval_port, group_id,
                      secret_key, eval_pred, eval_relay, eval_viz, has_terminated)
    visualizer = Visualizer(viz_eval, has_terminated)

    relay.start()
    predictor.start()
    eval.start()
    visualizer.start()

    relay.join()
    eval.join()
    visualizer.join()
    predictor.join()

    print("Program terminated, thanks for playing :D")
