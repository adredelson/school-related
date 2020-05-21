using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FishController : MonoBehaviour
{

    public GameObject openToilet;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (openToilet.active)
            gameObject.tag = GameManager.SCRIPTED_OBJECT_TAG;
    }
}
