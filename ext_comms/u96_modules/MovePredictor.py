import numpy as np
import pynq.lib.dma
from pynq import allocate
from pynq import Overlay
import multiprocessing
import threading
from queue import Queue, Empty
import csv

CONNECT = 0


def clear(q):
    try:
        while not q.empty():
            q.get_nowait()
    except (Empty, EOFError):
        pass
    except Exception as e:
        print("Clearing queue error:", e)


class MovePredictor(multiprocessing.Process):
    def __init__(self, pred_relay_p1, pred_relay_p2, eval_pred, has_terminated):
        super().__init__()
        self.ml_queue = Queue()
        self.ml = MLPred(self.ml_queue, eval_pred, has_terminated)
        self.receive_p1 = pred_relay_p1
        self.receive_p2 = pred_relay_p2
        self.daemon = True
        self.has_terminated = has_terminated

    def run(self):
        player1_recv = threading.Thread(
            target=self.receive_data, args=(self.receive_p1,))
        player2_recv = threading.Thread(
            target=self.receive_data, args=(self.receive_p2,))

        player1_recv.start()
        player2_recv.start()

        self.ml.run()  # ml run on main thread

        player1_recv.join()
        player2_recv.join()

    def receive_data(self, player_queue):
        while not self.has_terminated.value:
            try:
                data = player_queue.get()
                self.ml_queue.put(data)
            except Exception as e:
                print("Error in receive_data:", e)


class MLPred():
    def __init__(self, relay_queue, eval_pred, has_terminated):
        super().__init__()  # init parent (Thread)
        self.daemon = True
        self.has_terminated = has_terminated

        self.overlay = Overlay('mlp.bit')
        self.dma_send = self.overlay.axi_dma_0
        self.dma_recv = self.overlay.axi_dma_0
        self.relay_queue = relay_queue
        self.eval_pred = eval_pred

        self.input_arr = [[], []]  # p1, p2
        self.input_buffer = [allocate(shape=(60,), dtype=np.float32), allocate(
            shape=(60,), dtype=np.float32)]
        self.output_buffer = [
            allocate(shape=(1,), dtype=np.int32), allocate(shape=(1,), dtype=np.int32)]

    def pred_action(self, data, player):
        self.input_arr[player].extend(data)
        print("len of input arr: ", len(self.input_arr[player]))
        if len(self.input_arr[player]) < 60:
            return None

        # put ml data to csv
        filename = 'p' + str(player+1) + '_data.csv'
        with open(filename, 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.input_arr[player])

        actions = ["grenade", "shield", "reload", "nomovement"]

        for i in range(60):
            self.input_buffer[player][i] = float(self.input_arr[player][i])

        # print("Input buffer: ", self.input_buffer[player])
        print("Running prediction...")
        self.dma_send.sendchannel.transfer(self.input_buffer[player])
        self.dma_recv.recvchannel.transfer(self.output_buffer[player])
        self.dma_send.sendchannel.wait()
        self.dma_recv.recvchannel.wait()
        clear(self.relay_queue)
        self.input_arr[player].clear()  # clear array after prediction
        print("len of input arr after clear: ", len(self.input_arr[player]))
        # print("Cleared pipe after buffer")

        return actions[self.output_buffer[player][0]]

    def run(self):
        while not self.has_terminated.value:
            try:
                data, player = self.relay_queue.get()

                # on connect/reconnect, we clear all the input array for the player
                if data == CONNECT:
                    self.input_arr[player] = []
                    continue

                # clear pipe content
                print("[ML] Recived: ", len(data))
                action = self.pred_action(data, player)

                if action is not None:
                    print("[MovePredictor] Predicted action: ",
                          action, " for Player ", player+1)

                if action is not None and action != "nomovement":
                    self.eval_pred.put((action, player))

            except KeyboardInterrupt:
                print("[MovePredictor]Keyboard Interrupt, terminating")
                self.has_terminated.value = True
                break
            except Exception as e:
                print("[MovePredictor]Encountered error: ", e)
