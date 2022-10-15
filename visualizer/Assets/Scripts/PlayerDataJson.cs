using System.Collections;
using System.Collections.Generic;
using UnityEngine;


[System.Serializable]
public class PlayerDataJson
{
    public PlayerStatsJson p1;
    public PlayerStatsJson p2;

    public static PlayerDataJson CreateDataFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<PlayerDataJson>(jsonString);
    }
}

[System.Serializable]
public class PlayerStatsJson
{
    public int hp;
    public string action;
    public int bullets;
    public int grenades;
    public float shield_time;
    public int shield_health;
    public int num_deaths;
    public int num_shield;    
}

// [System.Serializable]
// public class GrenadeHitJson
// {
//     public string grenadeHit;

//     public static GrenadeHitJson CreateHitDataFromJSON(string jsonString)
//     {
//         return JsonUtility.FromJson<GrenadeHitJson>(jsonString);
//     }
// }
