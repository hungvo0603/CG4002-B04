using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BulletDisplay : MonoBehaviour
{
    public GameObject[] bulletsPlayer1;
    public GameObject[] bulletsPlayer2;
    public GameObject bulletP1Canvas;
    public GameObject bulletP2Canvas;
    [SerializeField] private ShootController shootController;

    const int MAX_BULLET = 6;
    int index, index2;
    // Start is called before the first frame update
    void Start()
    {
        index = 0;
        index2 = 0;
    }

    // Update is called once per frame
    void Update()
    {
        if (bulletP1Canvas.activeSelf)
        {
            index = shootController.player1Bullet;
            for (int i = 0; i < index; i++) {
                bulletsPlayer1[i].gameObject.SetActive(true);
            }
            for (int i = index; i < MAX_BULLET; i++)
            {
                bulletsPlayer1[i].gameObject.SetActive(false);
            }            
        }

        if (bulletP2Canvas.activeSelf)
        {
            index2 = shootController.player2Bullet;
            for (int i = 0; i < index; i++) {
                bulletsPlayer2[i].gameObject.SetActive(true);
            }
            for (int i = index2; i < MAX_BULLET; i++)
            {
                bulletsPlayer2[i].gameObject.SetActive(false);
            }            
        }
    }

}
