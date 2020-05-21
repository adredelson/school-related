using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RatController : MonoBehaviour
{
    public Transform rat;
    public Animator animator;
    public float startX;
    public float endX;


 
    private Vector3 _ratTranslation = Vector3.zero;
    private float _speed = 0.1f;
    private SpriteRenderer spriteRenderer;
    private GameManager gameManager;
    private bool onMop;



    // Start is called before the first frame update
    void Start()
    {
        gameManager = GameManager.Instance;
        spriteRenderer = gameObject.GetComponent<SpriteRenderer>();
    }

    // Update is called once per frame
    void Update()
    {
        Move();
    }

    private void Move()
    {
        float x = 0, y = 0, z = 0;
        if (Input.GetKey(GameManager.MOVE_LEFT_KEY))
        {
            animator.SetBool("isWalking", true);
            spriteRenderer.flipX = false;
            x = -_speed;
        }
        else if (Input.GetKey(GameManager.MOVE_RIGHT_KEY))
        {
            animator.SetBool("isWalking", true);
            spriteRenderer.flipX = true;
            x = _speed;
        }

        else
            animator.SetBool("isWalking", false);


        _ratTranslation.Set(x, y, z);
        rat.Translate(_ratTranslation * Time.deltaTime * 60);

        x = rat.position.x;
        float newX = Mathf.Clamp(x, startX, endX);
        rat.position = new Vector3(newX, rat.position.y);

    }

    public void LowerSpeed(float factor)
    {
        _speed /= factor;
    }

    private void OnTriggerEnter2D(Collider2D collision)
    {
        if (collision.name.Equals("Level Exit"))
        {
            gameManager.Invoke("NextLevel", 0.5f);
        }
    }

}
