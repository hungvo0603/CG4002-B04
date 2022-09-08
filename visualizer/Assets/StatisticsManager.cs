using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class StatisticsManager : MonoBehaviour
{
    private const int MAX_HEALTH = 100;
    // private const int MAX_BULLET = 6;

    [SerializeField] private TextMeshProUGUI player1HealthText;
    // [SerializeField] private TextMeshProUGUI player1BulletText;

    int player1Health = 100;
    // int player1Bullet = 6;

    void Start()
    {
        player1HealthText.text = "100%";
        // player1BulletText.text = "6/6";
    }

    public void HealthDownButtonPress() 
    {
        player1Health = (player1Health > 0) ? (player1Health - 10) : MAX_HEALTH;
        player1HealthText.text = player1Health.ToString() + "%";
    }

    // public void BulletDownButtonPress()
    // {
    //     player1Bullet = (player1Bullet > 0) ? (player1Bullet - 1) : MAX_BULLET;
    //     player1BulletText.text = player1Bullet.ToString() + "/6";
    // }
}
