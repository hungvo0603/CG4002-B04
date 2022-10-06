using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using M2MQTT.MainController;

public class GrenadeController : MonoBehaviour
{
    public Player player1;
    public Player player2;

    [SerializeField] private ShieldController shieldController;
    [SerializeField] private ShieldHealthController shieldHealthController;
    private bool _isShieldActivatedPlayer1;
    private bool _isShieldActivatedPlayer2;
    
    private const int MAX_GRENADE = 2;
    private const int GRENADE_DAMAGE = 30;

    public EnemyDetector enemyDetector;
    public ShieldDetector shieldDetector;
    private bool hasEnemy;
    private bool hasShield;
    
    public Button grenadeButtonPlayer1;
    public Button grenadeButtonPlayer2;

    public int player1Grenade;
    public int player2Grenade;

    [SerializeField] private GameObject[] grenadePlayer1;
    [SerializeField] private GameObject[] grenadePlayer2;

    void Start ()
    {
        grenadeButtonPlayer1.onClick.AddListener(ExplosionButtonPressPlayer1);
        grenadeButtonPlayer2.onClick.AddListener(ExplosionButtonPressPlayer2);
        player1Grenade = MAX_GRENADE;
        player2Grenade = MAX_GRENADE;
        SelfUpdateGrenadeDisplay();
        OpponentUpdateGrenadeDisplay();
        hasEnemy = false;
        hasShield = false;
        // _isShieldActivatedPlayer1 = false;
        // _isShieldActivatedPlayer2 = false;
    }

    void Update()
    {
        
    }

    public void ExplosionButtonPressPlayer1()
    {
        if (player1Grenade > 0)
        {
            StartCoroutine(ThrowGrenadePlayer1());
        }
        else
        {
            player1Grenade = MAX_GRENADE;
            SelfUpdateGrenadeDisplay();
        }
    }

    public void ExplosionButtonPressPlayer2()
    {
        if (player2Grenade > 0)
        {
            StartCoroutine(ThrowGrenadePlayer2());
        }
        else
        {
            player2Grenade = MAX_GRENADE;
            OpponentUpdateGrenadeDisplay();
        }
    }

    IEnumerator ThrowGrenadePlayer1() 
    {
        // player1Grenade -= 1;
        SelfUpdateGrenadeDisplay();

        hasEnemy = enemyDetector.hasEnemy;
        hasShield = shieldDetector.hasShieldEnemy;

        // int currentShieldHealthPlayer2 = shieldHealthController.currentShieldHealthPlayer2;
        // int shieldHealthPlayer2;

        yield return new WaitForSeconds(2.01f);
        
        // Game logic for grenade
        /**
        if (hasEnemy)
        {
            if (hasShield)
            {
                shieldHealthPlayer2 = currentShieldHealthPlayer2 - GRENADE_DAMAGE;
                if (shieldHealthPlayer2 <= 0)
                {
                    shieldHealthController.SetShieldHealthPlayer2(0);
                    player2.TakeDamagePlayer2(-shieldHealthPlayer2);
                }
            }
            else
            {
                player2.TakeDamagePlayer2(GRENADE_DAMAGE);
            }
        }
        */

    }

    IEnumerator ThrowGrenadePlayer2()
    {
        // player2Grenade -= 1;
        OpponentUpdateGrenadeDisplay();
        _isShieldActivatedPlayer1 = shieldController.isShieldActivatedPlayer1;

        // int currentShieldHealthPlayer1 = shieldHealthController.currentShieldHealthPlayer1;
        // int shieldHealthPlayer1;

        yield return new WaitForSeconds(2.01f);
        
        // Game Logic for Grenade
        /**
        if (_isShieldActivatedPlayer1)
        {
            shieldHealthPlayer1 = currentShieldHealthPlayer1 - GRENADE_DAMAGE;
            if (shieldHealthPlayer1 <= 0)
            {
                shieldHealthController.SetShieldHealthPlayer1(0);
                player1.TakeDamagePlayer1(-shieldHealthPlayer1);
            }
        }
        else
        {
            player1.TakeDamagePlayer1(GRENADE_DAMAGE);
        }
        */

    }

    void SelfUpdateGrenadeDisplay()
    {
        for (int i = 0; i < player1Grenade; i++)
        {
            grenadePlayer1[i].gameObject.SetActive(true);
        }
        for (int i = player1Grenade; i < MAX_GRENADE; i++)
        {   
            grenadePlayer1[i].gameObject.SetActive(false);
        }
    }

    void OpponentUpdateGrenadeDisplay()
    {
        for (int i = 0; i < player2Grenade; i++)
        {
            grenadePlayer2[i].gameObject.SetActive(true);
        }
        for (int i = player2Grenade; i < MAX_GRENADE; i++)
        {
            grenadePlayer2[i].gameObject.SetActive(false);
        }
    }

    public void SetGrenadeCounter(int grenadeP1, int grenadeP2)
    {
        player1Grenade = grenadeP1;
        player2Grenade = grenadeP2;
        SelfUpdateGrenadeDisplay();
        OpponentUpdateGrenadeDisplay();
    }
}
