using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ShieldDetector : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI shieldDetectionText;
    public bool hasShieldEnemy;
    [SerializeField] private ShieldController sc;
    private bool _isShieldActivatedPlayer2;

    void Start()
    {
        hasShieldEnemy = false;
        _isShieldActivatedPlayer2 = sc.isShieldActivatedPlayer2;
    }

    void Update()
    {
        _isShieldActivatedPlayer2 = sc.isShieldActivatedPlayer2;
        ShieldDetected();
        StartCoroutine(DelayHalfSec());
    }

    public void ShieldDetected()
    {
        if (_isShieldActivatedPlayer2)
        {
            shieldDetectionText.text = "SHIELD ACTIVATED";
            hasShieldEnemy = true;
        }
        else
        {
            shieldDetectionText.text = "SHIELD NOT ACTIVATED";
            hasShieldEnemy = false;
        }
    }

    public void ShieldLost()
    {
        shieldDetectionText.text = "SHIELD NOT ACTIVATED";
        hasShieldEnemy = false;
    }

    IEnumerator DelayHalfSec()
    {
        yield return new WaitForSeconds(.5f);
    }
    
}