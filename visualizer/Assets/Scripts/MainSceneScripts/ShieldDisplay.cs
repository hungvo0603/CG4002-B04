using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ShieldDisplay : MonoBehaviour
{
    public GameObject[] shieldsPlayer1;
    public GameObject[] shieldsPlayer2;

    const int MAX_SHIELD = 3;
    [SerializeField] private ShieldController shieldController;
    int i1;
    int i2;
    // Start is called before the first frame update
    void Start()
    {
        i1 = 0;
        i2 = 0;
    }

    // Update is called once per frame
    void Update()
    {
        i1 = shieldController.currentShieldCountPlayer1;
        for (int i = 0; i < i1; i++) 
        {
            shieldsPlayer1[i].gameObject.SetActive(true);
        }
        for (int i = i1; i < MAX_SHIELD; i++)
        {
            shieldsPlayer1[i].gameObject.SetActive(false);
        }

        i2 = shieldController.currentShieldCountPlayer2;
        for (int i = 0; i < i2; i++)
        {
            shieldsPlayer2[i].gameObject.SetActive(true);
        }
        for (int i = i2; i < MAX_SHIELD; i++)
        {
            shieldsPlayer2[i].gameObject.SetActive(false);
        }
    }
}
