using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using TMPro;

public class ShootController : MonoBehaviour
{
    public GameObject shootButton;
    public UnityEvent onClick = new UnityEvent();

    private const int MAX_BULLET = 6;
    [SerializeField] private TextMeshProUGUI player1BulletText;

    int player1Bullet = 6;

    // Start is called before the first frame update
    void Start()
    {
        player1BulletText.text = "6/6";
        shootButton = this.gameObject;
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.touchCount > 0 && Input.GetTouch(0).phase == TouchPhase.Began) {
            player1Bullet = (player1Bullet > 0) ? (player1Bullet - 1) : MAX_BULLET;
            player1BulletText.text = player1Bullet.ToString() + "/6";
        }   
    }
}
