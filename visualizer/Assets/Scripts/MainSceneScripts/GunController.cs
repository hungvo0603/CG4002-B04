using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GunController : MonoBehaviour
{
    // Start is called before the first frame update
    public AudioSource gunShotSound;
    public AudioSource gunReloadSound;
    public ParticleSystem gunShotEffect;

    void Start()
    {
        gunShotEffect.Stop();
        gunShotEffect.Clear();
    }

    public void PlayGunShotEffect() 
    {
        gunShotSound.Play();
        gunShotEffect.Play();
        GetComponent<Animator>().Play("Shoot");
    }

    public void PlayGunShotEffectPlayer2()
    {
        gunShotSound.Play();
    }

    public void PlayReloadEffect() 
    {
        gunReloadSound.Play(); 
        GetComponent<Animator>().Play("Reload");
    }
}
