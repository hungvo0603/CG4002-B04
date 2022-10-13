import numpy as np
import pynq.lib.dma
from pynq import allocate
from pynq import Overlay
import multiprocessing


class MovePredictor(multiprocessing.Process):
    def __init__(self, move_data_buffer_out, move_res_buffer_in):
        super().__init__()  # init parent (Thread)
        self.daemon = True
        self.has_terminated = False

        self.overlay = Overlay('mlp.bit')
        self.dma_send = self.overlay.axi_dma_0
        self.dma_recv = self.overlay.axi_dma_0
        self.move_data_buffer_out = move_data_buffer_out
        self.move_res_buffer_in = move_res_buffer_in

        self.input_arr = []
        self.input_buffer = allocate(shape=(60,), dtype=np.float32)
        self.output_buffer = allocate(shape=(1,), dtype=np.int32)

    def pred_action(self, data):
        self.input_arr.append(data)

        if len(self.input_arr) < 60:
            return None

        actions = ["grenade", "shield", "reload", "logout", "nomovement"]

        for i in range(60):
            self.input_buffer[i] = float(self.input_arr[i])

        self.dma_send.sendchannel.transfer(self.input_buffer)
        self.dma_recv.recvchannel.transfer(self.output_buffer)
        self.dma_send.sendchannel.wait()
        self.dma_recv.recvchannel.wait()
        self.input_arr = []  # clear array after prediction

        return actions[self.output_buffer[0]]

    # Machine learning model
    def run(self):
        action = ""
        while action != "logout" and not self.has_terminated:
            try:
                if self.move_data_buffer_out.poll():
                    data = self.move_data_buffer_out.recv()
                    action = self.pred_action(data)
                    if action is not None:
                        self.move_res_buffer_in.send(action)
            except KeyboardInterrupt:
                print("[MovePredictor]Keyboard Interrupt, terminating")
                self.has_terminated = True
                break
