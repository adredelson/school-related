using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RatFall : MonoBehaviour
{
    public Transform rat;
    public float targetY;
    public float speed;

    private bool _startFall = false;
    // Start is called before the first frame update
    void Start()
    {
        rat.gameObject.SetActive(false);
        Invoke("StartFall", 1.5f);
    }

    // Update is called once per frame
    void Update()
    {
        if (rat.position.y > targetY && _startFall)
        {
            rat.Translate(new Vector3(0, -0.5f, 0)*Time.deltaTime*speed);
        }
    }

    private void StartFall()
    {
        rat.gameObject.SetActive(true);
        _startFall = true;
    }
}
