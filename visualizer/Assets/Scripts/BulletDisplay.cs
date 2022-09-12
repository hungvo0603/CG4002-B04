using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BulletDisplay : MonoBehaviour
{
    public GameObject[] bulletsPlayer1;
    [SerializeField] private ShootController gun;

    const int MAX_BULLET = 6;
    int index;
    // Start is called before the first frame update
    void Start()
    {
        index = 0;
    }

    // Update is called once per frame
    void Update()
    {
        index = gun.player1Bullet;
        for (int i = 0; i < index; i++) {
            bulletsPlayer1[i].gameObject.SetActive(true);
        }
        for (int i = index; i < MAX_BULLET; i++)
        {
            bulletsPlayer1[i].gameObject.SetActive(false);
        }
    }
}
