using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Grenade : MonoBehaviour
{

    public float delay = 3f;
    public float radius = 5f;
    public float explosionForce = 100f;

    [SerializeField] GameObject explosionEffect;

    float countdown;
    bool hasExploded = false;

    // Start is called before the first frame update
    void Start ()
    {
        countdown = delay;
    }

    // Update is called once per frame
    void Update ()
    {
        countdown -= Time.deltaTime;
        if (countdown <= 0f && !hasExploded)
        {
            Explode();
        }
    }

    public void Explode ()
    {
        // Show effect
        GameObject grenade = Instantiate(explosionEffect, transform.position, transform.rotation);
        Destroy (grenade, 2);

        // Nearby object (other player)
        Collider[] colliders = Physics.OverlapSphere(transform.position, radius);
        foreach (Collider nearbyObject in colliders)
        {
            // Add force
            Rigidbody rb = nearbyObject.GetComponent<Rigidbody>();
            if (rb != null)
            {
                rb.AddExplosionForce(explosionForce, transform.position, radius);
            }
            // Damage
        }

        hasExploded = true;

        // Remove grenade
        Destroy(gameObject);
    }
}
