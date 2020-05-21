using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

public class HandleController : MonoBehaviour
{
    public UnityEvent correctState;
    public UnityEvent incorrectState;
    public UnityEvent misleadingState;

    public List<GameObject> state1Active;
    public List<GameObject> state2Active;
    public List<GameObject> state3Active;
    public List<GameObject> state4Active;

    private int _curState = 0;
    private Dictionary<int, List<GameObject>> _states;
    private const int NUM_STATES = 4;
    // Start is called before the first frame update
    void Start()
    {
        _states = new Dictionary<int, List<GameObject>>();
        _states.Add(0, state1Active);
        _states.Add(1, state2Active);
        _states.Add(2, state3Active);
        _states.Add(3, state4Active);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void nextState()
    {
        List<GameObject> activeState = _states[_curState];
        foreach (var obj in activeState)
        {
            obj.SetActive(false);
        }
        _curState = (_curState + 1) % NUM_STATES;
        activeState = _states[_curState];
        foreach (var obj in activeState)
        {
            obj.SetActive(true);
        }
        if (_curState == NUM_STATES - 1)
        {
            correctState.Invoke();
        }
        else if (_curState == 1)
        {
            misleadingState.Invoke();
        }
        else
        {
            incorrectState.Invoke();
        }
    }
}
