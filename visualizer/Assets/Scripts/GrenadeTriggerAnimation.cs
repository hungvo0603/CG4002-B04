using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GrenadeTriggerAnimation : MonoBehaviour
{
    [SerializeField] private Button launchGrenade;
    public GrenadeController grenadeController;
    int whichGrenade;

    public ParticleSystem explosionParticles;
    public AudioSource grenadeExplosionSound;

    // Start is called before the first frame update
    void Start()
    {
        explosionParticles.Stop();
        explosionParticles.Clear();
        whichGrenade = -1;
        launchGrenade.onClick.AddListener(TriggerAnimation);
    }

    void Update()
    {
        whichGrenade = grenadeController.player1Grenade;
    }

    void TriggerAnimation()
    {
        if (whichGrenade == 2) 
        {
            GetComponent<Animator>().Play("GrenadeThrowing");
            StartCoroutine(TriggerExplosion());
        } 
        else if (whichGrenade == 1)
        {
            GetComponent<Animator>().Play("GrenadeThrowing0");
            StartCoroutine(TriggerExplosion());
        }
    }

    IEnumerator TriggerExplosion()
    {
        yield return new WaitForSeconds(2f);
        explosionParticles.Play();
        grenadeExplosionSound.Play();
    }
}
