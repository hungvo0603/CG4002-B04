using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class SceneChanger : MonoBehaviour
{
    public Animator transition;

    public void ChangeScene ()
    {
        StartCoroutine(StartTransition(SceneManager.GetActiveScene().buildIndex + 1));
    }

    IEnumerator StartTransition(int levelIndex)
    {
        transition.SetTrigger("Start");
        yield return new WaitForSeconds(1f);
        SceneManager.LoadScene(levelIndex);
    }

    public void Exit()
    {
        Application.Quit();
    }
}