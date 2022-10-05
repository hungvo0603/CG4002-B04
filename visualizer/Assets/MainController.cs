/*
The MIT License (MIT)

Copyright (c) 2018 Giovanni Paolo Vigano'

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;
using M2MqttUnity;

/// <summary>
/// Examples for the M2MQTT library (https://github.com/eclipse/paho.mqtt.m2mqtt),
/// </summary>
namespace M2MQTT.MainController
{
    /// <summary>
    /// Script for testing M2MQTT with a Unity UI
    /// </summary>
    public class MainController : M2MqttUnityClient
    {
        [Header("User Interface")]
        public Image connectedIcon;
        public Image disconnectedIcon;
        public Button connectButton;
        public Button disconnectButton;
        public Button testPublishButton;

        private List<string> eventMessages = new List<string>();
        private bool updateUI = false;

        public void TestPublish()
        {
            client.Publish("M2MQTT_Unity/test", System.Text.Encoding.UTF8.GetBytes("Test message"), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
            Debug.Log("Test message published");
            // AddUiMessage("Test message published.");
        }

        // public void SetUiMessage(string msg)
        // {
        //     if (consoleInputField != null)
        //     {
        //         consoleInputField.text = msg;
        //         updateUI = true;
        //     }
        // }

        // public void AddUiMessage(string msg)
        // {
        //     if (consoleInputField != null)
        //     {
        //         consoleInputField.text += msg + "\n";
        //         updateUI = true;
        //     }
        // }

        protected override void OnConnecting()
        {
            base.OnConnecting();
            Debug.Log("Connecting to broker.");
            updateUI = true;
        }

        protected override void OnConnected()
        {
            base.OnConnected();
            connectedIcon.gameObject.SetActive(true);
            disconnectedIcon.gameObject.SetActive(false);
            updateUI = true;
        }

        protected override void SubscribeTopics()
        {
            client.Subscribe(new string[] { "M2MQTT_Unity/test" }, new byte[] { MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE });
        }

        protected override void UnsubscribeTopics()
        {
            client.Unsubscribe(new string[] { "M2MQTT_Unity/test" });
        }

        protected override void OnConnectionFailed(string errorMessage)
        {
            Debug.Log("CONNECTION FAILED!");
            updateUI = true;
        }

        protected override void OnDisconnected()
        {
            Debug.Log("DISCONNECTED");
            connectedIcon.gameObject.SetActive(false);
            disconnectedIcon.gameObject.SetActive(true);
            updateUI = true;
        }

        protected override void OnConnectionLost()
        {
            Debug.Log("CONNECTION LOST");
            updateUI = true;
        }

        private void UpdateUI()
        {
            if (client == null)
            {
                if (connectButton != null)
                {
                    connectButton.interactable = true;
                    disconnectButton.interactable = false;
                    testPublishButton.interactable = false;
                }
            }
            else
            {
                if (testPublishButton != null)
                {
                    testPublishButton.interactable = client.IsConnected;
                }
                if (disconnectButton != null)
                {
                    disconnectButton.interactable = client.IsConnected;
                }
                if (connectButton != null)
                {
                    connectButton.interactable = !client.IsConnected;
                }
            }
            updateUI = false;
        }

        protected override void Start()
        {
            connectedIcon.gameObject.SetActive(false);
            disconnectedIcon.gameObject.SetActive(true);
            // SetUiMessage("Ready.");
            updateUI = true;
            base.Start();
        }

        protected override void DecodeMessage(string topic, byte[] message)
        {
            string msg = System.Text.Encoding.UTF8.GetString(message);
            Debug.Log("Received: " + msg);
            StoreMessage(msg);
            // if (topic == "M2MQTT_Unity/test")
            // {
            //     if (autoTest)
            //     {
            //         autoTest = false;
            //         Disconnect();
            //     }
            // }
        }

        private void StoreMessage(string eventMsg)
        {
            eventMessages.Add(eventMsg);
        }

        private void ProcessMessage(string msg)
        {
            Debug.Log("Received: " + msg);
            updateUI = true;
        }

        protected override void Update()
        {
            base.Update(); // call ProcessMqttEvents()

            if (eventMessages.Count > 0)
            {
                foreach (string msg in eventMessages)
                {
                    ProcessMessage(msg);
                }
                eventMessages.Clear();
            }
            if (updateUI)
            {
                UpdateUI();
            }
        }

        private void OnDestroy()
        {
            Disconnect();
        }
    }
}
