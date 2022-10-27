# Process:
# - ml model, comm visualiser, comm eval, comm relay
# To try:


# Todo:
# blocking process on last few movements -> can try to move viz to main process + thread
# 2 player: can either have shield first then damage or vice versa
# continue action after the broken pipe nonetype error or the mqqt temp name resolution error too
# try out hivemq

# Main modules
from EvalServer import EvalServer
from MovePredictor import MovePredictor
from RelayLaptop import RelayLaptop
from Visualizer import Visualizer

import sys
from multiprocessing import Pipe, Value, Event
import time

# Data buffer
pred_relay, relay_pred = Pipe()  # internal data, data
eval_pred, pred_eval = Pipe()  # data, action
has_incoming_bullet_p1_out, has_incoming_bullet_p1_in = Pipe()
has_incoming_bullet_p2_out, has_incoming_bullet_p2_in = Pipe()
eval_relay, relay_eval = Pipe()  # internal data, action
viz_eval, eval_viz = Pipe(duplex=True)  # player_hit, state
has_terminated = Value('i', False)

# Events
# relay_pred_event = Event()
# pred_eval_event = Event()
# relay_eval_event = Event()
# eval_viz_event = Event()
# viz_eval_event = Event()


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Invalid number of arguments')
        sys.exit()

    group_id = int(sys.argv[1])
    eval_port = int(sys.argv[2])
    eval_ip = sys.argv[3]
    secret_key = sys.argv[4]

    # ultra96 = Ultra96(local_port, group_id, eval_port,
    #                   eval_ip, secret_key, has_terminated)
    # ultra96.start_processes()

    # Ultra96 Processes
    relay = RelayLaptop(group_id,
                        relay_pred, relay_eval, has_terminated, has_incoming_bullet_p1_in, has_incoming_bullet_p2_in)
    predictor = MovePredictor(pred_relay, pred_eval, has_terminated)
    eval = EvalServer(eval_ip, eval_port, group_id,
                      secret_key, eval_pred, eval_relay, eval_viz, has_terminated, has_incoming_bullet_p1_out, has_incoming_bullet_p2_out)
    visualizer = Visualizer(viz_eval, has_terminated)

    relay.start()
    predictor.start()
    eval.start()
    visualizer.start()

    relay.join()
    eval.join()
    predictor.join()
    visualizer.terminate()

    print("Program terminated, thanks for playing :D")
