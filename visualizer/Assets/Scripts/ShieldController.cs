using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ShieldController : MonoBehaviour
{
    public GameObject shieldPlayer2;
    public Button shieldActivateButton;
    public bool isShieldActivatedPlayer2;

    void Start ()
    {
        shieldActivateButton.onClick.AddListener(ActivateShieldPlayer2);
        shieldPlayer2.gameObject.SetActive(false);
        isShieldActivatedPlayer2 = false;
    }
    
    public void ActivateShieldPlayer2()
    {
        shieldPlayer2.gameObject.SetActive(true);
        isShieldActivatedPlayer2 = true;
        StartCoroutine(DeactivateShieldPlayer2());
    }

    IEnumerator DeactivateShieldPlayer2()
    {
        yield return new WaitForSeconds(10f);
        shieldPlayer2.gameObject.SetActive(false);
        isShieldActivatedPlayer2 = false;
    }

}
