using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ShieldTriggerAnimation : MonoBehaviour
{
    // Start is called before the first frame update
    // [SerializeField] private Button loadShield;
    public Button loadShield;
    [SerializeField] private Image shieldLayer;
    private bool _isBrokenShield; // for later

    void Start()
    {
        loadShield.onClick.AddListener(TriggerAnimation);
        shieldLayer.gameObject.SetActive(false);
        _isBrokenShield = false;
    }

    // Update is called once per frame
    void Update()
    {
        shieldLayer.gameObject.SetActive(!_isBrokenShield);
    }

    void TriggerAnimation()
    {
        shieldLayer.gameObject.SetActive(true);
        GetComponent<Animator>().Play("ShieldFlashing");
        StartCoroutine(DeactivateShieldPlayer1());
    }

    IEnumerator DeactivateShieldPlayer1()
    {
        yield return new WaitForSeconds(10f);
        shieldLayer.gameObject.SetActive(false);
    }
}
