using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GrenadeTriggerAnimation : MonoBehaviour
{
    [SerializeField] private Button launchGrenade;
    public GrenadeController grenadeController;
    int grenadeCounter;

    public ParticleSystem explosionParticles;
    public AudioSource grenadeExplosionSound;

    // Start is called before the first frame update
    void Start()
    {
        explosionParticles.Stop();
        explosionParticles.Clear();
        grenadeCounter = -1;
        launchGrenade.onClick.AddListener(TriggerAnimation);
    }

    void Update()
    {
        grenadeCounter = grenadeController.player1Grenade;
    }

    void TriggerAnimation()
    {
        if (grenadeCounter > 0)
        {
            GetComponent<Animator>().Play("SelfGrenadeThrowing");
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
