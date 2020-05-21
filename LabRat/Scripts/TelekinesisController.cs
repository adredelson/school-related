using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TelekinesisController : MonoBehaviour
{

    public Transform telekinesisTransform;
    public GameObject objectHalo;
   


    //private const KeyCode SELECT_KEY = KeyCode.Space;

    private GameObject inRangeObject;
    private GameObject selectedObject = null;
    public Animator ratAnimation;

    // Start is called before the first frame update
    void Start()
    {
        //ratAnimation = gameObject.GetComponent<Animator>();
    }

    // Update is called once per frame
    void Update()
    {
        if(Input.GetKeyDown(GameManager.SELECT_KEY))
        {
            
            if (selectedObject != null)
                releaseObject();
            else if (selectedObject == null && inRangeObject != null)
            {
                StartCoroutine(ToggleAnimation(true, 0));
                if (inRangeObject.CompareTag(GameManager.ANIMATED_OBJECT_TAG))
                {
                    AnimatedObject anim = inRangeObject.GetComponent<AnimatedObject>();
                    anim.Invoke("ActivateAnimation", 0.3f);
                    StartCoroutine(ToggleAnimation(false, 0.05f));
                }

                else if (inRangeObject.CompareTag(GameManager.SCRIPTED_OBJECT_TAG))
                {
                    ScriptedObject scrpt = inRangeObject.GetComponent<ScriptedObject>();
                    scrpt.runScript();
                    StartCoroutine(ToggleAnimation(false, 0.1f));
                }

                else if(inRangeObject.CompareTag(GameManager.MOVABLE_OBJECT_TAG))
                    selectObject();
            }
        }
  
    }

    private IEnumerator ToggleAnimation(bool active, float delay)
    {
        yield return new WaitForSeconds(delay);
        ratAnimation.SetBool("Telekinesis", active);
    }
  
    private void releaseObject()
    {
        gameObject.tag = "AreaOfInfluence";
        selectedObject.GetComponent<MovableObject>().Release();
        objectHalo.SetActive(false);
        objectHalo.transform.SetParent(transform);
        selectedObject.tag = GameManager.MOVABLE_OBJECT_TAG;
        inRangeObject = selectedObject;
        selectedObject = null;
        StartCoroutine(ToggleAnimation(false, 0.1f));

    }

    private void selectObject()
    {
        gameObject.tag = "Untagged";
        selectedObject = inRangeObject;
        objectHalo.SetActive(true);
        objectHalo.transform.position = selectedObject.transform.position;
        objectHalo.transform.SetParent(selectedObject.transform);
        selectedObject.GetComponent<MovableObject>().Grab(transform);
        selectedObject.tag = GameManager.TELEKINESIS_TAG;

    }

    private void OnTriggerEnter2D(Collider2D collision)
    {
        GameObject collisionObject = collision.gameObject;
        if (collidedWithInteractive(collisionObject))
        {
            //gameObject.tag = "Untagged";
            inRangeObject = collisionObject;
        }
    }

    private void OnTriggerStay2D(Collider2D collision)
    {
        GameObject collisionObject = collision.gameObject;
        if (inRangeObject == null && collidedWithInteractive(collisionObject))
        {
            inRangeObject = collisionObject;
        }
    }

    private void OnTriggerExit2D(Collider2D collision)
    {
        
        GameObject collisionObject = collision.gameObject;
        if (collidedWithInteractive(collisionObject))
        {
            //gameObject.tag = "AreaOfInfluence";
            if (inRangeObject.name == collisionObject.name)
            {
                inRangeObject = null;
            }
        }
    }

    private bool collidedWithInteractive(GameObject collision)
    {
        return collision.CompareTag(GameManager.MOVABLE_OBJECT_TAG) ||
            collision.CompareTag(GameManager.SCRIPTED_OBJECT_TAG) ||
            collision.CompareTag(GameManager.ANIMATED_OBJECT_TAG);
    }

}
