using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ShootController : MonoBehaviour
{
    private const int MAX_BULLET = 6;

    public Player player1;


    [SerializeField] private TextMeshProUGUI player1BulletText;

    int player1Bullet = 6;

    // Start is called before the first frame update
    void Start()
    {
        player1BulletText.text = "6/6";
    }

    public void GunShot()
    {
        player1Bullet = (player1Bullet > 0) ? (player1Bullet - 1) : MAX_BULLET;
        player1BulletText.text = player1Bullet.ToString() + "/6";
        player1.TakeDamageFromShot();
    }

}
