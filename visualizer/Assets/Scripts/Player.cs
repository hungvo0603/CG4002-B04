using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Player : MonoBehaviour
{
    private const int MAX_HEALTH = 100;

    private const int SHOT_DAMAGE = 10;

    public HealthBarController healthBar;
    
    int playerCurrentHealth;
    // Start is called before the first frame update
    void Start()
    {
        playerCurrentHealth = MAX_HEALTH;
        healthBar.SetHealth(MAX_HEALTH);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void TakeDamageFromShot()
    {
        playerCurrentHealth -= SHOT_DAMAGE;
        if (playerCurrentHealth <= 0)
        {
            InstantRespawn();
        }
        healthBar.SetHealth(playerCurrentHealth);
    }

    void InstantRespawn()
    {
        playerCurrentHealth = MAX_HEALTH;
    }
}
