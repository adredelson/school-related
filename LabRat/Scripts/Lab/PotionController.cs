using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PotionController : MonoBehaviour
{
    public float shrinkFactor;
    public Transform rat;
    public RatController ratController;
    public float newRatY;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void Shrink()
    {
        rat.localScale /= shrinkFactor;
        Vector3 ratPos = rat.localPosition;
        ratPos.Set(ratPos.x, newRatY, ratPos.z);
        rat.localPosition = ratPos;
        ratController.LowerSpeed(shrinkFactor);
        Invoke("Delete", 0.1f);
    }

    private void Delete()
    {
        Destroy(gameObject);
    }
}
