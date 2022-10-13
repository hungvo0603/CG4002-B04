from paho.mqtt import client as mqtt_client

mqtt_broker = "test.mosquitto.org"  # 'broker.emqx.io'  # Public broker
mqtt_port = 1883

MQTT_PUB = "cg4002/4/viz_u9620"
MQTT_SUB = "cg4002/4/u96_viz20"

class Mqtt(threading.Thread):
    # Connection to visualiser
    def __init__(self, topic):
        super().__init__()
        self.topic = topic
        # self.client_id = client_id
        self.client = None
        self.daemon = True
        self.connect_mqtt()

    def connect_mqtt(self):
        def on_connect(client, broker, port, rc):
            if rc != 0:
                print("Failed to connect, return code: ", rc)

        try:
            client_temp = mqtt_client.Client(clean_session=True)
            client_temp.on_connect = on_connect
            client_temp.connect(mqtt_broker, mqtt_port)
            print("[Mqtt] Connection established to ", self.topic)
            self.client = client_temp
        except:
            # print("[Mqtt] Retry connection of ", self.topic)
            self.connect_mqtt()

    def publish(self):
        global has_terminated
        while True:
            try:
                if not viz_send_buffer.empty():
                    state = viz_send_buffer.get()
                    message = json.dumps(state)
                    status = 1
                    while status:
                        result = self.client.publish(self.topic, message)
                        status = result[0]
                        if status:
                            print("[Mqtt Pub]Failed to send message, retrying")
                    # print("[Mqtt Pub]Published data: ", message)

                    # result = self.client.publish(self.topic, message)
                    # status = result[0]
                    # if status:
                    #     print("[Mqtt Pub]Failed to send message, retrying")
                    # else:
                    #     print("[Mqtt Pub]Published data: ", message)

            except (KeyboardInterrupt, socket.gaierror, ConnectionError):
                print("[Mqtt Pub]Keyboard Interrupt, terminating")
                has_terminated = True
                break

    def subscribe(self):
        def on_message(client, userdata, msg):
            viz_recv_buffer.put(msg.payload.decode())
            print("[Mqtt]Received data: ", msg.payload.decode())

        self.client.on_message = on_message
        self.client.subscribe(self.topic)

    def terminate(self):
        # dont need to unsubs because clean session is true
        self.client.disconnect()
        self.client.loop_stop()
