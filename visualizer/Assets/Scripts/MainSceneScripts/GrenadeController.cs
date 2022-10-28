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

    public GameObject grenadePlayer1Canvas;
    public GameObject grenadePlayer2Canvas;

    public int player1Grenade;
    public int player2Grenade;

    [SerializeField] private GameObject[] grenadePlayer1;
    [SerializeField] private GameObject[] grenadePlayer2;

    void Start ()
    {
        player1Grenade = MAX_GRENADE;
        player2Grenade = MAX_GRENADE;
        SelfUpdateGrenadeDisplay();
        OpponentUpdateGrenadeDisplay();
        hasEnemy = false;
        hasShield = false;
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
    }

    public void ExplosionButtonPressPlayer2()
    {
        if (player2Grenade > 0)
        {
            StartCoroutine(ThrowGrenadePlayer2());
        }
    }

    IEnumerator ThrowGrenadePlayer1() 
    {
        SelfUpdateGrenadeDisplay();

        hasEnemy = enemyDetector.hasEnemy;
        hasShield = shieldDetector.hasShieldEnemy;

        yield return new WaitForSeconds(2.01f);
    }

    IEnumerator ThrowGrenadePlayer2()
    {
        OpponentUpdateGrenadeDisplay();
        _isShieldActivatedPlayer1 = shieldController.isShieldActivatedPlayer1;

        yield return new WaitForSeconds(2.01f);

    }

    void SelfUpdateGrenadeDisplay()
    {
        if (grenadePlayer1Canvas.activeSelf) {
            for (int i = 0; i < player1Grenade; i++)
            {
                grenadePlayer1[i].gameObject.SetActive(true);
            }
            for (int i = player1Grenade; i < MAX_GRENADE; i++)
            {   
                grenadePlayer1[i].gameObject.SetActive(false);
            }
        }
    }

    void OpponentUpdateGrenadeDisplay()
    {
        if (grenadePlayer2Canvas.activeSelf) {
            for (int i = 0; i < player2Grenade; i++)
            {
                grenadePlayer2[i].gameObject.SetActive(true);
            }
            for (int i = player2Grenade; i < MAX_GRENADE; i++)
            {
                grenadePlayer2[i].gameObject.SetActive(false);
            }
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
