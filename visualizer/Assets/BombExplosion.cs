using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BombExplosion : MonoBehaviour
{
    public GameObject explosionParticles;
    bool isActive;

    void Start ()
    {
        isActive = false;
        explosionParticles.SetActive(isActive);
    }

    public void ExplosionButtonPress ()
    {
        isActive = !isActive;
        explosionParticles.SetActive(isActive);
    }

}
