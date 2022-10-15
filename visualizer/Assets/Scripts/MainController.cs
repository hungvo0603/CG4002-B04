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
        [Header("Connection UI")]
        public Image connectedIcon;
        public Image disconnectedIcon;
        public Button PublishMessageButton;

        [Header("Healthbar UI")]
        public HealthBarController healthBarPlayer1;
        public HealthBarController healthBarPlayer2;

        [Header("Bullet UI")]
        public ShootController shootController;
        public GunController gunController;

        [Header("Grenade UI")]
        public GrenadeController grenadeController;
        public GrenadeTriggerAnimation grenadeTriggerAnimation;
        public EnemyGrenadeTriggerAnimation enemyGrenadeTriggerAnimation;

        [Header("Shield UI")]
        public ShieldHealthController shieldHealthController;
        public ShieldController shieldController;
        public ShieldCountdown shieldCountdown;

        [Header("KDA UI")]
        public Player player;

        [Header("Enemy Detector")]
        public EnemyDetector enemyDetector;

        [Header("Data")]
        public PlayerDataJson playerData = new PlayerDataJson();
        public PlayerStatsJson player1Data = new PlayerStatsJson();
        public PlayerStatsJson player2Data = new PlayerStatsJson();
        // public GrenadeHitJson grenadeHitData = new GrenadeHitJson();

        [Header("Scene Changer")]
        public SceneChanger sceneChanger;

        private List<string> eventMessages = new List<string>();
        private bool updateUI = false;

        // Receiver: cg4002/4/u96_viz20
        public void PublishMessage(string msg)
        {
            // client.Publish("cg4002/4/u96_viz20", System.Text.Encoding.UTF8.GetBytes("p1"), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
            
            // Sending feedback message
            // Adi should parse the feedback, being "p1", "p2" or "none"
            
            // FEEDBACK TO EXT_COMM
            
            if (!String.IsNullOrEmpty(msg))
            {
                client.Publish("cg4002/4/u96_viz", System.Text.Encoding.UTF8.GetBytes(msg), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
                Debug.Log(msg);
                Debug.Log("Feedback message published");
            }
            else {
            // TESTING FOR VISUALIZER
            // string sample_json_string = "{\"p1\": {\"hp\": 100, \"action\": \"shoot\", \"bullets\": 5, \"grenades\": 1, \"shield_time\": 10, \"shield_health\": 30, \"num_deaths\": 2, \"num_shield\": 3}, \"p2\": {\"hp\": 60, \"action\": \"none\", \"bullets\": 6, \"grenades\": 2, \"shield_time\": 10, \"shield_health\": 30, \"num_deaths\": 3, \"num_shield\": 3}}";
            // string sample_json_string = "{\"p1\": {\"hp\": 100, \"action\": \"shield\", \"bullets\": 5, \"grenades\": 2, \"shield_time\": 10, \"shield_health\": 30, \"num_deaths\": 0, \"num_shield\": 3}, \"p2\": {\"hp\": 100, \"action\": \"none\", \"bullets\": 6, \"grenades\": 2, \"shield_time\": 10, \"shield_health\": 30, \"num_deaths\": 0, \"num_shield\": 3}}";
            string sample_json_string = "{\"p1\": {\"hp\": 100, \"action\": \"reload\", \"bullets\": 6, \"grenades\": 1, \"shield_time\": 10, \"shield_health\": 30, \"num_deaths\": 0, \"num_shield\": 2}, \"p2\": {\"hp\": 60, \"action\": \"none\", \"bullets\": 6, \"grenades\": 2, \"shield_time\": 10, \"shield_health\": 30, \"num_deaths\": 0, \"num_shield\": 3}}";
            // string sample_json_string = "{\"p1\": {\"hp\": 100, \"action\": \"grenade\", \"bullets\": 6, \"grenades\": 1, \"shield_time\": 10, \"shield_health\": 30, \"num_deaths\": 0, \"num_shield\": 2}, \"p2\": {\"hp\": 60, \"action\": \"none\", \"bullets\": 6, \"grenades\": 2, \"shield_time\": 10, \"shield_health\": 30, \"num_deaths\": 0, \"num_shield\": 3}}";
            // string sample_json_string = "{\"p1\": {\"hp\": 100, \"action\": \"logout\", \"bullets\": 5, \"grenades\": 1, \"shield_time\": 10, \"shield_health\": 30, \"num_deaths\": 2, \"num_shield\": 3}, \"p2\": {\"hp\": 60, \"action\": \"none\", \"bullets\": 6, \"grenades\": 2, \"shield_time\": 10, \"shield_health\": 30, \"num_deaths\": 3, \"num_shield\": 3}}";

            client.Publish("cg4002/4/viz_u96", System.Text.Encoding.UTF8.GetBytes(sample_json_string), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
            Debug.Log("Test message published");
            }
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
            
            // For testing Reload only
            // shootController.SetBullet(3, 4);
        }

        protected override void SubscribeTopics()
        {
            client.Subscribe(new string[] { "cg4002/4/viz_u96" }, new byte[] { MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE });
        }

        protected override void UnsubscribeTopics()
        {
            client.Unsubscribe(new string[] { "cg4002/4/viz_u96" });
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
                PublishMessageButton.interactable = false;
            }
            else
            {
                if (PublishMessageButton != null)
                {
                    PublishMessageButton.interactable = client.IsConnected;
                }
            }
            updateUI = false;
        }

        protected override void Start()
        {
            connectedIcon.gameObject.SetActive(false);
            disconnectedIcon.gameObject.SetActive(true);
            Connect();
            // SetUiMessage("Ready.");
            updateUI = true;
            base.Start();
        }

        protected override void DecodeMessage(string topic, byte[] message)
        {
            string msg = System.Text.Encoding.UTF8.GetString(message);
            Debug.Log("Received: " + msg);
            StoreMessage(msg);
        }

        private void StoreMessage(string eventMsg)
        {
            eventMessages.Add(eventMsg);
        }

        /** Player data
        //  hp --
        //  action
        //  bullets --
        //  grenades --
        //  shield_time 
        //  shield_health --
        //  num_deaths --
        //  num_shields --
        */
        private void ProcessMessage(string msg)
        {
            // string[] specialMessage = new string[] {"p1", "p2", "none"};
            // if (msg in specialMessage)
            // {
            //     grenadeHitData = GrenadeHitJson.CreateHitDataFromJSON(msg);
            // }
            // else
            // {
            if (msg == "p1" || msg == "p2" || msg == "none")
            {
                Debug.Log("Feedback received");
            }
            else
            {
                playerData = PlayerDataJson.CreateDataFromJSON(msg);
                player1Data = playerData.p1;
                player2Data = playerData.p2;
                updateUI = true;
                ProcessAction(player1Data.action, player2Data.action);
                ProcessHealthBarUpdate(player1Data.hp, player2Data.hp);
                ProcessBulletUpdate(player1Data.bullets, player2Data.bullets);
                ProcessKDAUpdate(player2Data.num_deaths, player1Data.num_deaths);
                ProcessShieldCounterUpdate(player1Data.num_shield, player2Data.num_shield);
                ProcessShieldHealthUpdate(player1Data.shield_health, player2Data.shield_health);
                ProcessGrenadeUpdate(player1Data.grenades, player2Data.grenades);
                ProcessShieldTimeUpdate(player1Data.shield_time, player2Data.shield_time);
            }

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

        private void ProcessHealthBarUpdate(int healthP1, int healthP2)
        {
            healthBarPlayer1.SetHealth(healthP1);
            healthBarPlayer2.SetHealth(healthP2);
        }

        private void ProcessBulletUpdate(int bulletP1, int bulletP2)
        {
            shootController.SetBullet(bulletP1, bulletP2);
        }

        private void ProcessKDAUpdate(int killP1, int killP2)
        {
            player.SetKillStatistics(killP1, killP2);
        }

        private void ProcessShieldCounterUpdate(int shieldP1, int shieldP2)
        {
            shieldController.SetShieldCount(shieldP1, shieldP2);
        }

        // This won't have effect if the shield is not activated
        private void ProcessShieldHealthUpdate(int shieldHealthP1, int shieldHealthP2)
        {
            shieldHealthController.SetShieldHealthPlayer1(shieldHealthP1);
            shieldHealthController.SetShieldHealthPlayer2(shieldHealthP2);
        }

        private void ProcessGrenadeUpdate(int grenadeP1, int grenadeP2)
        {
            grenadeController.SetGrenadeCounter(grenadeP1, grenadeP2);
        }

        private void ProcessShieldTimeUpdate(float shieldTimeP1, float shieldTimeP2)
        {
            shieldCountdown.SetShieldTime(shieldTimeP1, shieldTimeP2);
        }

        private void ProcessAction(string actionP1, string actionP2)
        {
            switch (actionP1)
            {
                case "grenade":
                    grenadeController.ExplosionButtonPressPlayer1();
                    grenadeTriggerAnimation.TriggerAnimation();
                    ProcessGrenadeHitFeedback("p1");
                    break;
                case "shoot":
                    shootController.GunShotPlayer1();
                    gunController.PlayGunShotEffect();
                    break;
                case "shield":
                    shieldController.ActivateShieldPlayer1();
                    break;
                case "reload":
                    shootController.ReloadPlayer1();
                    break;
                case "logout":
                    Disconnect();
                    sceneChanger.ChangeScene("ScoreboardOverlay");
                    break;
                default:
                    break;
            }

            switch (actionP2)
            {
                case "grenade":
                    grenadeController.ExplosionButtonPressPlayer2();
                    enemyGrenadeTriggerAnimation.TriggerAnimation();
                    // Feedback hit
                    // ProcessGrenadeHitFeedback("p2");
                    break;
                case "shoot":
                    shootController.GunShotPlayer2();
                    gunController.PlayGunShotEffectPlayer2();
                    break;
                case "shield":
                    shieldController.ActivateShieldPlayer2();
                    break;
                case "reload":
                    shootController.ReloadPlayer2();
                    break;
                default:
                    break;
            }
        }

        private void ProcessGrenadeHitFeedback(string thrower)
        {
            bool enemyDetected = enemyDetector.hasEnemy;
            // bool enemyDetected = true;
            if (enemyDetected)
            {
                PublishMessage("p2");
                // if (thrower == "p1")
                // {
                //     PublishMessage("p2");
                // }
                // else if (thrower == "p2")
                // {
                //     PublishMessage("p1");
                // }
            }
            else
            {
                PublishMessage("none");
            }
        }
    }
}
