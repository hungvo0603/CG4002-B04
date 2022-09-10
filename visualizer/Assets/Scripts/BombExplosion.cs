using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BombExplosion : MonoBehaviour
{
    public ParticleSystem explosionParticles;

    void Start ()
    {
        explosionParticles.Stop();
        explosionParticles.Clear();
    }

    public void ExplosionButtonPress()
    {
        explosionParticles.Play();
    }
}
