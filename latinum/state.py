from .utils import Duration

_TIME = 0.0

_SPACE = [0, 1]

_AGENTS = {}

def log(string):
    print("{}\t{}".format(_TIME, string))

def current_time():
    return _TIME

def advance_time(amount):
    assert amount > 0
    global _TIME
    duration_end = _TIME + amount
    duration = Duration(_TIME, duration_end)
    log("TIME => {}".format(duration_end))
    for agent_id in list(all_agent_ids()):
        agent = get_agent(agent_id)
        agent.advance(duration)
    _TIME = duration_end

def get_spatial_boundary():
    return _SPACE

def set_spatial_boundary(x, y):
    assert y > x
    _SPACE[0] = x
    _SPACE[1] = y

def add_agent(agent):
    log("AGENT {} ADDED @ {}".format(agent.id, agent.location))
    _AGENTS[agent.id] = agent

def all_agent_ids():
    return _AGENTS.keys()

def get_agent(id):
    return _AGENTS[id]

def remove_agent(id):
    log("AGENT {} DELETED".format(id))
    del _AGENTS[id]

def agents_located_in(a, b):
    assert b > a
    return (agent for agent in _AGENTS.values() if agent.location >= a and agent.location <= b)
