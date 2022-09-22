using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class KDAController : MonoBehaviour
{
    private int player1KillStatistic;
    private int player2KillStatistic;
    [SerializeField] private TextMeshProUGUI player1KillText;
    [SerializeField] private TextMeshProUGUI player2KillText;
    [SerializeField] Player player;

    void Start()
    {
        player1KillStatistic = player.getPlayer1Kill();
        player2KillStatistic = player.getPlayer2Kill();
    }

    void Update()
    {
        player1KillStatistic = player.getPlayer1Kill();
        player1KillText.text = player1KillStatistic.ToString();

        player2KillStatistic = player.getPlayer2Kill();
        player2KillText.text = player2KillStatistic.ToString();
    }
}
