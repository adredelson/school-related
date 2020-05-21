using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class KillCloudController : MonoBehaviour
{
    public bool left;


    private float lifeSpan = 1f;
    private Vector3 translation = new Vector3(1, 1,-5);
    private float z = -5;
    private float speed = 4;
    private ArrayList deadMonsters;

    // Start is called before the first frame update
    void Start()
    {
        deadMonsters = new ArrayList();
        if (left)
        {

            gameObject.GetComponent<SpriteRenderer>().flipX = true;
            translation = new Vector3(translation.x * -1, translation.y,z);
        }
        Invoke("DestroyCloud", lifeSpan);
    }

    // Update is called once per frame
    void Update()
    {
        transform.Translate(translation * Time.deltaTime * speed);
    }

    private void DestroyCloud()
    {
        Destroy(gameObject);
    }

    private void OnTriggerEnter2D(Collider2D collision)
    {
        if (collision.gameObject.CompareTag(GameManager.MONSTER_TAG))
        {
            collision.gameObject.GetComponent<Animator>().SetTrigger("Hit");
            collision.gameObject.GetComponent<BoxCollider2D>().enabled = false;

            deadMonsters.Add(collision.gameObject);
            Invoke("DestoryObjects", 1f);
           
        }
    }

    private void DestroyObjects()
    {
        deadMonsters.Clear();
        DestroyCloud();
    }
}
