using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class EnemyDetector : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI enemyDetectionText;
    
    public void EnemyDetected()
    {
        enemyDetectionText.text = "ENEMY DETECTED";
    }

    public void EnemyLost()
    {
        enemyDetectionText.text = "ENEMY LOST";
    }
    
}
