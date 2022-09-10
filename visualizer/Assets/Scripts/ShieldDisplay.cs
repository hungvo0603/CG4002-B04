using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ShieldDisplay : MonoBehaviour
{
    public GameObject[] shields;
    const int MAX_SHIELD = 3;
    [SerializeField] private ShieldCountdown sc1;
    int index;
    // Start is called before the first frame update
    void Start()
    {
        index = 0;
    }

    // Update is called once per frame
    void Update()
    {
        index = sc1.currentShieldCount;
        for (int i = 0; i < index; i++) 
        {
            shields[i].gameObject.SetActive(true);
        }
        for (int i = index; i < MAX_SHIELD; i++)
        {
            shields[i].gameObject.SetActive(false);
        }
    }
}
