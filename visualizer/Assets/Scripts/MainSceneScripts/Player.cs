using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Player : MonoBehaviour
{
    private const int MAX_HEALTH = 100;

    private const int SHOT_DAMAGE = 10;
    private const int GRENADE_DAMAGE = 30;

    public HealthBarController healthBarPlayer1;
    public HealthBarController healthBarPlayer2;
    
    int player1CurrentHealth;
    int player2CurrentHealth;
    public static int player1KillStatistic;
    public static int player2KillStatistic;
    // Start is called before the first frame update
    void Start()
    {
        player1CurrentHealth = MAX_HEALTH;
        healthBarPlayer1.SetHealth(MAX_HEALTH);

        player2CurrentHealth = MAX_HEALTH;
        healthBarPlayer2.SetHealth(MAX_HEALTH);

        player1KillStatistic = 0;
        player2KillStatistic = 0;
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public int getPlayer1Kill()
    {
        return player1KillStatistic;
    }

    public int getPlayer2Kill()
    {
        return player2KillStatistic;
    }

    public void TakeDamagePlayer1(int damage)
    {
        player1CurrentHealth -= damage;
        if (player1CurrentHealth <= 0)
        {
            player2KillStatistic += 1;
            player1CurrentHealth = MAX_HEALTH;
        } 
        healthBarPlayer1.SetHealth(player1CurrentHealth);
    }

    public void TakeDamagePlayer2(int damage)
    {
        player2CurrentHealth -= damage;
        if (player2CurrentHealth <= 0)
        {
            player1KillStatistic += 1;
            player2CurrentHealth = MAX_HEALTH;
        } 
        healthBarPlayer2.SetHealth(player2CurrentHealth);
    }

    public void SetKillStatistics(int killP1, int killP2)
    {
        player1KillStatistic = killP1;
        player2KillStatistic = killP2;
    }


}
