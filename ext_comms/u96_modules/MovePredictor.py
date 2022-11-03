import numpy as np
import pynq.lib.dma
from pynq import allocate
from pynq import Overlay
import multiprocessing
from queue import Empty


def clear(pipe):
    try:
        print("Clearing pipe")
        while pipe.poll():
            pipe.recv()
    except Empty:
        print("Finish clearing pipe")
        pass


class MovePredictor(multiprocessing.Process):
    def __init__(self, pred_relay, pred_eval, has_terminated):
        super().__init__()  # init parent (Thread)
        self.daemon = True
        self.has_terminated = has_terminated

        self.overlay = Overlay('mlp.bit')
        self.dma_send = self.overlay.axi_dma_0
        self.dma_recv = self.overlay.axi_dma_0
        self.pred_relay = pred_relay
        self.pred_eval = pred_eval

        self.input_arr = [[], []]  # p1, p2
        self.input_buffer = [allocate(shape=(60,), dtype=np.float32), allocate(
            shape=(60,), dtype=np.float32)]
        self.output_buffer = [
            allocate(shape=(1,), dtype=np.int32), allocate(shape=(1,), dtype=np.int32)]
        self.action_count = {"grenade": 0, "shield": 0, "reload": 0}

    def pred_action(self, data, player):
        self.input_arr[player].extend(data)
        print("len of input arr: ", len(
            self.input_arr[player]), "from player: ", player+1)
        if len(self.input_arr[player]) < 60:
            return None

        actions = ["grenade", "shield", "reload", "nomovement"]

        for i in range(60):
            self.input_buffer[player][i] = float(self.input_arr[player][i])

        # print("Input buffer: ", self.input_buffer[player])
        print("Running prediction...")
        self.dma_send.sendchannel.transfer(self.input_buffer[player])
        self.dma_recv.recvchannel.transfer(self.output_buffer[player])
        self.dma_send.sendchannel.wait()
        self.dma_recv.recvchannel.wait()
        self.input_arr[player].clear()  # clear array after prediction
        # print("len of input arr: ", len(self.input_arr[player]))
        # print("Cleared pipe after buffer")
        # clear(self.pred_relay)

        return actions[self.output_buffer[player][0]]

    def run(self):
        while not self.has_terminated.value:
            try:
                self.action_count = {"grenade": 0, "shield": 0, "reload": 0}
                for i in range(0, 3):
                    action = None
                    while action is None:
                        data, player = self.pred_relay.recv()
                        # clear pipe content
                        print("[ML] Recived: ", len(data))
                        action = self.pred_action(data, player)

                    self.action_count[action] += 1
                    print("[MovePredictor] Predicted", i, "action: ",
                          action, " for player ", player+1)

                max_action = max(self.action_count,
                                 key=self.action_count.get)
                print("Max action: ", max_action)
                self.pred_eval.send((max_action, player))

            except KeyboardInterrupt:
                print("[MovePredictor]Keyboard Interrupt, terminating")
                self.has_terminated.value = True
                break
