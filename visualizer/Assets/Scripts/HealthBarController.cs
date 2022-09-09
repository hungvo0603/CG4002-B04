using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class HealthBarController : MonoBehaviour
{
    public Slider slider;

    public void SetHealth(int health)
    {
        slider.value = health / 10;
    }
}
