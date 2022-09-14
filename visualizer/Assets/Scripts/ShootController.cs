using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ShootController : MonoBehaviour
{
    // public Player player1;
    public Player player2;
    [SerializeField] private ShieldController shieldController;
    [SerializeField] private ShieldHealthController shieldHealthController;
    // private bool _isShieldActivatedPlayer1;
    private bool _isShieldActivatedPlayer2;

    private const int MAX_BULLET = 6;
    private const int SHOOT_DAMAGE = 10;

    public EnemyDetector enemy;
    private bool hasEnemy;

    public int player1Bullet;

    // Start is called before the first frame update
    void Start()
    {
        player1Bullet = MAX_BULLET;
        hasEnemy = false;
        // _isShieldActivatedPlayer1 = false;
        _isShieldActivatedPlayer2 = false;
    }

    void Update()
    {
        if (player1Bullet == 0)
        {
            player1Bullet = MAX_BULLET;
        }
        // _isShieldActivatedPlayer1 = shieldController.isShieldActivatedPlayer1;
        _isShieldActivatedPlayer2 = shieldController.isShieldActivatedPlayer2;
    }

    public void GunShot()
    {
        hasEnemy = enemy.hasEnemy;
        player1Bullet -= 1;
        int currentShieldHealthPlayer2 = shieldHealthController.currentShieldHealthPlayer2;
        int shieldHealthPlayer2;
        if (hasEnemy)
        {
            if (_isShieldActivatedPlayer2)
            {
                shieldHealthPlayer2 = currentShieldHealthPlayer2 - SHOOT_DAMAGE;
                if (shieldHealthPlayer2 >= 0)
                {
                    shieldHealthController.SetShieldHealthPlayer2(shieldHealthPlayer2);
                }
            } 
            else
            {
                player2.TakeDamagePlayer2(SHOOT_DAMAGE);
            }

        }
    }

}
