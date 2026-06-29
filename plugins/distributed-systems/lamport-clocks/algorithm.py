import json
from typing import Generator
from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, AlgorithmState
from algorithm_atlas_sdk import DistributedSystemState, DSNode, DSMessage
from algorithm_atlas_sdk.types import SimulationParams


class LamportClocks(AlgorithmPlugin):
    def metadata(self):
        return AlgorithmMetadata(
            slug="lamport-clocks",
            name="Lamport Clocks",
            category="distributed-systems",
            visualization_type="TIMELINE",
            description="Scalar Lamport clocks: on send LC=LC+1; on receive LC=max(local,received)+1. Provides a partial ordering of events.",
            complexity_time_best="O(1)",
            complexity_time_average="O(1)",
            complexity_time_worst="O(1)",
            complexity_space="O(n)",
            tags=["distributed", "logical-clocks", "ordering", "causality"],
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> AlgorithmState:
        nodes = tuple(DSNode(node_id=f"P{i}", role="process", term=0,
                             log=(), inbox=(),
                             data=json.dumps({"lc": 0}))
                      for i in range(3))
        return DistributedSystemState(
            nodes=nodes, messages=(),
            event="init",
            description="3 processes with Lamport clocks LC=0. "
                        "Events demonstrate total ordering guarantee.",
        )

    def steps(self, state: AlgorithmState) -> Generator[AlgorithmState, None, AlgorithmState]:
        lc = [0, 0, 0]
        history = []
        step = 0

        def nodes(active=None):
            return tuple(DSNode(
                node_id=f"P{i}", role="active" if i == active else "process",
                term=lc[i], log=(f"LC={lc[i]}",), inbox=(),
                data=json.dumps({"lc": lc[i]}),
            ) for i in range(3))

        def local(p, name):
            nonlocal step
            step += 1
            lc[p] += 1
            return DistributedSystemState(nodes=nodes(p), messages=tuple(history),
                event=f"local_{p}", description=f"P{p} '{name}': LC[{p}]++ = {lc[p]}")

        def send(src, dst, label):
            nonlocal step
            step += 1
            lc[src] += 1
            msg = DSMessage(msg_id=f"lc{step}-{src}{dst}", src=f"P{src}", dst=f"P{dst}",
                            msg_type="Send", payload=f"{label} ts={lc[src]}", delivered=False)
            history.append(msg)
            return (DistributedSystemState(nodes=nodes(src), messages=tuple(history),
                event=f"send_{src}_{dst}",
                description=f"P{src} sends '{label}' stamped ts={lc[src]}"),
                lc[src])

        def recv(src, dst, ts, label):
            nonlocal step
            step += 1
            lc[dst] = max(lc[dst], ts) + 1
            for i, m in enumerate(history):
                if m.src == f"P{src}" and m.dst == f"P{dst}" and not m.delivered:
                    history[i] = DSMessage(m.msg_id, m.src, m.dst, m.msg_type, m.payload, True)
                    break
            return DistributedSystemState(nodes=nodes(dst), messages=tuple(history),
                event=f"recv_{src}_{dst}",
                description=f"P{dst} receives '{label}' ts={ts}: LC = max({lc[dst]-1},{ts})+1 = {lc[dst]}")

        yield local(0, "event_a")
        s, t01 = send(0, 1, "msg_1"); yield s
        yield local(1, "event_b")
        yield recv(0, 1, t01, "msg_1")
        s, t12 = send(1, 2, "msg_2"); yield s
        yield local(2, "event_c")
        yield recv(1, 2, t12, "msg_2")
        yield local(0, "event_d")
        s, t20 = send(2, 0, "msg_3"); yield s
        yield recv(2, 0, t20, "msg_3")
        s, t02 = send(0, 2, "msg_4"); yield s
        yield recv(0, 2, t02, "msg_4")

        final = DistributedSystemState(
            nodes=nodes(), messages=tuple(history), event="done",
            description=f"Final Lamport clocks: P0={lc[0]}, P1={lc[1]}, P2={lc[2]}. "
                        "Lamport clocks imply: if a→b then LC(a)<LC(b).")
        yield final
        return final
