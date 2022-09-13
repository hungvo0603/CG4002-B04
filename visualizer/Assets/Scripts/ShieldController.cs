using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ShieldController : MonoBehaviour
{
    public GameObject shieldPlayer2;
    public Button shieldActivateButtonPlayer2;
    public bool isShieldActivatedPlayer2;

    public Slider shieldBarSlider;
    public Image fill;

    void Start ()
    {
        shieldActivateButtonPlayer2.onClick.AddListener(ActivateShieldPlayer2);
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

    public void SetShieldHealth(int shieldHealth)
    {
        shieldBarSlider.value = shieldHealth / 10;
    }

}
