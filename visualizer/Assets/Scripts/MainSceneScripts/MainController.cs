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
using TMPro;

namespace M2MQTT.MainController
{
    public class MainController : M2MqttUnityClient
    {
        [Header("Registered Player")]
        public TextMeshProUGUI playerRegistered;
        public TextMeshProUGUI playerIdentifier;

        [Header("Connection UI")]
        public Image selfBrokerConnection;
        public Image selfGunConnection;
        public Image selfVestConnection;
        public Image selfGloveConnection;
        public Image opponentBrokerConnection;
        public Image opponentGunConnection;
        public Image opponentVestConnection;
        public Image opponentGloveConnection;
        public Button PublishMessageButton;

        [Header("Healthbar UI")]
        public HealthBarController healthBarPlayer1;
        public HealthBarController healthBarPlayer2;

        [Header("Bullet UI")]
        public ShootController shootController;
        public GunController gunController;
        public BulletDisplay bulletDisplay;
        public GameObject bulletDisplayP1;
        public GameObject bulletDisplayP2;

        [Header("Grenade UI")]
        public GameObject grenadePlayer1;
        public GameObject grenadePlayer2;
        public GrenadeController grenadeController;
        public GrenadeTriggerAnimation grenadeTriggerAnimation;
        public EnemyGrenadeTriggerAnimation enemyGrenadeTriggerAnimation;

        [Header("Shield UI")]
        public ShieldHealthController shieldHealthController;
        public ShieldController shieldController;
        public ShieldCountdown shieldCountdown;
        public GameObject shieldCdCanvasPlayer1;
        public GameObject shieldCdCanvasPlayer2;
        public GameObject opponentShield;
        public ShieldTriggerAnimation shieldAnimation;

        [Header("KDA UI")]
        public Player player;

        [Header("Enemy Detector")]
        public Animator AROpponent;
        public EnemyDetector enemyDetector;

        [Header("Scoreboard Overlay")]
        public GameObject scoreboardOverlay;

        [Header("Data")]
        public PlayerDataJson playerData = new PlayerDataJson();
        public PlayerStatsJson player1Data = new PlayerStatsJson();
        public PlayerStatsJson player2Data = new PlayerStatsJson();
        // public GrenadeHitJson grenadeHitData = new GrenadeHitJson();

        private List<string> eventMessages = new List<string>();
        private bool updateUI = false;
        private int counter = 0;

        public void PublishMessage(string msg)
        {   
            if (!String.IsNullOrEmpty(msg))
            {
                client.Publish("cg4002/4/u96_viz", System.Text.Encoding.UTF8.GetBytes(msg), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
                Debug.Log(msg);
                Debug.Log("Feedback message published");
            }
            else {
            // TESTING FOR VISUALIZER
            string sample_json_string = "{\"p1\": {\"hp\": 100, \"action\": \"grenade\", \"bullets\": 5, \"grenades\": 1, \"shield_time\": 10, \"shield_health\": 30, \"num_deaths\": 8, \"num_shield\": 3}, \"p2\": {\"hp\": 100, \"action\": \"shield\", \"bullets\": 6, \"grenades\": 2, \"shield_time\": 10, \"shield_health\": 30, \"num_deaths\": 5, \"num_shield\": 3}}";
            client.Publish("cg4002/4/viz_u96", System.Text.Encoding.UTF8.GetBytes(sample_json_string), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
            Debug.Log("Test message published");
            PublishMessageButton.gameObject.SetActive(false);
            StartCoroutine(ReactivatePublishButton());
            }
        }

        IEnumerator ReactivatePublishButton()
        {
            yield return new WaitForSeconds(10f);
            PublishMessageButton.gameObject.SetActive(true);
        }

        protected override void OnConnecting()
        {
            base.OnConnecting();
            Debug.Log("Connecting to Ultra96.");
            updateUI = true;
        }

        protected override void OnConnected()
        {
            base.OnConnected();
            int whichPlayer = SettingsController.REGISTERED_PLAYER;
            if (whichPlayer == 1)
                selfBrokerConnection.color = UnityEngine.Color.green;
            else if (whichPlayer == 2)
                opponentBrokerConnection.color = UnityEngine.Color.green;
            updateUI = true;
        }

        protected override void SubscribeTopics()
        {
            Debug.Log("Topic Subscribed");
            client.Subscribe(new string[] { "cg4002/4/viz_u96" }, new byte[] { MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE });
        }

        protected override void UnsubscribeTopics()
        {
            Debug.Log("Topic Unsubscribed");
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
            int whichPlayer = SettingsController.REGISTERED_PLAYER;
            if (whichPlayer == 1)
                selfBrokerConnection.color = UnityEngine.Color.red;
            else if (whichPlayer == 2)
                opponentBrokerConnection.color = UnityEngine.Color.red;
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
            if (SettingsController.REGISTERED_PLAYER == 1)
            {
                bulletDisplayP2.gameObject.SetActive(false);
                grenadePlayer2.gameObject.SetActive(false);
                shieldCdCanvasPlayer2.gameObject.SetActive(false);
            }
            else if (SettingsController.REGISTERED_PLAYER == 2)
            {
                bulletDisplayP1.gameObject.SetActive(false);
                grenadePlayer1.gameObject.SetActive(false);
                shieldCdCanvasPlayer1.gameObject.SetActive(false);
            }
            updateUI = false;
        }

        protected override void Start()
        {
            scoreboardOverlay.gameObject.SetActive(false);
            playerRegistered.text = "Player " + SettingsController.REGISTERED_PLAYER.ToString();
            playerIdentifier.text = "B04";
            opponentShield.gameObject.SetActive(false);
            UpdateSelfConnectionStatus();
            StartCoroutine(SetPlayerSide());
            Connect();
            updateUI = true;
            base.Start();
        }

        IEnumerator SetPlayerSide()
        {
            yield return new WaitForSeconds(1f);

            if (SettingsController.REGISTERED_PLAYER == 1)
            {
                playerRegistered.text = (counter == 0) ? "<<" : "<<" + playerRegistered.text;
            } 
            else if (SettingsController.REGISTERED_PLAYER == 2)
            {
                playerRegistered.text = (counter == 0) ? ">>" : playerRegistered.text + ">>";
            }

            counter += 1;
            if (counter == 3) 
            {
                counter = 0;
                StartCoroutine(DisablePlayerNotice());
            }
            else
            {
                StartCoroutine(SetPlayerSide());
            }
            
        }

        IEnumerator DisablePlayerNotice()
        {
            yield return new WaitForSeconds(2f);
            if (SettingsController.REGISTERED_PLAYER == 1) 
            {
                playerIdentifier.text = "< P1";
            } 
            else if (SettingsController.REGISTERED_PLAYER == 2)
            {
                playerIdentifier.text = "P2 >";
            }
            playerRegistered.gameObject.SetActive(false);
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

        private void ProcessMessage(string msg)
        {
            // string[] specialMessage = new string[] {"p1", "p2", "none"};
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
                int whichPlayer = SettingsController.REGISTERED_PLAYER;
                if (player1Data.action == "grenade") ProcessGrenadeHitFeedback("p1");
                if (player2Data.action == "grenade") ProcessGrenadeHitFeedback("p2");
                string selfAction = (whichPlayer == 1) ? player1Data.action : player2Data.action;
                string opponentAction = (whichPlayer == 1) ? player2Data.action : player1Data.action;
                ProcessAction(selfAction, opponentAction);
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

        private void UpdateSelfConnectionStatus()
        {
            int playerNumber = SettingsController.REGISTERED_PLAYER;
            if (playerNumber == 1)
            {
                selfGunConnection.color = UnityEngine.Color.red;
                selfVestConnection.color = UnityEngine.Color.red;
                selfGloveConnection.color = UnityEngine.Color.red;
                opponentBrokerConnection.gameObject.SetActive(false);
                opponentGloveConnection.gameObject.SetActive(false);
                opponentGunConnection.gameObject.SetActive(false);
                opponentVestConnection.gameObject.SetActive(false);
            }
            else if (playerNumber == 2)
            {
                opponentGunConnection.color = UnityEngine.Color.red;
                opponentVestConnection.color = UnityEngine.Color.red;
                opponentGloveConnection.color = UnityEngine.Color.red;
                selfBrokerConnection.gameObject.SetActive(false);
                selfGloveConnection.gameObject.SetActive(false);
                selfGunConnection.gameObject.SetActive(false);
                selfVestConnection.gameObject.SetActive(false);
            }
        }

        private void ProcessHealthBarUpdate(int healthP1, int healthP2)
        {
            healthBarPlayer1.SetHealth(Math.Max(healthP1, 0));
            healthBarPlayer2.SetHealth(Math.Max(healthP2, 0));
        }

        private void ProcessBulletUpdate(int bulletP1, int bulletP2)
        {
            shootController.SetBullet(Math.Max(bulletP1, 0), Math.Max(bulletP2, 0));
            bulletDisplay.UpdateBulletDisplayP1();
            bulletDisplay.UpdateBulletDisplayP2();
        }

        private void ProcessKDAUpdate(int killP1, int killP2)
        {
            player.SetKillStatistics(killP1, killP2);
        }

        private void ProcessShieldCounterUpdate(int shieldP1, int shieldP2)
        {
            shieldController.SetShieldCount(Math.Max(shieldP1, 0), Math.Max(shieldP2, 0));
        }

        // This won't have effect if the shield is not activated
        private void ProcessShieldHealthUpdate(int shieldHealthP1, int shieldHealthP2)
        {
            shieldHealthController.SetShieldHealthPlayer1(Math.Max(shieldHealthP1, 0));
            shieldHealthController.SetShieldHealthPlayer2(Math.Max(shieldHealthP2, 0));
        }

        private void ProcessGrenadeUpdate(int grenadeP1, int grenadeP2)
        {
            grenadeController.SetGrenadeCounter(Math.Max(grenadeP1, 0), Math.Max(grenadeP2, 0));
        }

        private void ProcessShieldTimeUpdate(float shieldTimeP1, float shieldTimeP2)
        {
            shieldCountdown.SetShieldTime(shieldTimeP1, shieldTimeP2);
        }

        private void ProcessAction(string selfAction, string opponentAction)
        {
            string currentPlayer = "p" + SettingsController.REGISTERED_PLAYER.ToString();
            UpdateConnectionStatus(currentPlayer, selfAction);
            switch (selfAction)
            {
                case "grenade":
                    grenadeController.ExplosionButtonPressPlayer1();
                    grenadeTriggerAnimation.TriggerAnimation();
                    break;
                case "shoot":
                    gunController.PlayGunShotEffect();
                    break;
                case "shield":
                    if (currentPlayer == "p1") shieldController.ActivateShieldPlayer1();
                    else if (currentPlayer == "p2") shieldController.ActivateShieldPlayer2();
                    shieldAnimation.TriggerAnimation();
                    break;
                case "reload":
                    gunController.PlayReloadEffect();
                    break;
                case "logout":
                    scoreboardOverlay.gameObject.SetActive(true);
                    StartCoroutine(HideScoreboardOverlay());
                    break;
                default:
                    break;
            }
        
            switch (opponentAction)
            {
                case "grenade":
                    grenadeController.ExplosionButtonPressPlayer2();
                    enemyGrenadeTriggerAnimation.TriggerAnimation();
                    break;
                case "shoot":
                    gunController.PlayGunShotEffectPlayer2();
                    AROpponent.Play("Shoot_SingleShot_AR");
                    break;
                case "shield":
                    if (currentPlayer == "p2") shieldController.ActivateShieldPlayer1();
                    else if (currentPlayer == "p1") shieldController.ActivateShieldPlayer2();
                    opponentShield.gameObject.SetActive(true);
                    AROpponent.Play("Idle_Ducking_AR");
                    StartCoroutine(StandFront());
                    break;
                case "reload":
                    shootController.ReloadPlayer2();
                    AROpponent.Play("Reload");
                    break;
                case "logout":
                    scoreboardOverlay.gameObject.SetActive(true);
                    StartCoroutine(HideScoreboardOverlay());
                    break;
                default:
                    break;
            }
        }

        private void UpdateConnectionStatus(string currentPlayer, string selfAction)
        {
            if (currentPlayer == "p1")
            {
                switch (selfAction)
                {
                    case "gun connect":
                        selfGunConnection.color = UnityEngine.Color.green;
                        break;
                    case "gun disconnect":
                        selfGunConnection.color = UnityEngine.Color.red;
                        break;
                    case "vest connect":
                        selfVestConnection.color = UnityEngine.Color.green;
                        break;
                    case "vest disconnect":
                        selfVestConnection.color = UnityEngine.Color.red;
                        break;
                    case "glove connect":
                        selfGloveConnection.color = UnityEngine.Color.green;
                        break;
                    case "glove disconnect":
                        selfGloveConnection.color = UnityEngine.Color.red;
                        break;
                    default:
                        break;
                }
            }
            else if (currentPlayer == "p2")
            {
                switch (selfAction)
                {
                    case "gun connect":
                        opponentGunConnection.color = UnityEngine.Color.green;
                        break;
                    case "gun disconnect":
                        opponentGunConnection.color = UnityEngine.Color.red;
                        break;
                    case "vest connect":
                        opponentVestConnection.color = UnityEngine.Color.green;
                        break;
                    case "vest disconnect":
                        opponentVestConnection.color = UnityEngine.Color.red;
                        break;
                    case "glove connect":
                        opponentGloveConnection.color = UnityEngine.Color.green;
                        break;
                    case "glove disconnect":
                        opponentGloveConnection.color = UnityEngine.Color.red;
                        break;
                    default:
                        break;
                }
            }
        }

        private void ProcessGrenadeHitFeedback(string thrower)
        {
            bool enemyDetected = enemyDetector.hasEnemy;
            if (enemyDetected)
            {
                string message = (thrower == "p1") ? "p1-hit" : (thrower == "p2") ? "p2-hit" : "invalid-message";
                PublishMessage(message);
            }
            else
            {
                string message = (thrower == "p1") ? "p1-miss" : (thrower == "p2") ? "p2-miss" : "invalid-message";
                PublishMessage(message);
            }
        }

        IEnumerator HideScoreboardOverlay()
        {
            yield return new WaitForSeconds(5f);
            scoreboardOverlay.gameObject.SetActive(false);
        }

        IEnumerator StandFront()
        {
            yield return new WaitForSeconds(10f);
            AROpponent.Play("Idle_Guard_AR");
        }
    }
}
