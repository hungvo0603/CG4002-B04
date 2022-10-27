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

    [SerializeField] private TextMeshProUGUI timerTextPlayer2;
    public Image TimerCounterPlayer2;
    float sliderValuePlayer2;
    bool _isShieldActivatedPlayer2;

    // float shieldTimerPlayer2;
    // public TextMeshProUGUI shieldCounterPlayer2Text;
    // bool _isShieldActivatedPlayer2;

    void Start()
    {
        sliderValuePlayer1 = 0;
        sliderValuePlayer2 = 0;
        timerTextPlayer1.text = "READY";
        timerTextPlayer2.text = "READY";

        // shieldTimerPlayer2 = SHIELD_TIME;
        // shieldCounterPlayer2Text.text = shieldTimerPlayer2.ToString();
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

        // Player 2
        _isShieldActivatedPlayer2 = shieldController.isShieldActivatedPlayer2;

        if (_isShieldActivatedPlayer2)
        {
            if (sliderValuePlayer2 == 0)
            {
                sliderValuePlayer2 = SHIELD_TIME;
            }

            if (sliderValuePlayer2 > 0)
            {
                sliderValuePlayer2 -= Time.deltaTime;
                timerTextPlayer2.text = ((int)Mathf.Ceil(sliderValuePlayer2)).ToString();
                TimerCounterPlayer2.fillAmount = sliderValuePlayer2 / SHIELD_TIME;
            }
        }
        else
        {
            sliderValuePlayer2 = 0;
        }

        if (sliderValuePlayer2 == 0 || !_isShieldActivatedPlayer2)
        {
            timerTextPlayer2.text = "READY";
            TimerCounterPlayer2.fillAmount = 1;
        }

    }

    public void SetShieldTime(float shieldTimeP1, float shieldTimeP2)
    {
        sliderValuePlayer1 = shieldTimeP1;
        sliderValuePlayer2 = shieldTimeP2;
    }

}