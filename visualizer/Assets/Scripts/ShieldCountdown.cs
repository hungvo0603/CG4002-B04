using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ShieldCountdown : MonoBehaviour
{
    // Constants
    const int SHIELD_TIME = 10;
    const int MAX_SHIELD = 3;

    // Player 1 Shield Statistics
    [SerializeField] private TextMeshProUGUI timerTextPlayer1;
    public Image TimerCounterPlayer1;
    public int currentShieldCountPlayer1;
    float sliderValuePlayer1;
    bool isShieldActivatedPlayer1;

    // Player 2 Shield Statistics
    // [SerializeField] private TextMeshProUGUI timerTextPlayer2;
    // public Image TimerCounterPlayer2;
    // int currentShieldCountPlayer2;
    // float sliderValuePlayer2;
    // bool isShieldActivatedPlayer2;

    // Testing purpose
    public Button shieldLoadPlayer1;
    // public Button shieldLoadPlayer2;

    void Start()
    {
        shieldLoadPlayer1.onClick.AddListener(ActivateShieldPlayer1);
        currentShieldCountPlayer1 = MAX_SHIELD;
        isShieldActivatedPlayer1 = false;
        sliderValuePlayer1 = 0;
        timerTextPlayer1.text = "READY";

        // shieldLoadPlayer2.onClick.AddListener(ActivateShieldPlayer2);
        // currentShieldCountPlayer2 = MAX_SHIELD;
        // isShieldActivatedPlayer2 = false;
        // sliderValuePlayer2 = 0;
        // timerTextPlayer2.text = "READY";
    }

    // Update is called once per frame
    void Update()
    {
        // Player 1
        if (isShieldActivatedPlayer1)
        {
            if (sliderValuePlayer1 > 0)
            {
                sliderValuePlayer1 -= Time.deltaTime;
                timerTextPlayer1.text = ((int)Mathf.Ceil(sliderValuePlayer1)).ToString();
                TimerCounterPlayer1.fillAmount = sliderValuePlayer1 / SHIELD_TIME;
            }
            else
            {
                sliderValuePlayer1 = 0;
                isShieldActivatedPlayer1 = false;
            }
        }

        if (sliderValuePlayer1 == 0 && !isShieldActivatedPlayer1)
        {
            timerTextPlayer1.text = "READY";
            TimerCounterPlayer1.fillAmount = 1;
        }

        // Player 2
        // if (isShieldActivatedPlayer2)
        // {
        //     if (sliderValuePlayer2 > 0)
        //     {
        //         sliderValuePlayer2 -= Time.deltaTime;
        //         timerTextPlayer2.text = ((int)Mathf.Ceil(sliderValuePlayer2)).ToString();
        //         TimerCounterPlayer2.fillAmount = sliderValuePlayer2 / SHIELD_TIME;
        //     }
        //     else
        //     {
        //         sliderValuePlayer2 = 0;
        //         isShieldActivatedPlayer2 = false;
        //     }
        // }

        // if (sliderValuePlayer2 == 0 && !isShieldActivatedPlayer2)
        // {
        //     timerTextPlayer2.text = "READY";
        //     TimerCounterPlayer2.fillAmount = 1;
        // }
    }

    void ActivateShieldPlayer1()
    {
        if (currentShieldCountPlayer1 > 0) {
            currentShieldCountPlayer1 -= 1;
            isShieldActivatedPlayer1 = true;
            sliderValuePlayer1 = SHIELD_TIME;
        } else {
            currentShieldCountPlayer1 = MAX_SHIELD;
        }
    }

    // void ActivateShieldPlayer2()
    // {
    //     if (currentShieldCountPlayer2 > 0) {
    //         currentShieldCountPlayer2 -= 1;
    //         isShieldActivatedPlayer2 = true;
    //         sliderValuePlayer2 = SHIELD_TIME;
    //     } else {
    //         currentShieldCountPlayer2 = MAX_SHIELD;
    //     }
    // }

}