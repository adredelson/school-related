using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

public class ScriptedObject : MonoBehaviour
{

	public UnityEvent script;

	// Start is called before the first frame update
	void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void runScript()
	{
		script.Invoke();
	}


}
