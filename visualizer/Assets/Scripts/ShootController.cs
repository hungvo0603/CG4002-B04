using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ShootController : MonoBehaviour
{
    private const int MAX_BULLET = 6;
    private const int SHOOT_DAMAGE = 10;

    public Player pl;

    public EnemyDetector enemy;
    private bool hasEnemy;

    public int player1Bullet;

    // Start is called before the first frame update
    void Start()
    {
        player1Bullet = MAX_BULLET;
        hasEnemy = false;
    }

    void Update()
    {
        if (player1Bullet == 0)
        {
            player1Bullet = MAX_BULLET;
        }
    }

    public void GunShot()
    {
        hasEnemy = enemy.hasEnemy;
        player1Bullet -= 1;
        if (hasEnemy)
        {
            pl.TakeDamagePlayer2(SHOOT_DAMAGE);
        }
    }

}
