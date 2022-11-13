using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ScoreboardManager : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI player1Kill;
    [SerializeField] private TextMeshProUGUI player2Kill;
    [SerializeField] private TextMeshProUGUI scoreboardHeader;
    public AudioSource victorySound;
    public AudioSource defeatSound;

    void Start()
    {
        player1Kill.text = Player.player1KillStatistic.ToString();
        player2Kill.text = Player.player2KillStatistic.ToString();
        if (SettingsController.REGISTERED_PLAYER == 1)
        {
            if (Player.player1KillStatistic > Player.player2KillStatistic)
            {
                scoreboardHeader.text = "VICTORY";
                victorySound.Play();
            }
            else if (Player.player1KillStatistic < Player.player2KillStatistic)
            {
                scoreboardHeader.text = "DEFEAT";
                defeatSound.Play();
            }
            else
            {
                scoreboardHeader.text = "DRAW";
            }
        }
        else if (SettingsController.REGISTERED_PLAYER == 2)
        {
            if (Player.player1KillStatistic < Player.player2KillStatistic)
            {
                scoreboardHeader.text = "VICTORY";
                victorySound.Play();
            }
            else if (Player.player1KillStatistic > Player.player2KillStatistic)
            {
                scoreboardHeader.text = "DEFEAT";
                defeatSound.Play();
            }
            else
            {
                scoreboardHeader.text = "DRAW";
            }
        }
    }

}
