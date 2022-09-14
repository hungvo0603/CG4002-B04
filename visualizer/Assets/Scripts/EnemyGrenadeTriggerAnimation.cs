using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class EnemyGrenadeTriggerAnimation : MonoBehaviour
{
    [SerializeField] private Button launchGrenadePlayer2;
    public GrenadeController grenadeController;

    public ParticleSystem explosionParticles;
    public AudioSource grenadeExplosionSound;

    // Start is called before the first frame update
    void Start()
    {
        explosionParticles.Stop();
        explosionParticles.Clear();
        launchGrenadePlayer2.onClick.AddListener(TriggerAnimation);
    }

    void Update()
    {
        
    }

    void TriggerAnimation()
    {
        GetComponent<Animator>().Play("EnemyGrenadeThrowing");
        StartCoroutine(TriggerExplosion());
    }

    IEnumerator TriggerExplosion()
    {
        yield return new WaitForSeconds(2f);
        explosionParticles.Play();
        grenadeExplosionSound.Play();
    }
}
