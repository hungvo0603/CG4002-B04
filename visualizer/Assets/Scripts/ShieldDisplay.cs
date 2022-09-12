using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ShieldDisplay : MonoBehaviour
{
    public GameObject[] shieldsPlayer1;

    const int MAX_SHIELD = 3;
    [SerializeField] private ShieldCountdown sc;
    int index1;
    // Start is called before the first frame update
    void Start()
    {
        index1 = 0;
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
    }
}
