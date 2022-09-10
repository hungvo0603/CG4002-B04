using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ShieldCountdown : MonoBehaviour
{
    const int SHIELD_TIME = 10;
    const int MAX_SHIELD = 3;
    public Image TimerCounter;
    [SerializeField] private TextMeshProUGUI timerText;
    public int currentShieldCount;
    float currentValue;
    bool isShieldActivated;

    public Button shieldLoad;

    void Start()
    {
        shieldLoad.onClick.AddListener(ActivateShield);
        currentShieldCount = MAX_SHIELD;
        isShieldActivated = false;
        currentValue = 0;
        timerText.text = MAX_SHIELD.ToString();
    }

    // Update is called once per frame
    void Update()
    {
        if (isShieldActivated)
        {
            if (currentValue > 0)
            {
                currentValue -= Time.deltaTime;
                timerText.text = ((int)Mathf.Ceil(currentValue)).ToString();
                TimerCounter.fillAmount = currentValue / SHIELD_TIME;
            }
            else
            {
                currentValue = 0;
                isShieldActivated = false;
                currentShieldCount = (currentShieldCount > 0) ? currentShieldCount - 1 : MAX_SHIELD;
            }
        }

        if (currentValue == 0 && !isShieldActivated)
        {
            timerText.text = "READY";
            TimerCounter.fillAmount = 1;
        }
    }

    void ActivateShield()
    {
        if (currentShieldCount > 0) {
            isShieldActivated = true;
            currentValue = SHIELD_TIME;
        } else {
            currentShieldCount = MAX_SHIELD;
        }
    }

}