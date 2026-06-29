import json
from typing import Generator
from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, AlgorithmState
from algorithm_atlas_sdk import DistributedSystemState, DSNode, DSMessage
from algorithm_atlas_sdk.types import SimulationParams


class DistributedMutex(AlgorithmPlugin):
    def metadata(self):
        return AlgorithmMetadata(
            slug="distributed-mutex",
            name="Distributed Mutex (Ricart-Agrawala)",
            category="distributed-systems",
            visualization_type="TIMELINE",
            description="Ricart-Agrawala algorithm: process wanting CS broadcasts Request with timestamp; others reply OK or defer; after n-1 OKs enter CS.",
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=["distributed", "mutual-exclusion", "critical-section", "ricart-agrawala"],
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> AlgorithmState:
        nodes = tuple(DSNode(f"P{i}", "idle", 0, (), (), json.dumps({"state": "idle"}))
                      for i in range(3))
        return DistributedSystemState(
            nodes=nodes, messages=(),
            event="init",
            description="3 processes. P0 wants to enter Critical Section. "
                        "Ricart-Agrawala requires n-1=2 OKs before entering.")

    def steps(self, state: AlgorithmState) -> Generator[AlgorithmState, None, AlgorithmState]:
        history = []
        step = [0]
        ts = [0, 0, 0]  # Lamport timestamps

        def nxt(): step[0] += 1; return step[0]

        def mk(states, terms=None):
            terms = terms or ts
            return tuple(DSNode(f"P{i}", states[i], terms[i],
                                log=(f"state={states[i]}",), inbox=(),
                                data=json.dumps({"state": states[i], "ts": ts[i]}))
                         for i in range(3))

        states = ["idle", "idle", "idle"]

        # P0 wants CS
        ts[0] += 1
        states[0] = "wanting"
        reqs = [DSMessage(f"m{nxt()}-P0-P{i}", "P0", f"P{i}", "Request",
                          f"ts={ts[0]}") for i in range(1, 3)]
        history.extend(reqs)
        yield DistributedSystemState(
            nodes=mk(states), messages=tuple(history),
            event="request_sent",
            description=f"P0 wants CS (ts={ts[0]}). Broadcasts Request to P1, P2.")

        # P1 is idle → replies OK immediately
        ts[1] += 1
        idx = next(j for j, m in enumerate(history) if m.src == "P0" and m.dst == "P1")
        history[idx] = DSMessage(history[idx].msg_id, "P0", "P1", "Request",
                                 f"ts={ts[0]}", True)
        ok1 = DSMessage(f"m{nxt()}-P1-P0", "P1", "P0", "OK", "ts=0")
        history.append(ok1)
        yield DistributedSystemState(
            nodes=mk(states), messages=tuple(history),
            event="ok_from_p1",
            description="P1 is idle → immediately replies OK to P0.")

        # P2 also wants CS, sends its own request (higher ts → will defer)
        ts[2] = ts[0]  # same time → lower id wins (P0 < P2)
        states[2] = "wanting"
        req2 = DSMessage(f"m{nxt()}-P2-P0", "P2", "P0", "Request", f"ts={ts[2]}")
        history.append(req2)
        yield DistributedSystemState(
            nodes=mk(states), messages=tuple(history),
            event="p2_request",
            description=f"P2 also wants CS with ts={ts[2]}. P0's request has same ts but lower id → P0 has priority.")

        # P0 sees P2's request: since ts[0]<ts[2] or (ts same and id 0<2), defer
        # P0 defers P2 (adds to deferred list)
        # P2 receives P0's request: P0 has higher priority → P2 defers, sends OK
        idx2 = next(j for j, m in enumerate(history) if m.src == "P0" and m.dst == "P2")
        history[idx2] = DSMessage(history[idx2].msg_id, "P0", "P2", "Request",
                                  f"ts={ts[0]}", True)
        ok2 = DSMessage(f"m{nxt()}-P2-P0", "P2", "P0", "OK", "deferred_self")
        history.append(ok2)
        yield DistributedSystemState(
            nodes=mk(states), messages=tuple(history),
            event="p2_defers",
            description="P2 receives P0's request: P0 has equal ts but lower id → P2 sends OK and defers its own entry.")

        # P0 has 2 OKs → enters CS
        for m in [ok1, ok2]:
            i = next(j for j, h in enumerate(history) if h.msg_id == m.msg_id)
            history[i] = DSMessage(m.msg_id, m.src, m.dst, m.msg_type, m.payload, True)
        states[0] = "in_cs"
        yield DistributedSystemState(
            nodes=mk(states), messages=tuple(history),
            event="enter_cs",
            description="P0 received OK from P1 and P2 (2 of 2 needed). Enters Critical Section!")

        # P0 exits CS, sends deferred OK to P2
        states[0] = "idle"
        ok_p2 = DSMessage(f"m{nxt()}-P0-P2", "P0", "P2", "OK", "released_cs")
        history.append(ok_p2)
        yield DistributedSystemState(
            nodes=mk(states), messages=tuple(history),
            event="release_cs",
            description="P0 exits CS. Sends OK to deferred P2.")

        # P2 enters CS
        idx = next(j for j, m in enumerate(history) if m.msg_id == ok_p2.msg_id)
        history[idx] = DSMessage(ok_p2.msg_id, ok_p2.src, ok_p2.dst, ok_p2.msg_type, ok_p2.payload, True)
        states[2] = "in_cs"
        final = DistributedSystemState(
            nodes=mk(states), messages=tuple(history),
            event="done",
            description="P2 now enters CS. Mutual exclusion achieved with no deadlock.")
        yield final
        return final
