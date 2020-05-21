using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class GameManager : Singleton<GameManager>
{
    public const string ANIMATED_OBJECT_TAG = "Animated";
    public const string SCRIPTED_OBJECT_TAG = "Scripted";
    public const string MOVABLE_OBJECT_TAG = "Movable";
    public const string INTERACTIVE_OBJECT_TAG = "Interactive";
    public const string TELEKINESIS_TAG = "In Telekinesis";
    public const string MONSTER_TAG= "Monster";


    public const KeyCode MOVE_RIGHT_KEY = KeyCode.RightArrow;
    public const KeyCode MOVE_LEFT_KEY = KeyCode.LeftArrow;
    public const KeyCode SELECT_KEY = KeyCode.Space;



    public const KeyCode ACTION_KEY1 = KeyCode.Space;
    public const KeyCode ACTION_KEY2 = KeyCode.Return;

    public const int LEVEL_COUNT = 6;
    public GameObject pauseScreen;
    public List<GameObject> pauseScreenButtons;
    public GameObject levelCut;
    public float buttonScaleChangeFactor;

    private float _totalTimePlayed = 0;
    private GameObject _gameplay;
    private int _buttonIndex = 0;
    private GameObject _activeButton;
    private bool _inTitleScreen = true;
    private int _curLevel = 0;
    private bool _isPlaying = false;
    private List<Vector2> _initialPauseScales;

    // Start is called before the first frame update
    void Start()
    {
        pauseScreenButtons = new List<GameObject>();
        GetPauseScreenButtons();
        _initialPauseScales = new List<Vector2>(pauseScreenButtons.Count);
        for (int i = 0; i < pauseScreenButtons.Count; ++i)
        {
            _initialPauseScales.Add(pauseScreenButtons[i].transform.localScale);
        }
        buttonScaleChangeFactor = 1.5f;
    }

    private void GetPauseScreenButtons()
    {
        pauseScreenButtons.Clear();
        pauseScreenButtons.Add(GameObject.Find("Resume Button"));
        pauseScreenButtons.Add(GameObject.Find("Reset Button"));
        pauseScreenButtons.Add(GameObject.Find("Quit Button"));
    }

    private void GetLevelGameObjects()
    {
        _activeButton = pauseScreenButtons[_buttonIndex];
        _gameplay = GameObject.Find("Gameplay");
        levelCut = GameObject.Find("Level Cut");
        
    }

    // Update is called once per frame
    void Update()
    {
        if (_isPlaying)
        {
            _totalTimePlayed += Time.deltaTime;
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                PauseGame();
            }
            if (Input.GetKeyDown(KeyCode.F1))
            {
                JumpToLevel(1);
            }
            else if (Input.GetKeyDown(KeyCode.F2))
            {
                JumpToLevel(2);
            }
            else if (Input.GetKeyDown(KeyCode.F3))
            {
                JumpToLevel(3);
            }
            else if (Input.GetKeyDown(KeyCode.F4))
            {
                JumpToLevel(4);
            }
        }
        else if (!_inTitleScreen)
        {
            MenuInteraction();
        }
        else if (Input.anyKey)
        {
            _inTitleScreen = false;
            _isPlaying = true;
            NextLevel();
        }
    }

    internal static ScriptableObject getSceneController()
    {
        throw new NotImplementedException();
    }

    [RuntimeInitializeOnLoadMethod]
    static void BootManager()
    {
        GameManager manager = GameManager.Instance;
    }

    public void StartGame()
    {
        _isPlaying = true;
        _gameplay.SetActive(true);
        Destroy(pauseScreen);
        _buttonIndex = 0;
    }

    public void PauseGame()
    {
        _isPlaying = false;
        _gameplay.SetActive(false);
        pauseScreen = Instantiate(Resources.Load("Pause Screen")) as GameObject;
        GetPauseScreenButtons();
        _activeButton = pauseScreenButtons[_buttonIndex];
    }

    public void ResetGame()
    {
        _totalTimePlayed = 0;
        _inTitleScreen = true;
        _isPlaying = false;
        JumpToLevel(0);
        _buttonIndex = 0;
        _gameplay.SetActive(false);
    }

    public void Quit()
    {
        Application.Quit(0);
    }

    public void NextLevel()
    {
        if (_curLevel < LEVEL_COUNT)
        {
            JumpToLevel(_curLevel + 1);
        }
    }

    public void MenuInteraction()
    {
        if (Input.GetKeyDown(ACTION_KEY1) || Input.GetKeyDown(ACTION_KEY2))
        {
            _activeButton.GetComponent<ButtonAction>().Activate();
        }
        else if (Input.GetKeyDown(KeyCode.UpArrow))
        {
            MenuScroll(-1);
        }
        else if (Input.GetKeyDown(KeyCode.DownArrow))
        {
            MenuScroll(1);
        }
    }

    public void MenuScroll(int direction)
    {
        _buttonIndex = (_buttonIndex + direction) % pauseScreenButtons.Count;
        if (_buttonIndex < 0)
        {
            _buttonIndex = pauseScreenButtons.Count - 1;
        }
        _activeButton.transform.localScale /= buttonScaleChangeFactor;
        _activeButton = pauseScreenButtons[_buttonIndex];
        _activeButton.transform.localScale *= buttonScaleChangeFactor;
    }

    public void JumpToLevel(int level)
    {
        _curLevel = level;
        SceneManager.LoadScene(_curLevel);
        Invoke("GetLevelGameObjects", 0.1f);
    }

    public float GetTotalTime()
    {
        return _totalTimePlayed;
    }
}
