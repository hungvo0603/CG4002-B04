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
        if (player1Grenade == 0)
        {
            player1Grenade = MAX_GRENADE;
        }
    }

    public void ExplosionButtonPress()
    {
        player1Grenade -= 1;
        explosionParticles.Play();
    }

    public void PlayExplosionSound() {
        grenadeExplosionSound.Play();
    }
}
