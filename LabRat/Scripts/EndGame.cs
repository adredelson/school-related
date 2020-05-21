using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class EndGame : MonoBehaviour
{
    public TextMeshProUGUI ResultText;
    public const string RESULT = "You have finished the expiriment successfully.\n It took you {0} seconds";

    private float _time;
    // Start is called before the first frame update
    void Start()
    {
        _time = GameManager.Instance.GetTotalTime();
        string timeString = _time.ToString("f1");
        ResultText.text = string.Format(RESULT, timeString);
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
