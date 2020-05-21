using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class InteractiveObject : MonoBehaviour
{
    public Material outlineMat;

    private Material _defaultMat;
    private SpriteRenderer _renderer;
    private string _originalTag;
    // Start is called before the first frame update
    void Start()
    {
        _renderer = gameObject.GetComponent<SpriteRenderer>();
        _defaultMat = _renderer.material;
        _originalTag = tag;
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    private void OnTriggerEnter2D(Collider2D collision)
    {
        if (collision.CompareTag(GameManager.TELEKINESIS_TAG))
        {
            tag = "Untagged";
        }
        else if (collision.CompareTag("AreaOfInfluence") && IsInteractive())
        {
            SetOutline(true);
        }
    }

    private void OnTriggerExit2D(Collider2D collision)
    {
        if (collision.CompareTag(GameManager.TELEKINESIS_TAG))
        {
            tag = _originalTag;
        }
        SetOutline(false);
    }

    public void SetOutline(bool on)
    {
        if (on)
        {
            _renderer.material = outlineMat;
        }
        else
        {
            _renderer.material = _defaultMat;
        }
    }

    private bool IsInteractive()
    {
        return tag.Equals(GameManager.MOVABLE_OBJECT_TAG) || tag.Equals(GameManager.SCRIPTED_OBJECT_TAG)
            || tag.Equals(GameManager.ANIMATED_OBJECT_TAG) || tag.Equals(GameManager.INTERACTIVE_OBJECT_TAG);
    }
}
