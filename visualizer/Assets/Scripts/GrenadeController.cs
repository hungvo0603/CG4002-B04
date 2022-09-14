using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GrenadeController : MonoBehaviour
{
    public Player player1;
    public Player player2;

    [SerializeField] private ShieldController shieldController;
    [SerializeField] private ShieldHealthController shieldHealthController;
    // private bool _isShieldActivatedPlayer1, _isShieldActivatedPlayer2;
    
    private const int MAX_GRENADE = 2;
    private const int GRENADE_DAMAGE = 30;

    public EnemyDetector enemyDetector;
    public ShieldDetector shieldDetector;
    private bool hasEnemy;
    private bool hasShield;

    public int player1Grenade;


    void Start ()
    {
        player1Grenade = MAX_GRENADE;
        hasEnemy = false;
        hasShield = false;
        // _isShieldActivatedPlayer1 = false;
        // _isShieldActivatedPlayer2 = false;
    }

    void Update()
    {
        // _isShieldActivatedPlayer1 = shieldController.isShieldActivatedPlayer1;
        // _isShieldActivatedPlayer2 = shieldController.isShieldActivatedPlayer2;
    }

    public void ExplosionButtonPress()
    {
        if (player1Grenade > 0)
        {
            StartCoroutine(PlayGrenadeExplosionPlayer1());
        }
        else
        {
            player1Grenade = MAX_GRENADE;
        }
    }

    IEnumerator PlayGrenadeExplosionPlayer1() 
    {
        hasEnemy = enemyDetector.hasEnemy;
        hasShield = shieldDetector.hasShieldEnemy;

        int currentShieldHealthPlayer2 = shieldHealthController.currentShieldHealthPlayer2;
        int shieldHealthPlayer2;
        
        yield return new WaitForSeconds(2.01f);

        player1Grenade -= 1;

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
    }
}
