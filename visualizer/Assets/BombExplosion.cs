using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BombExplosion : MonoBehaviour
{
    public GameObject explosion;
    public float explosionForce, radius;

    private void OnCollisionEnter(Collision other)
    {
        GameObject _exp = Instantiate(explosion, transform.position, transform.rotation);
        Destroy(_exp, 5);
    }
}
