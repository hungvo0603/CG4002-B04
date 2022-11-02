import json
# import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
from PlayerState import PlayerStateStudent
from PlayerState import PlayerStateBase

P1 = 0
P2 = 1


class GameState:
    """
    class for sending and receiving the game state json object
    """

    def __init__(self, main):
        self.main = main
        self.player_1 = PlayerStateStudent(self.main)
        self.player_2 = PlayerStateStudent(self.main)

    def _get_data_plain_text(self):
        data = {'p1': self.player_1.get_dict(), 'p2': self.player_2.get_dict()}
        return json.dumps(data)

    def get_data_plain_text(self, player):
        player = int(player)
        data = dict()
        if player == 0:
            temp = self.player_2.action
            self.player_2.update_actl('none')
            data = {
                'p1': self.player_1.get_dict(),
                'p2': self.player_2.get_dict()
            }
            self.player_2.action = temp
        elif player == 1:
            temp = self.player_1.action
            self.player_1.update_actl('none')
            data = {
                'p1': self.player_1.get_dict(),
                'p2': self.player_2.get_dict()
            }
            self.player_1.action = temp
        elif player == 2:
            prev_action_1 = self.player_1.action
            prev_action_2 = self.player_2.action
            self.player_1.update_actl('none')
            self.player_2.update_actl('none')
            data = {
                'p1': self.player_1.get_dict(),
                'p2': self.player_2.get_dict()
            }
            self.player_1.action = prev_action_1
            self.player_2.action = prev_action_2
        elif player == 3:
            data = {
                'p1': self.player_1.get_dict(),
                'p2': self.player_2.get_dict()
            }
        return data

    # encrypt and send the game state json to remote host

    def send_encrypted(self, remote_socket, secret_key_string):
        success = True
        plaintext = self._get_data_plain_text()

        # print(plaintext)

        print(
            f"Sending message to server: {plaintext} (Unencrypted)")
        plaintext_bytes = pad(plaintext.encode("utf-8"), 16)

        secret_key_bytes = secret_key_string.encode("utf-8")
        cipher = AES.new(secret_key_bytes, AES.MODE_CBC)
        iv_bytes = cipher.iv

        ciphertext_bytes = cipher.encrypt(plaintext_bytes)
        message = base64.b64encode(iv_bytes + ciphertext_bytes)

        # send len followed by '_' followed by cypher

        m = str(len(message))+'_'
        try:
           # print("trying to send")
            remote_socket.sendall(m.encode("utf-8"))
            remote_socket.sendall(message)
           # print("send to eval server")
        except OSError:
            print("Connection terminated")
            success = False
        return success

    # send the game state json to remote host
    def send_plaintext(self, remote_socket):
        success = True
        plaintext = self._get_data_plain_text()

        # send len followed by '_' followed by cypher
        m = str(len(plaintext))+'_'
        try:
            remote_socket.sendall(m.encode("utf-8"))
            remote_socket.sendall(plaintext.encode("utf-8"))
        except OSError:
            print("Connection terminated")
            success = False
        return success

    # recv the game state json from remote host and update the object
    def recv_and_update(self, remote_socket):
        success = False
        while True:
            # recv length followed by '_' followed by cypher
            data = b''
            while not data.endswith(b'_'):
                _d = remote_socket.recv(1)
                if not _d:
                    data = b''
                    break
                data += _d
            if len(data) == 0:
                print('no more data from', remote_socket)
                break

            data = data.decode("utf-8")
            #print(f"data from gamestate: {data}")
            length = int(data[:-1])

            data = b''
            while len(data) < length:
                _d = remote_socket.recv(length - len(data))
                if not _d:
                    data = b''
                    break
                data += _d
            if len(data) == 0:
                print('no more data from', remote_socket)
                break
            msg = data.decode("utf8")  # Decode raw bytes to UTF-8

            game_state_received = json.loads(msg)

            self.player_1.initialize_from_dict(game_state_received['p1'])
            self.player_2.initialize_from_dict(game_state_received['p2'])

            success = True
            break
        return success

    def init_player(self, player_id, action, hp, bullets_remaining, grenades_remaining,
                    shield_time_remaining, shield_health, num_unused_shield, num_deaths):
        if player_id == 0:
            player = self.player_1
        else:
            player = self.player_2
        player.initialize(action, bullets_remaining, grenades_remaining, hp,
                          num_deaths, num_unused_shield,
                          shield_health, shield_time_remaining)

    def init_players(self, player_1: PlayerStateBase, player_2: PlayerStateBase):
        self.player_1.initialize_from_player_state(player_1)
        self.player_2.initialize_from_player_state(player_2)

    def update_player(self, new_data, player):
        player = int(player)
        if player == P1:
            return self.player_1.update_actl(new_data)
        elif player == P2:
            return self.player_2.update_actl(new_data)
        else:
            self.player_1.update_actl(new_data)
            self.player_2.update_actl(new_data)

    def check_player(self, player):
        if player == P1:
            return self.player_1.get_dict()
        elif player == P2:
            return self.player_2.get_dict()
