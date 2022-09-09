using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class StatisticsManager : MonoBehaviour
{
    private const int MAX_HEALTH = 100;

    [SerializeField] private TextMeshProUGUI player1HealthText;

    int player1Health = 100;

    void Start()
    {
        player1HealthText.text = "100%";
    }

    public void HealthDownButtonPress() 
    {
        player1Health = (player1Health > 0) ? (player1Health - 10) : MAX_HEALTH;
        player1HealthText.text = player1Health.ToString() + "%";
    }
}
