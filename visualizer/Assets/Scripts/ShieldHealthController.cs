using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ShieldHealthController : MonoBehaviour
{
    [SerializeField] private Button shieldPlayer1Button;
    [SerializeField] private Button shieldPlayer2Button;
    [SerializeField] private ShieldController shieldController;
    private bool _isShieldActivatedPlayer1;
    private bool _isShieldActivatedPlayer2;

    public Slider shieldBarSliderPlayer1;
    public Slider shieldBarSliderPlayer2;

    [SerializeField] private Image fillShieldPlayer1;
    [SerializeField] private Image fillShieldPlayer2;

    public Color activateColor;
    public Color inactivateColor;

    int currentShieldHealthPlayer1;
    int currentShieldHealthPlayer2;

    private const int MAX_SHIELD_HEALTH = 30;

    void Start()
    {
        shieldPlayer1Button.onClick.AddListener(InitShieldHealthPlayer1);
        shieldPlayer2Button.onClick.AddListener(InitShieldHealthPlayer2);
        activateColor.a = 1;
        inactivateColor.a = 1;
        fillShieldPlayer1.color = inactivateColor;
        fillShieldPlayer2.color = inactivateColor;
        currentShieldHealthPlayer1 = 0;
        currentShieldHealthPlayer2 = 0;
        _isShieldActivatedPlayer1 = shieldController.isShieldActivatedPlayer1;
        _isShieldActivatedPlayer2 = shieldController.isShieldActivatedPlayer2;
    }

    void Update()
    {
        ColorUpdate();
    }

    void ColorUpdate() 
    {
        _isShieldActivatedPlayer1 = shieldController.isShieldActivatedPlayer1;
        _isShieldActivatedPlayer2 = shieldController.isShieldActivatedPlayer2;
        if (_isShieldActivatedPlayer1)
        {
            fillShieldPlayer1.color = activateColor;
        }
        else
        {
            fillShieldPlayer1.color = inactivateColor;
        }

        if (_isShieldActivatedPlayer2)
        {
            fillShieldPlayer2.color = activateColor;
        }
        else
        {
            fillShieldPlayer2.color = inactivateColor;
        }
    }

    void InitShieldHealthPlayer1()
    {
        currentShieldHealthPlayer1 = MAX_SHIELD_HEALTH;
        SetShieldHealthPlayer1(currentShieldHealthPlayer1);
    }

    void InitShieldHealthPlayer2()
    {
        currentShieldHealthPlayer2 = MAX_SHIELD_HEALTH;
        SetShieldHealthPlayer2(currentShieldHealthPlayer2);
    }

    void SetShieldHealthPlayer1(int shieldHealth)
    {
        shieldBarSliderPlayer1.value = shieldHealth / 10;
    }

    void SetShieldHealthPlayer2(int shieldHealth)
    {
        shieldBarSliderPlayer2.value = shieldHealth / 10;
    }
}
