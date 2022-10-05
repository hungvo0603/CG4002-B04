using System.Collections;
using System.Collections.Generic;
using UnityEngine;


[System.Serializable]
public class PlayerDataJson
{
    public PlayerStatsJson p1;
    public PlayerStatsJson p2;
    public string sender;

    public static PlayerDataJson CreateDataFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<PlayerDataJson>(jsonString);
    }
}

[System.Serializable]
public class PlayerStatsJson
{
    [Header("Player Statistics")]
    public int hp;
    public string action;
    public int bullets;
    public int grenades;
    public float shield_time;
    public int shield_health;
    public int num_deaths;
    public int num_shield;    
}
