using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AnimatedObject : MonoBehaviour
{

    private Animator _animator;
    private InteractiveObject _halo;
    private Collider2D _collider;
    
    // Start is called before the first frame update
    void Start()
    {
        _animator = gameObject.GetComponent<Animator>();
        _halo = gameObject.GetComponent<InteractiveObject>();
        _collider = gameObject.GetComponent<Collider2D>();
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void ActivateAnimation()
    {
        _animator.SetBool("On", true);
        _halo.SetOutline(false);
        _collider.enabled = false;
        gameObject.tag = GameManager.TELEKINESIS_TAG;
        Invoke("StopAnimation", 4);
    }

    private void StopAnimation()
    {
        _animator.SetBool("On", false);
        gameObject.tag = GameManager.ANIMATED_OBJECT_TAG;
        _collider.enabled = true;
    }
}
