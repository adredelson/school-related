using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class CameraScript : MonoBehaviour


{
    public Transform playerTransform;
    public bool sewerScene = false;

    [SerializeField]
    public float leftLimit;
    [SerializeField]
    public float rightLimit;


    private float DESIGN_WIDTH = 1920f;
    private float DESIGN_HEIGHT = 1080f;

    //private bool leftFrame = false;
    //private bool rightFrame = false;
    ////private bool endFrame;
    ////private const string BACKGROUND = "Background";

    // Start is called before the first frame update
    void Start()
    {
        // Set resolution
        float windowAspect = (float)Screen.width / (float)Screen.height;
        float targetAspect = DESIGN_WIDTH / DESIGN_HEIGHT;
        float scaleHeight = windowAspect / targetAspect;

        if (windowAspect < targetAspect)
        {
            Camera.main.orthographicSize = (DESIGN_HEIGHT / 200f) / scaleHeight;
        }
        else
        {
            Camera.main.orthographicSize = DESIGN_HEIGHT / 200f;
        }

    }

    // Update is called once per frame
    void Update()
    {
        Vector3 temp = transform.position;
        if (sewerScene)
            leftLimit = transform.position.x;
        temp.x = Mathf.Clamp(playerTransform.position.x, leftLimit, rightLimit);

        transform.position = temp;
    }

    
}
