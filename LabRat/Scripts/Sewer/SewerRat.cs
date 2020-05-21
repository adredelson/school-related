using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SewerRat : MonoBehaviour
{

    public Transform rat;
    public Animator animator;
    public float endX;
    public Transform cameraTransform;
    public Camera mainCamera;
    public GameObject killCloudPrefab;
    public float ratWidth = 3.1f;
    public GameObject ladder;

    public Sprite[] livesSprites;
    public SpriteRenderer lifeBar;
    public Vector3 killCloudPlacment = new Vector3(2.8f, 0.3f);



    private const KeyCode MOVE_RIGHT_KEY = KeyCode.RightArrow;
    private const KeyCode MOVE_LEFT_KEY = KeyCode.LeftArrow;

    private SpriteRenderer spriteRenderer;
    private Vector3 _ratTranslation = Vector3.zero;
    private bool isLeft;
    private int lifeLeft = 3;

    // Start is called before the first frame update
    void Start()
    {
        spriteRenderer = gameObject.GetComponent<SpriteRenderer>();
    }

    // Update is called once per frame
    void Update()
    {

        lifeBar.sprite = livesSprites[lifeLeft];
        Move();
        animator.SetBool("Dead", false);

        if (Input.GetKeyDown(GameManager.SELECT_KEY))
        {
            CreateKillClouds();
        }
    }

    public void LateUpdate()
    {
        lifeBar.sprite = livesSprites[lifeLeft];

    }


    private void CreateKillClouds()
    {
        float x = rat.position.x + killCloudPlacment.x;
        float y = rat.position.y + killCloudPlacment.y;
        if (isLeft)
            x = rat.position.x - ratWidth;
        GameObject cloud = Instantiate(killCloudPrefab, new Vector3(x, y), Quaternion.identity);
        cloud.GetComponent<KillCloudController>().left = isLeft;


    }

    private void Move()
    {
        float x = 0, y = 0, z = 0;
        if (Input.GetKey(MOVE_LEFT_KEY))
        {
            animator.SetBool("isWalking", true);
            spriteRenderer.flipX = true;
            x = -0.1f;
            isLeft = true;

        }
        else if (Input.GetKey(MOVE_RIGHT_KEY))
        {
            animator.SetBool("isWalking", true);
            spriteRenderer.flipX = false;
            x = 0.1f;
            isLeft = false;
        }

        else
        {
            animator.SetBool("isWalking", false);
            return;
        }

        _ratTranslation.Set(x, y, z);
        rat.Translate(_ratTranslation * Time.deltaTime * 70);

        x = rat.position.x;
        float startX = cameraTransform.position.x-mainCamera.orthographicSize;
       
        float newX = Mathf.Clamp(x, startX, endX);
        rat.position = new Vector3(newX, rat.position.y);
    }


    private void OnTriggerEnter2D(Collider2D collision)
    {
        GameObject collisionObject = collision.gameObject;
        if (collisionObject.CompareTag(GameManager.MONSTER_TAG))
        {
            //ToggleAnimation(true, 0f);
            gameObject.GetComponent<BoxCollider2D>().enabled = false;
            collisionObject.GetComponent<BoxCollider2D>().enabled = false;
            animator.SetBool("Hit", true);
            Invoke("DisableHit", 2f);
            
            lifeLeft--;
            if (lifeLeft == 0)
                Died();
           
        }

        if (collisionObject.CompareTag("Sewer End"))
        {
            collisionObject.SetActive(false);
            Invoke("ShowLadder", 13f);
        }
        if (collisionObject.CompareTag(GameManager.SCRIPTED_OBJECT_TAG))
            collision.gameObject.GetComponent<ScriptedObject>().runScript();
       
    }

    private void DisableHit()
    {
        animator.SetBool("Hit", false);
        gameObject.GetComponent<BoxCollider2D>().enabled = true;

    }

    private void Died()
    {
        lifeBar.sprite = livesSprites[4];
        Invoke("RestartLevel", 2f);
        

    }

    private void RestartLevel()
    {
        GameManager.Instance.JumpToLevel(4);
    }

    private void ShowLadder()
    {       
        ladder.SetActive(true);
        ladder.GetComponent<Animator>().SetBool("Show Ladder",true);
        Invoke("ResetLadder", 2f);

    }

    private void ResetLadder()
    {
        ladder.GetComponent<Animator>().SetBool("Show Ladder",false);
        ladder.tag = GameManager.SCRIPTED_OBJECT_TAG;


    }
}
