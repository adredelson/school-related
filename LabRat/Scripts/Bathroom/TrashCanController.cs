using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TrashCanController : MonoBehaviour
{
    //public Transform closedTrash;
    public float trashHeight;
    public GameObject openTrash;
    public GameObject closedCrack;
    public GameObject openCrack;
    public Animator ceilingPeice;
    public Animator mouseAnimator;
    public Transform mouseTransform;
    public GameObject openToilet;

    private Vector3 mouseOnTrash = new Vector3(1.79f, 2.38f);
    private Vector3 mousePos;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
            
    }


    public void playEndScene()
    {
        mousePos = mouseTransform.position;
        mouseTransform.position = mouseOnTrash;
        if (openToilet.active == false)
        {
            Invoke("MouseDown", 1.5f);
            mouseAnimator.SetTrigger("Jump");
        }
        else
        {
            Invoke("BreakCeiling", 1f);
            Invoke("OpenTrash", 2f);
        }

        //endScene();
    }

    private void MouseDown()
    {
        mouseTransform.position = mousePos;

    }

    private void BreakCeiling()
    {
        ceilingPeice.SetTrigger("Triggered");
        openCrack.SetActive(true);
        closedCrack.SetActive(false);
      
    }

    private void OpenTrash()
    {
        gameObject.SetActive(false);
        openTrash.SetActive(true);
        mouseAnimator.SetTrigger("trashOpen");
        Invoke("NextLevel", 3f);
    }

    public void NextLevel()
    {
        GameManager.Instance.NextLevel();
    }
}
