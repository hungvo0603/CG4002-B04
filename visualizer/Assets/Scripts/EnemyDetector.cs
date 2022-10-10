using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class EnemyDetector : MonoBehaviour
{
    // [SerializeField] private TextMeshProUGUI enemyDetectionText;
    public bool hasEnemy;

    void Start()
    {
        hasEnemy = false;
    }
    
    public void EnemyDetected()
    {
        // enemyDetectionText.text = "ENEMY DETECTED";
        hasEnemy = true;
    }

    public void EnemyLost()
    {
        // enemyDetectionText.text = "ENEMY LOST";
        hasEnemy = false;
    }
    
}
