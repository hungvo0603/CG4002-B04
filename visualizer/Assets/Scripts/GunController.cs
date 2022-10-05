using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GunController : MonoBehaviour
{
    // Start is called before the first frame update
    public AudioSource gunShotSound;
    public ParticleSystem gunShotEffect;

    void Start()
    {
        gunShotEffect.Stop();
        gunShotEffect.Clear();
    }

    public void PlayGunShotEffect() {
        gunShotSound.Play();
        gunShotEffect.Play();
    }
}
