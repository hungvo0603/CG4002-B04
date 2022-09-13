using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ShieldHealthController : MonoBehaviour
{
    [SerializeField] private Button shieldPlayer1Button;
    [SerializeField] private Button shieldPlayer2Button;
    [SerializeField] private ShieldController shieldController;
    private const int MAX_SHIELD_HEALTH = 30;
    int shieldHealthPlayer1, shieldHealthPlayer2;

    void Start()
    {
        shieldPlayer1Button.onClick.AddListener(InitShieldHealthPlayer1);
        shieldPlayer2Button.onClick.AddListener(InitShieldHealthPlayer2);
        shieldHealthPlayer1 = 0;
        shieldHealthPlayer2 = 0;
        shieldController.SetShieldHealth(0);
    }

    void InitShieldHealthPlayer1()
    {
        shieldHealthPlayer1 = MAX_SHIELD_HEALTH;
        shieldController.SetShieldHealth(shieldHealthPlayer1);
    }

    void InitShieldHealthPlayer2()
    {
        shieldHealthPlayer2 = MAX_SHIELD_HEALTH;
        shieldController.SetShieldHealth(shieldHealthPlayer2);
    }
}
