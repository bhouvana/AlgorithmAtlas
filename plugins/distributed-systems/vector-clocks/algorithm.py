import json
import random
from typing import Generator
from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, AlgorithmState
from algorithm_atlas_sdk import DistributedSystemState, DSNode, DSMessage
from algorithm_atlas_sdk.types import SimulationParams


class VectorClocks(AlgorithmPlugin):
    def metadata(self):
        return AlgorithmMetadata(
            slug="vector-clocks",
            name="Vector Clocks",
            category="distributed-systems",
            visualization_type="TIMELINE",
            description="Lamport vector clocks track causality across 3 processes: on send increment own component; on receive take element-wise max then increment.",
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=["distributed", "causality", "vector-clocks", "ordering"],
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> AlgorithmState:
        n = 3
        clocks = [[0] * n for _ in range(n)]
        nodes = [DSNode(node_id=f"P{i}", role="process", term=0,
                        log=(), inbox=(),
                        data=json.dumps({"vc": clocks[i]}))
                 for i in range(n)]
        return DistributedSystemState(
            nodes=tuple(nodes), messages=(),
            event="init",
            description="3 processes start with vector clocks [0,0,0]. "
                        "Events will show how clocks advance to capture causality.",
        )

    def steps(self, state: AlgorithmState) -> Generator[AlgorithmState, None, AlgorithmState]:
        n = 3
        clocks = [[0] * n for _ in range(n)]
        msgs_history = []
        step = 0

        def make_nodes(active=None, desc=""):
            return tuple(DSNode(
                node_id=f"P{i}", role="process" if i != active else "active",
                term=sum(clocks[i]),
                log=(f"VC={clocks[i]}",),
                inbox=(), data=json.dumps({"vc": list(clocks[i])})
            ) for i in range(n))

        def local_event(proc, event_name):
            nonlocal step
            step += 1
            clocks[proc][proc] += 1
            nodes = make_nodes(active=proc)
            return DistributedSystemState(
                nodes=nodes, messages=tuple(msgs_history),
                event=f"local_{proc}_{step}",
                description=f"P{proc} local event '{event_name}'. "
                            f"VC[{proc}] = {clocks[proc]}",
            )

        def send_msg(src, dst, label):
            nonlocal step
            step += 1
            clocks[src][src] += 1
            msg = DSMessage(
                msg_id=f"vc{step}-{src}-{dst}",
                src=f"P{src}", dst=f"P{dst}",
                msg_type="Send",
                payload=f"{label} VC={clocks[src]}",
                delivered=False,
            )
            msgs_history.append(msg)
            nodes = make_nodes(active=src)
            return DistributedSystemState(
                nodes=nodes, messages=tuple(msgs_history),
                event=f"send_{src}_{dst}",
                description=f"P{src} sends '{label}' to P{dst} with VC={clocks[src]}",
            ), list(clocks[src])

        def recv_msg(src, dst, sent_vc, label):
            nonlocal step
            step += 1
            # Element-wise max then increment own component
            for k in range(n):
                clocks[dst][k] = max(clocks[dst][k], sent_vc[k])
            clocks[dst][dst] += 1
            # Mark the corresponding send message delivered
            for i, m in enumerate(msgs_history):
                if m.src == f"P{src}" and m.dst == f"P{dst}" and not m.delivered:
                    msgs_history[i] = DSMessage(
                        msg_id=m.msg_id, src=m.src, dst=m.dst,
                        msg_type=m.msg_type, payload=m.payload, delivered=True,
                    )
                    break
            nodes = make_nodes(active=dst)
            return DistributedSystemState(
                nodes=nodes, messages=tuple(msgs_history),
                event=f"recv_{src}_{dst}",
                description=f"P{dst} receives '{label}' from P{src}. "
                            f"VC = max({clocks[dst]}, sent) + 1 = {clocks[dst]}",
            )

        yield local_event(0, "a")

        state_s, vc_0_1 = send_msg(0, 1, "m1")
        yield state_s

        yield local_event(1, "b")

        yield recv_msg(0, 1, vc_0_1, "m1")

        state_s, vc_1_2 = send_msg(1, 2, "m2")
        yield state_s

        yield local_event(0, "c")

        yield recv_msg(1, 2, vc_1_2, "m2")

        state_s, vc_2_0 = send_msg(2, 0, "m3")
        yield state_s

        yield local_event(2, "d")

        yield recv_msg(2, 0, vc_2_0, "m3")

        state_s, vc_0_2 = send_msg(0, 2, "m4")
        yield state_s

        yield recv_msg(0, 2, vc_0_2, "m4")

        final = DistributedSystemState(
            nodes=make_nodes(), messages=tuple(msgs_history),
            event="done",
            description=f"Final vector clocks: "
                        f"P0={clocks[0]}, P1={clocks[1]}, P2={clocks[2]}. "
                        f"Causality fully captured.",
        )
        yield final
        return final
