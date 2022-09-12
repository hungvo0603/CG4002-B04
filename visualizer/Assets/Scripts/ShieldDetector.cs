using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ShieldDetector : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI shieldDetectionText;
    public bool hasShieldEnemy;

    void Start()
    {
        hasShieldEnemy = false;
    }

    public void ShieldDetected()
    {
        shieldDetectionText.text = "SHIELD ACTIVATED";
        hasShieldEnemy = true;
    }

    public void ShieldLost()
    {
        shieldDetectionText.text = "SHIELD DEACTIVATED";
        hasShieldEnemy = false;
    }
    
}