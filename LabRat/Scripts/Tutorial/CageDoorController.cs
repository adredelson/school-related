using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CageDoorController : MonoBehaviour
{
    public GameObject closedDoor;
    public GameObject openDoor;
    public Animator ratAnimator;

    private RatController _ratController;
    // Start is called before the first frame update
    void Start()
    {
        _ratController = ratAnimator.gameObject.GetComponent<RatController>();
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void OpenCage()
    {
        closedDoor.SetActive(false);
        openDoor.SetActive(true);
        Destroy(gameObject);
        _ratController.enabled = false;
        ratAnimator.SetTrigger("LeaveCage");
    }
}
