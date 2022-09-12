using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ShieldDetector : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI shieldDetectionText;

    public void ShieldDetected()
    {
        shieldDetectionText.text = "SHIELD ACTIVATED";
    }

    public void ShieldLost()
    {
        shieldDetectionText.text = "SHIELD DEACTIVATED";
    }
    
}