# Try:
# shield should be later than shoot
# 2 player: can either have shield first then damage or vice versa
# Todo:
# mass logout of process
# add bluetooth whole pipeline


# Main modules
from EvalServer import EvalServer
from MovePredictor import MovePredictor
from RelayLaptop import RelayLaptop
from Visualizer import Visualizer

import sys
from multiprocessing import Pipe, Value, Queue
import time

# Data buffer
pred_relay, relay_pred = Pipe()  # internal data, data
eval_pred, pred_eval = Pipe()  # data, action
has_incoming_bullet_p1_out, has_incoming_bullet_p1_in = Pipe()
has_incoming_bullet_p2_out, has_incoming_bullet_p2_in = Pipe()
eval_relay, relay_eval = Pipe()  # internal data, action
viz_eval_p1 = Queue()
viz_eval_p2 = Queue()
eval_viz = Queue()
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

    # Ultra96 Processes
    relay = RelayLaptop(group_id,
                        relay_pred, relay_eval, has_terminated, has_incoming_bullet_p1_in, has_incoming_bullet_p2_in)
    predictor = MovePredictor(pred_relay, pred_eval, has_terminated)
    eval = EvalServer(eval_ip, eval_port, group_id,
                      secret_key, eval_pred, eval_relay, eval_viz, viz_eval_p1, viz_eval_p2, has_terminated, has_incoming_bullet_p1_out, has_incoming_bullet_p2_out)
    visualizer = Visualizer(eval_viz, viz_eval_p1, viz_eval_p2, has_terminated)

    relay.start()
    predictor.start()
    eval.start()
    visualizer.start()

    relay.join()
    eval.join()
    predictor.join()
    visualizer.terminate()

    print("Program terminated, thanks for playing :D")
