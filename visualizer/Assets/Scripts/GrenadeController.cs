using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GrenadeController : MonoBehaviour
{
    public ParticleSystem explosionParticles;
    public AudioSource grenadeExplosionSound;
    private const int MAX_GRENADE = 2;
    private const int GRENADE_DAMAGE = 30;
    public Player pl;

    public EnemyDetector enemy;
    private bool hasEnemy;

    public int player1Grenade;


    void Start ()
    {
        player1Grenade = MAX_GRENADE;
        explosionParticles.Stop();
        explosionParticles.Clear();
        hasEnemy = false;
    }

    void Update()
    {

    }

    public void ExplosionButtonPress()
    {
        if (player1Grenade > 0)
        {
            StartCoroutine(PlayExplosionEffect());
        } else {
            player1Grenade = MAX_GRENADE;
        }
    }

    IEnumerator PlayExplosionEffect() 
    {
        yield return new WaitForSeconds(2.01f);
        player1Grenade -= 1;
        explosionParticles.Play();
        grenadeExplosionSound.Play();
        
        hasEnemy = enemy.hasEnemy;
        if (hasEnemy)
        {
            pl.TakeDamagePlayer2(GRENADE_DAMAGE);
        }
    }
}
