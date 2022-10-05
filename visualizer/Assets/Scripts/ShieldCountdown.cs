using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ShieldCountdown : MonoBehaviour
{
    [SerializeField] private ShieldController shieldController;

    // Constants
    const int SHIELD_TIME = 10;

    // Player 1 Shield Statistics
    [SerializeField] private TextMeshProUGUI timerTextPlayer1;
    public Image TimerCounterPlayer1;
    float sliderValuePlayer1;
    bool _isShieldActivatedPlayer1;

    void Start()
    {
        sliderValuePlayer1 = 0;
        timerTextPlayer1.text = "READY";
    }

    // Update is called once per frame
    void Update()
    {
        // Player 1
        _isShieldActivatedPlayer1 = shieldController.isShieldActivatedPlayer1;
        
        if (_isShieldActivatedPlayer1)
        {
            if (sliderValuePlayer1 == 0)
            {
                sliderValuePlayer1 = SHIELD_TIME;
            }

            if (sliderValuePlayer1 > 0)
            {
                sliderValuePlayer1 -= Time.deltaTime;
                timerTextPlayer1.text = ((int)Mathf.Ceil(sliderValuePlayer1)).ToString();
                TimerCounterPlayer1.fillAmount = sliderValuePlayer1 / SHIELD_TIME;
            }
        } 
        else 
        {
            sliderValuePlayer1 = 0;
        }

        if (sliderValuePlayer1 == 0 && !_isShieldActivatedPlayer1)
        {
            timerTextPlayer1.text = "READY";
            TimerCounterPlayer1.fillAmount = 1;
        }

    }

}