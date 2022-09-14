using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;

namespace ConsoleApp1
{
    static class OutputBuffer
    {
        private static Object bufferLock = new Object();
        private static Queue<string> data = new Queue<string>();

        public static int getSize()
        {
            lock (bufferLock)
            {
                return data.Count;
            }
        }

        public static string output()
        {
            if (data == null || data.Count == 0) return null;

            lock (bufferLock)
            {
                return data.Dequeue();
            }
        }

        public static void input(string s)
        {
            lock (bufferLock)
            {
                data.Enqueue(s);
            }
        }
    }

    static class InputBuffer
    {
        private static Object bufferLock = new Object();
        private static Queue<string> data = new Queue<string>();

        public static int getSize()
        {
            lock (bufferLock)
            {
                return data.Count;
            }
        }

        public static string output()
        {
            if (getSize() == 0) return null;

            lock (bufferLock)
            {
                return data.Dequeue();
            }
        }

        public static void input(string s)
        {
            lock (bufferLock)
            {
                data.Enqueue(s);
            }
        }
    }


    public class App
    {
        MqttClient client;
        string clientId;
        string topic;
        string broker = "broker.emqx.io";

        public App(string atopic, string aclientId)
        {
            topic = atopic;
            clientId = aclientId;
            init_mqtt();
        }

        void init_mqtt()
        {
            client = new MqttClient(broker);
            // register a callback-function (we have to implement, see below) which is called by the library when a message was received
            client.MqttMsgPublishReceived += client_MqttMsgPublishReceived;

            client.Connect(clientId);
            Console.WriteLine("Connected to " + topic);
        }

        // this code runs when a message was received
        void client_MqttMsgPublishReceived(object sender, MqttMsgPublishEventArgs e)
        {
            string message = Encoding.UTF8.GetString(e.Message);
            InputBuffer.input(message);
            Console.WriteLine("[Sub] Received: " + message + " via " + topic);
            // if (message.Equals("logout")) close();
        }

        // this code runs when the main window closes (end of the app)
        public void close()
        {
            client.Disconnect();
        }


        // this code runs when the button "Subscribe" is clicked
        public void subscribe()
        {
            // subscribe to the topic with QoS 2
            client.Subscribe(new string[] { topic }, new byte[] { MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE });
            Console.WriteLine("[Sub] Subscribed to " + topic);
            // we need arrays as parameters because we can subscribe to different topics with one call
        }


        // this code runs when the button "Publish" is clicked
        public void publish()
        {
            while (true)
            {
                if (OutputBuffer.getSize() != 0)
                {
                    string message = OutputBuffer.output();
                    if (message.Equals("logout")) break; // do not re-publish after logout
                    // publish a message with QoS 2
                    client.Publish(topic, Encoding.UTF8.GetBytes(message), MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE, true);
                    Console.WriteLine("[Pub]Sent message: " + message + " via " + topic);
                }
            }
        }


    }

    internal class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Start Mqtt");
            App pub = new App("cg4002/4/u96_viz", "ghjk");

            Thread pub_thread = new Thread(pub.publish);
            pub_thread.Start();

            App sub = new App("cg4002/4/viz_u96", "trjk");
            sub.subscribe();

            // Visualiser
            while (true)
            {
                if (InputBuffer.getSize() != 0)
                {
                    string message = InputBuffer.output();

                    // Visualiser logic here
                    if (message.Equals("grenade"))
                    {
                        //Gen random grenade outcome
                        Random rnd = new Random();
                        int num = rnd.Next() % 2;
                        if (num == 0) OutputBuffer.input("False");
                        else OutputBuffer.input("True");
                    }
                    Console.WriteLine("[Viz]Received Message: " + message);
                    if (message.Equals("logout")) break;
                }
            }

            pub_thread.Abort();
            pub.close();
            sub.close();
        }

    }
}
