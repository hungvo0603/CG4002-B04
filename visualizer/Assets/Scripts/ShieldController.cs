using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ShieldController : MonoBehaviour
{
    const int MAX_SHIELD = 3;

    // Player 1
    public GameObject shieldPlayer1;
    public GameObject shieldBarPlayer1;
    public Button shieldActivateButtonPlayer1;
    public bool isShieldActivatedPlayer1;
    public int currentShieldCountPlayer1;

    // Player 2
    public GameObject shieldPlayer2;
    public GameObject shieldBarPlayer2;
    public Button shieldActivateButtonPlayer2;
    public bool isShieldActivatedPlayer2;
    public int currentShieldCountPlayer2;

    void Start ()
    {
        shieldActivateButtonPlayer1.onClick.AddListener(ActivateShieldPlayer1);
        shieldActivateButtonPlayer2.onClick.AddListener(ActivateShieldPlayer2);
        shieldPlayer1.gameObject.SetActive(false);
        shieldPlayer2.gameObject.SetActive(false);
        isShieldActivatedPlayer1 = false;
        isShieldActivatedPlayer2 = false;
        currentShieldCountPlayer1 = MAX_SHIELD;
        currentShieldCountPlayer2 = MAX_SHIELD;
    }

    void Update ()
    {
        
    }

    public void ActivateShieldPlayer1()
    {
        if (currentShieldCountPlayer1 > 0)
        {
            currentShieldCountPlayer1 -= 1;
            shieldPlayer1.gameObject.SetActive(true);
            isShieldActivatedPlayer1 = true;
            shieldActivateButtonPlayer1.interactable = false;
            StartCoroutine(DeactivateShieldPlayer1());
        }
        else
        {
            currentShieldCountPlayer1 = MAX_SHIELD;
        }
    }
    
    public void ActivateShieldPlayer2()
    {
        if (currentShieldCountPlayer2 > 0)
        {
            currentShieldCountPlayer2 -= 1;
            shieldPlayer2.gameObject.SetActive(true);
            isShieldActivatedPlayer2 = true;
            shieldActivateButtonPlayer2.interactable = false;
            StartCoroutine(DeactivateShieldPlayer2());
        }
        else
        {
            currentShieldCountPlayer2 = MAX_SHIELD;
        }

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
