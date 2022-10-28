using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ShieldDetector : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI shieldDetectionText;
    public bool hasShieldEnemy;
    [SerializeField] private ShieldController shieldController;
    private bool _isShieldActivatedPlayer2;

    void Start()
    {
        hasShieldEnemy = false;
        _isShieldActivatedPlayer2 = shieldController.isShieldActivatedPlayer2;
    }

    void Update()
    {
        _isShieldActivatedPlayer2 = shieldController.isShieldActivatedPlayer2;
        ShieldDetected();
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
        shieldDetectionText.text = "SHIELD LOST";
        hasShieldEnemy = false;
    }
    
}