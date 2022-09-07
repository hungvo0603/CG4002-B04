using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Video;

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
