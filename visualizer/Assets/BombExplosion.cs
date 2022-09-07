using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BombExplosion : MonoBehaviour
{
    public GameObject explosionParticles;

    void Start ()
    {
        explosionParticles.SetActive(false);
    }

    public void ExplosionButtonPress ()
    {
        explosionParticles.SetActive(true);
    }

}
