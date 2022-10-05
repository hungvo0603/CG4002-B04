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

        [Header("Data")]
        public PlayerDataJson playerData = new PlayerDataJson();
        public PlayerStatsJson player1Data = new PlayerStatsJson();
        public PlayerStatsJson player2Data = new PlayerStatsJson();

        private List<string> eventMessages = new List<string>();
        private bool updateUI = false;

        public void TestPublish()
        {
            // edit GetBytes to send data
            // client.Publish("cg4002/4/u96_viz20", System.Text.Encoding.UTF8.GetBytes("p1"), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
            string sample_json_string = "{\"p1\": {\"hp\": 100, \"action\": \"reload\", \"bullets\": 6, \"grenades\": 2, \"shield_time\": 0, \"shield_health\": 0, \"num_deaths\": 0, \"num_shield\": 3}, \"p2\": {\"hp\": 100, \"action\": \"none\", \"bullets\": 6, \"grenades\": 2, \"shield_time\": 0, \"shield_health\": 0, \"num_deaths\": 0, \"num_shield\": 3}, \"sender\": \"eval\"}";
            client.Publish("cg4002/4/viz_u9620", System.Text.Encoding.UTF8.GetBytes(sample_json_string), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
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
            Debug.Log("Connecting to Ultra96.");
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
            client.Subscribe(new string[] { "cg4002/4/viz_u9620" }, new byte[] { MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE });
        }

        protected override void UnsubscribeTopics()
        {
            client.Unsubscribe(new string[] { "cg4002/4/viz_u9620" });
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
            Debug.Log("Received in DecodeMessage: " + msg);
            StoreMessage(msg);
        }

        private void StoreMessage(string eventMsg)
        {
            eventMessages.Add(eventMsg);
        }

        private void ProcessMessage(string msg)
        {
            playerData = PlayerDataJson.CreateDataFromJSON(msg);
            player1Data = playerData.p1;
            player2Data = playerData.p2;
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
