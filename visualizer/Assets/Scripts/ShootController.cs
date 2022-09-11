using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ShootController : MonoBehaviour
{
    private const int MAX_BULLET = 6;

    public Player player1;
    public Player player2;


    public int player1Bullet;

    // Start is called before the first frame update
    void Start()
    {
        player1Bullet = MAX_BULLET;
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
        player1Bullet -= 1;
        player2.TakeDamageFromShotPlayer2();
    }

}
