using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AcidController : MonoBehaviour
{
    public GameObject standingAcid;
    public GameObject spilledAcid;
    public GameObject acidHole;
    public GameObject levelExit;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void Activate()
    {
        Invoke("SpillAcid", 0.1f);
    }

    private void SpillAcid()
    {
        spilledAcid.SetActive(true);
        standingAcid.SetActive(false);
        Invoke("MakeHole", 0.3f);
    }

    private void MakeHole()
    {
        spilledAcid.SetActive(false);
        acidHole.SetActive(true);
        levelExit.SetActive(true);
    }
}
