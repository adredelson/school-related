using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FlushController : MonoBehaviour
{

    
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

	private void OnTriggerEnter2D(Collider2D collision)
	{
		GameObject collisionObject = collision.gameObject;
		if (collisionObject.name == "Rat" || collisionObject.name == "Fish")
		{
            gameObject.GetComponent<AudioSource>().Play();
		}

	}
}
