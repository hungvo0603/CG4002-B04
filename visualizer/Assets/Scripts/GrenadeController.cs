using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GrenadeController : MonoBehaviour
{
    public ParticleSystem explosionParticles;
    public AudioSource grenadeExplosionSound;
    private const int MAX_GRENADE = 2;

    public int player1Grenade;


    void Start ()
    {
        player1Grenade = MAX_GRENADE;
        explosionParticles.Stop();
        explosionParticles.Clear();
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
    }
}
