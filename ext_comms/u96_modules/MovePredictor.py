import numpy as np
import pynq.lib.dma
from pynq import allocate
from pynq import Overlay
import multiprocessing


class MovePredictor(multiprocessing.Process):
    def __init__(self, pred_relay, pred_eval, has_terminated, pred_eval_event):
        super().__init__()  # init parent (Thread)
        self.daemon = True
        self.has_terminated = has_terminated

        self.overlay = Overlay('mlp.bit')
        self.dma_send = self.overlay.axi_dma_0
        self.dma_recv = self.overlay.axi_dma_0
        self.pred_relay = pred_relay
        self.pred_eval = pred_eval
        self.pred_eval_event = pred_eval_event

        self.input_arr = [[], []]  # p1, p2
        self.input_buffer = [allocate(shape=(60,), dtype=np.float32), allocate(
            shape=(60,), dtype=np.float32)]
        self.output_buffer = [
            allocate(shape=(1,), dtype=np.int32), allocate(shape=(1,), dtype=np.int32)]

    def pred_action(self, data, player):
        self.input_arr[player].extend(data)

        if len(self.input_arr[player]) < 60:
            return None

        actions = ["grenade", "shield", "reload", "logout", "nomovement"]

        for i in range(60):
            self.input_buffer[player][i] = float(self.input_arr[player][i])

        # print("Input buffer: ", self.input_buffer[player])
        print("Running prediction...")
        self.dma_send.sendchannel.transfer(self.input_buffer[player])
        self.dma_recv.recvchannel.transfer(self.output_buffer[player])
        self.dma_send.sendchannel.wait()
        self.dma_recv.recvchannel.wait()
        self.input_arr[player] = []  # clear array after prediction

        return actions[self.output_buffer[player][0]]

    def run(self):
        while not self.has_terminated.value:
            try:
                data, player = self.pred_relay.recv()
                action = self.pred_action(data, player)
                if action is not None and action != "nomovement":
                    print("[MovePredictor] Predicted action: ", action)
                    self.pred_eval.send((action, player))
                    self.pred_eval_event.set()
            except KeyboardInterrupt:
                print("[MovePredictor]Keyboard Interrupt, terminating")
                self.has_terminated.value = True
                break
