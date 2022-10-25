using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TriggerAnimatorButtons : MonoBehaviour
{
    // Start is called before the first frame update
    public void TriggerAnimation()
    {
        GetComponent<Animator>().Play("ControlButtons");
    }
}
