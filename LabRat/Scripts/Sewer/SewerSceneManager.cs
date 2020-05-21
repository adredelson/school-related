using System;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class SewerSceneManager : MonoBehaviour
{

    public GameObject[] monstersPrefab;
    public float timeBetweenMonsters;
    public int numberOfStartMonsters;
    public GameObject RatClimb;
    public GameObject transofrmation;
    public GameObject rat;
    public GameObject camera;
    public GameObject black;
    public GameObject backgroundMusic;

    private System.Random rnd = new System.Random();

    // Start is called before the first frame update
    void Start()
    {
      
    }


    public void StartScene()
    {
        camera.GetComponent<Transform>().position = new Vector3(0, 0,-20);
        camera.GetComponent<CameraScript>().enabled = true;
        transofrmation.GetComponent<Animator>().SetTrigger("On");
        backgroundMusic.SetActive(true);
        Invoke("startGame", 5f);

    }


    private void startGame()
    {
        transofrmation.SetActive(false);
        black.SetActive(false);
        rat.SetActive(true);

        Invoke("MonsterFactory", 5f);
    }


    // Update is called once per frame
    void Update()
    {
    

    }


    private void MonsterFactory()
    {
        for (int i = 0; i < numberOfStartMonsters; i++)
            Invoke("CreateMonster", i * 2);
        InvokeRepeating("CreateMonster", 10f, timeBetweenMonsters * 2);
        InvokeRepeating("CreateMonster", 35f, timeBetweenMonsters * 2);
    }

    void CreateMonster()
    {
        
        int index = rnd.Next(0, 3);
        bool isLeft = (UnityEngine.Random.value > 0.5f);

        //first few come from right only
        isLeft = numberOfStartMonsters <= 0 ? isLeft : false;
        float x = isLeft?0:1.1f;
        float y = 0f;
      
        Vector3 v3Pos = Camera.main.ViewportToWorldPoint(new Vector3(x, y));



       GameObject monster = Instantiate(monstersPrefab[index], v3Pos, Quaternion.identity);

       monster.GetComponent<MonsterController>().left = isLeft;
        if (numberOfStartMonsters > 0)
            monster.GetComponent<MonsterController>().speed = 2f;

        numberOfStartMonsters--;
   

    }

    public void endScene()
    {
        //RatClimb.SetActive(true);
        //RatClimb.GetComponent<Animator>().SetTrigger("On");
        //Time.timeScale = 0;
        Invoke("EndGame", 2.4f);
        
    }

    private void EndGame()
    {
        GameManager.Instance.NextLevel();
    }

}
