from enum import Enum, IntEnum

class M(Enum):
    H = "H"
    V = "V"

class O(Enum):
    ZERO = "0"
    PLUS = "+"

class Automaton(IntEnum):
    q0 = 0
    q1 = 1
    q2 = 2
    q3 = 3

    def step(self, m, o):
        return TRANSITIONS.get((self, m, o))

    @property
    def accepting(self):
        return self is Automaton.q3

    @property
    def command(self):
        return {Automaton.q0: M.V, Automaton.q1: M.V, Automaton.q2: M.H}.get(self) # Vertical if I haven't hit the wall yet, horizontal otherwise

# This is a map that gives me the next state based on input, i.e. the edges of automaton
TRANSITIONS = {
    # q0: hit nothing
    (Automaton.q0, M.H, O.PLUS): Automaton.q0,
    (Automaton.q0, M.V, O.PLUS): Automaton.q0,
    (Automaton.q0, M.H, O.ZERO): Automaton.q1,
    (Automaton.q0, M.V, O.ZERO): Automaton.q2,

    # q1: hit vertical (left wall)
    (Automaton.q1, M.V, O.PLUS): Automaton.q1,
    (Automaton.q1, M.H, O.ZERO): Automaton.q1,
    (Automaton.q1, M.H, O.PLUS): Automaton.q0,
    (Automaton.q1, M.V, O.ZERO): Automaton.q3,

    # q2: hit horizontal (bottom wall)
    (Automaton.q2, M.H, O.PLUS): Automaton.q2,
    (Automaton.q2, M.V, O.PLUS): Automaton.q0,
    (Automaton.q2, M.H, O.ZERO): Automaton.q3,

    # q3: hit origin (accepting)
    (Automaton.q3, M.V, O.PLUS): Automaton.q1,
    (Automaton.q3, M.H, O.PLUS): Automaton.q2,
}