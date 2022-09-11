using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ShieldDisplay : MonoBehaviour
{
    public GameObject[] shieldsPlayer1;
    // public GameObject[] shieldsPlayer2;

    const int MAX_SHIELD = 3;
    [SerializeField] private ShieldCountdown sc;
    int index1;
    // int index2;
    // Start is called before the first frame update
    void Start()
    {
        index1 = 0;
        // index2 = MAX_SHIELD;
    }

    // Update is called once per frame
    void Update()
    {
        index1 = sc.currentShieldCountPlayer1;
        for (int i = 0; i < index1; i++) 
        {
            shieldsPlayer1[i].gameObject.SetActive(true);
        }
        for (int i = index1; i < MAX_SHIELD; i++)
        {
            shieldsPlayer1[i].gameObject.SetActive(false);
        }

        // index2 = sc.getCurrentShieldCount(2);
        // UpdateShieldDisplay(index2, 2);
    }

    // void UpdateShieldDisplay(int index, int playerNumber) 
    // {
        // if (playerNumber == 1)
        // {
        // for (int i = 0; i < index; i++) 
        // {
        //     shieldsPlayer1[i].gameObject.SetActive(true);
        // }
        // for (int i = index; i < MAX_SHIELD; i++)
        // {
        //     shieldsPlayer1[i].gameObject.SetActive(false);
        // }
        // }
        // else if (playerNumber == 2)
        // {
        //     for (int i = 0; i < index; i++) 
        //     {
        //         shieldsPlayer2[i].gameObject.SetActive(true);
        //     }
        //     for (int i = index; i < MAX_SHIELD; i++)
        //     {
        //         shieldsPlayer2[i].gameObject.SetActive(false);
        //     }
        // }
    // }
}
