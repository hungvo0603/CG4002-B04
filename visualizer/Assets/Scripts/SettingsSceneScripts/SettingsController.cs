using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class SettingsController : MonoBehaviour
{
    public Button player1Button, player2Button;
    public SceneChanger sceneChanger;
    [SerializeField] private TextMeshProUGUI settingText;

    void Start()
    {
        player1Button.onClick.AddListener(OnPlayer1Chosen);
        player2Button.onClick.AddListener(OnPlayer2Chosen);
        settingText.text = "Choose your side ...";
    }

    public void OnPlayer1Chosen() 
    {
        settingText.text = "Get Ready, Player 1";
        StartCoroutine(ShowLoadingMessage());
        // sceneChanger.ChangeScene("MainScene");
    }

    public void OnPlayer2Chosen()
    {
        settingText.text = "Get Ready, Player 2";
        StartCoroutine(ShowLoadingMessage());
        // settingText.text = "Loading gameplay ...";
        // StartCoroutine(ShowLoadingMessage());
        // sceneChanger.ChangeScene("MainScene");
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
