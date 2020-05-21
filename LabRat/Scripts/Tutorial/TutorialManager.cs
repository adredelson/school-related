using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class TutorialManager : MonoBehaviour
{
    public GameObject key;
    public GameObject dropper;
    public GameObject instructionsCanvas;
    public TextMeshProUGUI instructions;
    public TextMeshProUGUI iContinue;

    private const string KEY_PROMPT = "Press Space again to release a lifted object";
    private const string DROPPER_PROMPT = "Not all interactions are useful...";

    private bool _prompt = false;
    private bool _keyPrompted = false;
    private bool _dropperPrompted = false;
    // Start is called before the first frame update
    void Start()
    {
        Prompt(instructions.text);
    }

    // Update is called once per frame
    void Update()
    {
        if (!_keyPrompted && key.tag.Equals(GameManager.TELEKINESIS_TAG))
        {
            Prompt(KEY_PROMPT);
            _keyPrompted = true;
        }
        if (!_dropperPrompted && dropper.tag.Equals(GameManager.TELEKINESIS_TAG))
        {
            Prompt(DROPPER_PROMPT);
            _dropperPrompted = true;
        }
        if (_prompt && Input.anyKeyDown)
        {
            Continue();
        }
    }

    private void Prompt(string instruction)
    {
        iContinue.enabled = false;
        instructionsCanvas.SetActive(true);
        instructions.text = instruction;
        Invoke("AllowContinue", 0.05f);
        Time.timeScale = 0.1f;
    }

    private void AllowContinue()
    {
        iContinue.enabled = true;
        _prompt = true;
    }

    private void Continue()
    {
        instructionsCanvas.SetActive(false);
        _prompt = false;
        Time.timeScale = 1;
    }
}
