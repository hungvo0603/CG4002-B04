using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ShieldController : MonoBehaviour
{
    public GameObject shieldPlayer1;
    public GameObject shieldBarPlayer1;
    public Button shieldActivateButtonPlayer1;
    public bool isShieldActivatedPlayer1;

    public GameObject shieldPlayer2;
    public GameObject shieldBarPlayer2;
    public Button shieldActivateButtonPlayer2;
    public bool isShieldActivatedPlayer2;

    void Start ()
    {
        shieldActivateButtonPlayer1.onClick.AddListener(ActivateShieldPlayer1);
        shieldActivateButtonPlayer2.onClick.AddListener(ActivateShieldPlayer2);
        shieldPlayer1.gameObject.SetActive(false);
        shieldPlayer2.gameObject.SetActive(false);
        isShieldActivatedPlayer1 = false;
        isShieldActivatedPlayer2 = false;
    }

    void Update ()
    {
        
    }

    public void ActivateShieldPlayer1()
    {
        shieldPlayer1.gameObject.SetActive(true);
        isShieldActivatedPlayer1 = true;
        shieldActivateButtonPlayer1.interactable = false;
        StartCoroutine(DeactivateShieldPlayer1());
    }
    
    public void ActivateShieldPlayer2()
    {
        shieldPlayer2.gameObject.SetActive(true);
        isShieldActivatedPlayer2 = true;
        shieldActivateButtonPlayer2.interactable = false;
        StartCoroutine(DeactivateShieldPlayer2());
    }

    public void BreakShieldPlayer1()
    {
        shieldPlayer1.gameObject.SetActive(false);
        isShieldActivatedPlayer1 = false;
    }

    public void BreakShieldPlayer2()
    {
        shieldPlayer2.gameObject.SetActive(false);
        isShieldActivatedPlayer2 = false;
    }

    IEnumerator DeactivateShieldPlayer1()
    {
        yield return new WaitForSeconds(10f);
        shieldActivateButtonPlayer1.interactable = true;
        shieldPlayer1.gameObject.SetActive(false);
        isShieldActivatedPlayer1 = false;
    }

    IEnumerator DeactivateShieldPlayer2()
    {
        yield return new WaitForSeconds(10f);
        shieldActivateButtonPlayer2.interactable = true;
        shieldPlayer2.gameObject.SetActive(false);
        isShieldActivatedPlayer2 = false;
    }

}
