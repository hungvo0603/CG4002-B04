using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ShootController : MonoBehaviour
{
    public Player player1;
    public Player player2;
    [SerializeField] private ShieldController shieldController;
    [SerializeField] private ShieldHealthController shieldHealthController;
    private bool _isShieldActivatedPlayer1;
    private bool _isShieldActivatedPlayer2;

    private const int MAX_BULLET = 6;
    private const int SHOOT_DAMAGE = 10;

    public AudioSource reloadSound;

    public EnemyDetector enemy;
    private bool hasEnemy;

    public int player1Bullet;
    public int player2Bullet;

    // Start is called before the first frame update
    void Start()
    {
        player1Bullet = MAX_BULLET;
        player2Bullet = MAX_BULLET;
        hasEnemy = false;
        // _isShieldActivatedPlayer1 = false;
        _isShieldActivatedPlayer2 = false;
    }

    void Update()
    {
        _isShieldActivatedPlayer1 = shieldController.isShieldActivatedPlayer1;
        _isShieldActivatedPlayer2 = shieldController.isShieldActivatedPlayer2;
    }

    public void GunShotPlayer1()
    {
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

    public void GunShotPlayer2()
    {
        int currentShieldHealthPlayer1 = shieldHealthController.currentShieldHealthPlayer1;
        int shieldHealthPlayer1;
        if (_isShieldActivatedPlayer1)
        {
            shieldHealthPlayer1 = currentShieldHealthPlayer1 - SHOOT_DAMAGE;
            if (shieldHealthPlayer1 >= 0)
            {
                shieldHealthController.SetShieldHealthPlayer1(shieldHealthPlayer1);
            }
        }
        else
        {
            player1.TakeDamagePlayer1(SHOOT_DAMAGE);
        }
    }

    public void SetBullet(int bulletP1, int bulletP2)
    {
        player1Bullet = bulletP1;
        player2Bullet = bulletP2;
    }

    public void ReloadPlayer1()
    {
        player1Bullet = MAX_BULLET;
    }

    public void ReloadPlayer2()
    {
        player2Bullet = MAX_BULLET;
    }

}
