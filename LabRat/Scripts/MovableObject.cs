using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

public class MovableObject : MonoBehaviour
{

    public string destColliderName;
    public UnityEvent inPlace;
    public UnityEvent hoveringInPlace;
    public UnityEvent leftPosition;
    public float liftHeight;
    public float destHeight;

    private Transform _target;
    private float _originalHeight;
    private bool _grabbed = false;
    private bool _lifted = false;
    private float _speed = 10f;
    private Vector3 _translationVec = Vector3.zero;
    private float _wobbleAmp = 0.5f;
    private float _targetDistance;
    private bool _overPosition = false;
    // Start is called before the first frame update
    void Start()
    {
        _target = transform;
        _originalHeight = transform.position.y;
    }

    // Update is called once per frame
    void Update()
    {
        if (_grabbed && !_lifted)
        {
            if (transform.position.y < liftHeight)
            {
                _translationVec.Set(0f, _speed, 0f);
                transform.Translate(_translationVec * Time.deltaTime);
            }
            else
            {
                _lifted = true;
            }
        }
        else if (_grabbed && _lifted)
        {
            Vector3 pos = transform.position;
            pos.y = liftHeight + Mathf.Sin(Time.time) * _wobbleAmp;
            transform.position = pos;
            _translationVec.Set(_target.position.x - pos.x - _targetDistance, 0f, 0f);
            transform.Translate(_translationVec);
        }
        else if (!_grabbed)
        {
            float targetY = _overPosition ? destHeight : _originalHeight;
            if (transform.position.y > targetY)
            {
                _translationVec.Set(0f, -_speed, 0f);
                transform.Translate(_translationVec * Time.deltaTime);
            }
            else
            {
                _lifted = false;
            }
        }
    }

    public void Grab(Transform target)
    {
        _target = target;
        _targetDistance = target.position.x - transform.position.x;
        _grabbed = true;
    }

    public void Release()
    {
        _target = transform;
        _grabbed = false;
    }

    private void OnTriggerEnter2D(Collider2D collision)
    {
        if (collision.gameObject.name.Equals(destColliderName))
        {
            _overPosition = true;
            hoveringInPlace.Invoke();
        }
    }

    private void OnTriggerStay2D(Collider2D collision)
    {
        if (collision.name.Equals(destColliderName) && gameObject.CompareTag(GameManager.MOVABLE_OBJECT_TAG))
        {
            inPlace.Invoke();
        }
    }

    private void OnTriggerExit2D(Collider2D collision)
    {
        if (collision.gameObject.name.Equals(destColliderName))
        {
            _overPosition = false;
            leftPosition.Invoke();
        }
    }
}
