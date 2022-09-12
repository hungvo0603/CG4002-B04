using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GrenadeTriggerAnimation : MonoBehaviour
{
    [SerializeField] private Button launchGrenade;
    public GrenadeController gc;
    int whichGrenade;

    // Start is called before the first frame update
    void Start()
    {
        whichGrenade = -1;
        launchGrenade.onClick.AddListener(TriggerAnimation);
    }

    void Update()
    {
        whichGrenade = gc.player1Grenade;
    }

    void TriggerAnimation()
    {
        if (whichGrenade == 2) 
        {
            GetComponent<Animator>().Play("GrenadeThrowing");
        } 
        else if (whichGrenade == 1)
        {
            GetComponent<Animator>().Play("GrenadeThrowing0");
        }
    }
}
