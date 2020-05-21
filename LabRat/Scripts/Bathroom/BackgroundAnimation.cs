using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BackgroundAnimation : MonoBehaviour
{

    public Animator anim;
    public float timeToStart;
    public float timeToRepeat;

    private bool on = false;

    // Start is called before the first frame update
    void Start()
    {
        InvokeRepeating("Animate", timeToStart, timeToRepeat);
     
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void Animate()
    {
        on = !on;
        anim.SetBool("On", on);
    }
}
