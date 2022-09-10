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
    // Start is called before the first frame update
    void Start()
    {
        player1CurrentHealth = MAX_HEALTH;
        healthBarPlayer1.SetHealth(MAX_HEALTH);

        player2CurrentHealth = MAX_HEALTH;
        healthBarPlayer2.SetHealth(MAX_HEALTH);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void TakeDamageFromShotPlayer1()
    {
        player1CurrentHealth -= SHOT_DAMAGE;
        if (player1CurrentHealth <= 0)
        {
            player1CurrentHealth = MAX_HEALTH;
        } 
        healthBarPlayer1.SetHealth(player1CurrentHealth);
    }

    public void TakeDamageFromShotPlayer2()
    {
        player2CurrentHealth -= SHOT_DAMAGE;
        if (player2CurrentHealth <= 0)
        {
            player2CurrentHealth = MAX_HEALTH;
        } 
        healthBarPlayer2.SetHealth(player2CurrentHealth);
    }

}
