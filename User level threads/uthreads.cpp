#include "uthreads.h"
#include <signal.h>
#include <iostream>
#include <deque>
#include <vector>
#include <csetjmp>
#include <sys/time.h>
#include <unordered_map>
#include <queue>
#include "sleeping_threads_list.h"

#define SA_ERR "System error: failure to assign handler to signal\n"
#define TIMER_ERR "System error: failure to set timer\n"
#define MEM_ERR "System error: failure to allocate memory\n"
#define TRD_CNT_ERR "Thread library error: max thread count exceeded\n"
#define QUANT_ERR "Thread library error: quantum length should be positive\n"
#define ILLEGAL_ID "Thread library error: illegal thread id\n"

#define READY 0
#define RUNNING 1
#define BLOCKED 2

typedef struct uthread
{
	int id, state, qunats;
	bool asleep = false;
	char stk[STACK_SIZE];
}uthread;

static sigjmp_buf env[MAX_THREAD_NUM];
static int quantCnt = 0;
static struct itimerval scheduler;
static struct itimerval sleepTimer;
static struct sigaction quantumsa;
static struct sigaction sleepsa;
static uthread* running;
static unsigned int trdCnt = 0;
static time_t q_len = 0;
static suseconds_t q_ulen = 0;
static SleepingThreadsList sleeping;
static sigset_t mask;
static std::deque<uthread*> ready;
static std::priority_queue <int, std::vector<int>, std::greater<int> > ids;
static std::unordered_map<int, uthread*> threads;

#ifdef __x86_64__
/* code for 64 bit Intel arch */

typedef unsigned long address_t;
#define JB_SP 6
#define JB_PC 7

/* A translation is required when using an address of a variable.
   Use this as a black box in your code. */
address_t translate_address(address_t addr)
{
	address_t ret;
	asm volatile("xor    %%fs:0x30,%0\n"
	             "rol    $0x11,%0\n"
	: "=g" (ret)
	: "0" (addr));
	return ret;
}

#else
/* code for 32 bit Intel arch */

typedef unsigned int address_t;
#define JB_SP 4
#define JB_PC 5

/* A translation is required when using an address of a variable.
   Use this as a black box in your code. */
address_t translate_address(address_t addr)
{
    address_t ret;
    asm volatile("xor    %%gs:0x18,%0\n"
		"rol    $0x9,%0\n"
                 : "=g" (ret)
                 : "0" (addr));
    return ret;
}

#endif

/**
 * Removes the given thread from the ready queue
 * @param trd the thread of interest
 */
static void unreadyThread(uthread *trd)
{
	std::deque<uthread*>::iterator trdIt;
	for (auto it = ready.begin(); it != ready.end(); it++)
	{
		if (*it == trd)
		{
			trdIt = it;
			break;
		}
	}
	ready.erase(trdIt);
}

/**
 * Moves the next ready thread to running state
 */
static void ready2running()
{
	uthread* trd = ready.front();
	ready.pop_front();
	running = trd;
	trd->state = RUNNING;
	trd->qunats++;
}

/**
 * Reset quantum timer
 * @return 0 upon success, -1 upon failure
 */
static int resetQuantumTimer()
{
    quantCnt++;
    scheduler.it_value.tv_sec = q_len;
    scheduler.it_value.tv_usec = q_ulen;
    if (setitimer (ITIMER_VIRTUAL, &scheduler, nullptr)) {
        std::cerr << TIMER_ERR;
        exit(1);
    }
    return 0;
}

/**
 * The handler function for the quantum timer signal
 * @param sig the timer signal
 */
static void quantumHandler(int sig)
{
	uthread* trd = running;
	if (sigsetjmp(env[trd->id], 1))
    {
        return;
    }
	ready.push_back(trd);
	trd->state = READY;
	ready2running();
    resetQuantumTimer();
	siglongjmp(env[running->id], 1);
}
/**
 * Calculates the timeval values until thread wakeup
 * @param usecs_to_sleep time for the thread to sleep in micro seconds
 * @return the calculated timeval struct
 */
static timeval calc_wake_up_timeval(int usecs_to_sleep) {

	timeval now, time_to_sleep, wake_up_timeval;
	gettimeofday(&now, nullptr);
	time_to_sleep.tv_sec = usecs_to_sleep / 1000000;
	time_to_sleep.tv_usec = usecs_to_sleep % 1000000;
	timeradd(&now, &time_to_sleep, &wake_up_timeval);
	return wake_up_timeval;
}

/**
 * Reset the timer for sleeping threads
 * @return 0 upon success, -1 upon failure
 */
static int resetSleepTimer()
{
	wake_up_info* wake = sleeping.peek();
	while (wake != nullptr && wake->dead)
    {
        sleeping.pop();
        wake = sleeping.peek();
    }
	if (wake != nullptr)
	{
		timeval now;
		gettimeofday(&now, nullptr);
		if (timercmp(&now, &wake->awaken_tv, <=))
		{
			sleepTimer.it_value.tv_usec = 2;
		}
		else
		{
			timersub(&wake->awaken_tv, &now, &sleepTimer.it_value);
		}
		if (setitimer (ITIMER_REAL, &sleepTimer, nullptr)) {
			std::cerr << TIMER_ERR;
			exit(1);
		}
	}
	return 0;
}

/**
 * The handler function for the sleep timer signal
 * @param sig the timer signal
 */
static void sleepHandler(int sig)
{
	wake_up_info* wake = sleeping.peek();
    while (wake != nullptr && wake->dead)
    {
        sleeping.pop();
        wake = sleeping.peek();
    }
    if (wake == nullptr)
    {
        return;
    }
	uthread* trd = threads[wake->id];
	if (trd->state != BLOCKED)
	{
		trd->state = READY;
		ready.push_back(trd);
	}
	trd->asleep = false;
	sleeping.pop();
	resetSleepTimer();
}

/**
 * Create mask of signals for blocking
 */
static void createSigMask()
{
	sigemptyset(&mask);
	sigaddset(&mask, SIGVTALRM);
	sigaddset(&mask, SIGALRM);
}

int uthread_init(int quantum_usecs)
{
	q_len = quantum_usecs / 1000000;
	q_ulen = quantum_usecs % 1000000;
	createSigMask();
	if (quantum_usecs <= 0)
	{
		std::cerr << QUANT_ERR;
		return -1;
	}
	uthread* mainT;
	try
	{
		mainT = new uthread;
	}
	catch (std::bad_alloc &e)
	{
		std::cerr<<MEM_ERR;
		exit(1);
	}
	running = mainT;
	mainT->state = RUNNING;
	mainT->id = trdCnt++;
    threads[mainT->id] = mainT;
	mainT->qunats = quantCnt + 1;
	quantumsa.sa_handler = &quantumHandler;
	quantumsa.sa_mask = mask;
	if (sigaction(SIGVTALRM, &quantumsa, nullptr) < 0)
	{
		std::cerr << SA_ERR;
		exit(1);
	}
	sleepsa.sa_handler = &sleepHandler;
	sleepsa.sa_mask = mask;
	if (sigaction(SIGALRM, &sleepsa, nullptr) < 0)
	{
		std::cerr << SA_ERR;
		exit(1);
	}
	resetQuantumTimer();
	sigsetjmp(env[mainT->id], 1);
	return 0;
}

int uthread_spawn(void (*f)(void))
{
	if (threads.size() >= MAX_THREAD_NUM)
	{
		std::cerr << TRD_CNT_ERR;
		return -1;
	}
	address_t sp, pc;
	uthread* newThread;
	try
	{
		newThread = new uthread;
	}
	catch (std::bad_alloc &e)
	{
		std::cerr << MEM_ERR;
		exit(1);
	}
	if (ids.empty())
	{
		newThread->id = trdCnt++;
	}
	else
	{
		newThread->id = ids.top();
		ids.pop();
	}
	newThread->qunats = 0;
	newThread->state = READY;
	ready.push_back(newThread);
	sp = (address_t)newThread->stk + STACK_SIZE - sizeof(address_t);
	pc = (address_t)f;
	if (sigsetjmp(env[newThread->id], 1))
    {
	    return 0;
    }
	(env[newThread->id]->__jmpbuf)[JB_SP] = translate_address(sp);
	(env[newThread->id]->__jmpbuf)[JB_PC] = translate_address(pc);
	sigemptyset(&env[newThread->id]->__saved_mask);
	threads[newThread->id] = newThread;
	return newThread->id;
}

int uthread_terminate(int tid)
{
	sigprocmask(SIG_BLOCK, &mask, nullptr);
	if(threads.find(tid) == threads.end())
	{
		std::cerr << ILLEGAL_ID;
		return -1;
	}
	if (tid == 0)
	{
		for (auto pair : threads)
		{
			delete pair.second;
		}
		sigprocmask(SIG_UNBLOCK, &mask, nullptr);
		exit(0);
	}
	ids.push(tid);
	uthread* trd = threads[tid];
	threads.erase(tid);
	if (running->id == tid)
	{
		delete running;
        ready2running();
		if (resetQuantumTimer())
		{
            sigprocmask(SIG_UNBLOCK, &mask, nullptr);
			return -1;
		}
		sigprocmask(SIG_UNBLOCK, &mask, nullptr);
		siglongjmp(env[running->id], 1);
	}
	if (trd->state == READY)
	{
		unreadyThread(trd);
	}
	if (trd->asleep)
	{
		sleeping.remove(trd->id);
	}
	delete trd;
	sigprocmask(SIG_UNBLOCK, &mask, nullptr);
	return 0;
}

int uthread_block(int tid)
{
	sigprocmask(SIG_BLOCK, &mask, nullptr);
	if(threads.find(tid) == threads.end() || tid == 0)
	{
		std::cerr << ILLEGAL_ID;
		return -1;
	}
	uthread* trd = threads[tid];
	if (trd->state == BLOCKED)
	{
		sigprocmask(SIG_UNBLOCK, &mask, nullptr);
		return 0;
	}
	trd->state = BLOCKED;
	if (running->id == tid )
	{
        ready2running();
		if (resetQuantumTimer())
		{
            sigprocmask(SIG_UNBLOCK, &mask, nullptr);
			return -1;
		}
        if (sigsetjmp(env[trd->id], 1))
        {
            sigprocmask(SIG_UNBLOCK, &mask, nullptr);
            return 0;
        }
		siglongjmp(env[running->id], 1);
	}
	if (!trd->asleep)
	{
		unreadyThread(trd);
	}
	sigprocmask(SIG_UNBLOCK, &mask, nullptr);
	return 0;
}

int uthread_resume(int tid)
{
	auto trdIt = threads.find(tid);
	if(trdIt == threads.end())
	{
		std::cerr << ILLEGAL_ID;
		return -1;
	}
	uthread* trd = trdIt->second;
	if (trd->state == BLOCKED)
	{
		if (!trd->asleep)
		{
			ready.push_back(trd);
		}
		trd->state = READY;
	}
	return 0;
}

int uthread_sleep(int usec)
{
    uthread* trd = running;
	sigprocmask(SIG_BLOCK, &mask, nullptr);
	if(running->id == 0)
	{
		std::cerr << ILLEGAL_ID;
        sigprocmask(SIG_UNBLOCK, &mask, nullptr);
		return -1;
	}
	timeval wakeup = calc_wake_up_timeval(usec);
	sleeping.add(running->id, wakeup);
	if (resetSleepTimer())
	{
        sigprocmask(SIG_UNBLOCK, &mask, nullptr);
		return -1;
	}
	running->asleep = true;
    ready2running();
    if (resetQuantumTimer())
    {
        sigprocmask(SIG_UNBLOCK, &mask, nullptr);
        return -1;
    }
    if (sigsetjmp(env[trd->id], 1))
    {
        sigprocmask(SIG_UNBLOCK, &mask, nullptr);
        return 0;
    }
    siglongjmp(env[running->id], 1);
}

int uthread_get_tid()
{
	return running->id;
}

int uthread_get_total_quantums()
{
	return quantCnt;
}

int uthread_get_quantums(int tid)
{
	if(threads.find(tid) == threads.end())
	{
		std::cerr << ILLEGAL_ID;
		return -1;
	}
	uthread* trd = threads[tid];
	return trd->qunats;
}
