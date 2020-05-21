using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MonsterController : MonoBehaviour
{

    public bool left;
    public float speed;
    public Vector3 startPoint;
    public Vector3 translationVec;
    

    // Start is called before the first frame update
    void Start()
    {
    

        if (left)
        {
            translationVec = new Vector3(translationVec.x * -1, translationVec.y);
            gameObject.GetComponent<SpriteRenderer>().flipX = true;
            speed += 5;
        }

        transform.position = new Vector3(transform.position.x + startPoint.x, transform.position.y + startPoint.y);

     }

    // Update is called once per frame
    void Update()
    {
        
        transform.Translate(translationVec * Time.deltaTime * speed);

    }
}
