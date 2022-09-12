using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GunController : MonoBehaviour
{
    // Start is called before the first frame update
    public AudioSource gunShotSound;

    public void PlayGunShotSound() {
        gunShotSound.Play();
    }
}
