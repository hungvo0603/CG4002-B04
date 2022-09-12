using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GrenadeDisplay : MonoBehaviour
{
    public GameObject[] grenadePlayer1;
    [SerializeField] private GrenadeController grenades;

    const int MAX_GRENADE = 2;
    int index;

    // Start is called before the first frame update
    void Start()
    {
        index = 0;
    }

    // Update is called once per frame
    void Update()
    {
        index = grenades.player1Grenade;
        for (int i = 0; i < index; i++)
        {
            grenadePlayer1[i].gameObject.SetActive(true);
        }
        for (int i = index; i < MAX_GRENADE; i++)
        {
            grenadePlayer1[i].gameObject.SetActive(false);
        }
    }
}
