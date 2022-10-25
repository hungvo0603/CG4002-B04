using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class StartSceneController : MonoBehaviour
{
    public Button startButton, exitButton;
    public SceneChanger sceneChanger;

    public TriggerAnimatorButtons tButtons;
    public TriggerAnimatorTitle tTitle;

    void Start() 
    {
        startButton.onClick.AddListener(changeToSettingsScene);
        exitButton.onClick.AddListener(exitGame);
    }

    public void changeToSettingsScene() 
    {
        tTitle.TriggerAnimation();
        tButtons.TriggerAnimation();
        StartCoroutine(ChangeScene());
    } 

    public void exitGame()
    {
        sceneChanger.Exit();
    }

    IEnumerator ChangeScene()
    {
        yield return new WaitForSeconds(0.5f);
        sceneChanger.ChangeScene("SettingsScene");
    }
}
