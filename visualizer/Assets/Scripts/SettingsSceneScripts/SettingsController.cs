using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class SettingsController : MonoBehaviour
{
    enum PLAYER
    {
        NONE, PLAYER_1, PLAYER_2
    };
    
    public Button player1Button, player2Button;
    public SceneChanger sceneChanger;
    [SerializeField] private TextMeshProUGUI settingText;
    public static int REGISTERED_PLAYER;

    void Start()
    {
        player1Button.onClick.AddListener(OnPlayer1Chosen);
        player2Button.onClick.AddListener(OnPlayer2Chosen);
        REGISTERED_PLAYER = (int)PLAYER.NONE;
        settingText.text = "Choose your side ...";
    }

    public void OnPlayer1Chosen() 
    {
        settingText.text = "Get Ready, Player 1";
        StartCoroutine(ShowLoadingMessage());
        REGISTERED_PLAYER = (int)PLAYER.PLAYER_1;
        Debug.Log(REGISTERED_PLAYER);
    }

    public void OnPlayer2Chosen()
    {
        settingText.text = "Get Ready, Player 2";
        StartCoroutine(ShowLoadingMessage());
        REGISTERED_PLAYER = (int)PLAYER.PLAYER_2;
        Debug.Log(REGISTERED_PLAYER);
    }

    IEnumerator ShowLoadingMessage()
    {
        yield return new WaitForSeconds(1f);
        settingText.text = "Loading gameplay ...";
        StartCoroutine(ChangeToMainScene());
    }

    IEnumerator ChangeToMainScene()
    {
        yield return new WaitForSeconds(1f);
        sceneChanger.ChangeScene("MainScene");
    }
}
