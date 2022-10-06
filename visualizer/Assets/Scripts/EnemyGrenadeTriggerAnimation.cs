using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class EnemyGrenadeTriggerAnimation : MonoBehaviour
{
    [SerializeField] private Button launchGrenadePlayer2;
    public GrenadeController grenadeController;
    int grenadeCounter;

    public ParticleSystem explosionParticles;
    public AudioSource grenadeExplosionSound;

    // Start is called before the first frame update
    void Start()
    {
        explosionParticles.Stop();
        explosionParticles.Clear();
        launchGrenadePlayer2.onClick.AddListener(TriggerAnimation);
        grenadeCounter = 0;
    }

    void Update()
    {
        grenadeCounter = grenadeController.player2Grenade;
    }

    public void TriggerAnimation()
    {
        if (grenadeCounter > 0)
        {
            GetComponent<Animator>().Play("EnemyGrenadeThrowing");
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
