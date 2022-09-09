using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GrenadeThrower : MonoBehaviour
{
    public float throwForce = 100f;
    public Button m_GrenadeThrowingButton;
    public GameObject grenadePrefab;

    public void ThrowGrenade() {
        GameObject grenade = Instantiate(grenadePrefab, transform.position, transform.rotation);
        Rigidbody rb = grenade.GetComponent<Rigidbody>();
    }
}
