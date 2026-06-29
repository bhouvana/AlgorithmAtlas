import json
from typing import Generator
from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, AlgorithmState
from algorithm_atlas_sdk import DistributedSystemState, DSNode, DSMessage
from algorithm_atlas_sdk.types import SimulationParams


class Paxos(AlgorithmPlugin):
    def metadata(self):
        return AlgorithmMetadata(
            slug="paxos",
            name="Paxos Consensus",
            category="distributed-systems",
            visualization_type="NETWORK_TOPOLOGY",
            description="Basic Paxos: proposer sends Prepare(n), acceptors respond Promise, proposer sends Accept(n,v), acceptors send Accepted.",
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=["distributed", "consensus", "paxos", "fault-tolerance"],
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> AlgorithmState:
        proposers = ["P0"]
        acceptors = ["A0", "A1", "A2", "A3", "A4"]
        nodes = ([DSNode("P0", "proposer", 0, (), (), "{}")]
               + [DSNode(a, "acceptor", 0, (), (), "{}") for a in acceptors])
        return DistributedSystemState(
            nodes=tuple(nodes), messages=(),
            event="init",
            description="1 proposer, 5 acceptors. Proposer will try to achieve consensus on value v=42.",
        )

    def steps(self, state: AlgorithmState) -> Generator[AlgorithmState, None, AlgorithmState]:
        proposers = ["P0"]
        acceptors = ["A0", "A1", "A2", "A3", "A4"]
        all_ids = proposers + acceptors
        history = []
        step = [0]
        ballot = 1
        value = 42

        def nxt():
            step[0] += 1; return step[0]

        def mk(roles, logs=None):
            logs = logs or {}
            return tuple(DSNode(nid, roles.get(nid, "acceptor"), ballot,
                                log=tuple(logs.get(nid, [])), inbox=(), data="{}") for nid in all_ids)

        # Phase 1a: Prepare
        prep_msgs = [DSMessage(f"m{nxt()}-P0-{a}", "P0", a, "Prepare", f"n={ballot}") for a in acceptors]
        history.extend(prep_msgs)
        yield DistributedSystemState(
            nodes=mk({"P0": "proposer"}), messages=tuple(history),
            event="phase1a_prepare",
            description=f"P0 broadcasts Prepare(n={ballot}) to all {len(acceptors)} acceptors.")

        # Phase 1b: Promise
        promise_msgs = []
        for i, a in enumerate(acceptors):
            # mark prepare delivered
            idx = next(j for j, m in enumerate(history) if m.msg_id == prep_msgs[i].msg_id)
            history[idx] = DSMessage(prep_msgs[i].msg_id, "P0", a, "Prepare",
                                     f"n={ballot}", True)
            pm = DSMessage(f"m{nxt()}-{a}-P0", a, "P0", "Promise",
                          f"n={ballot}, no_prev")
            promise_msgs.append(pm); history.append(pm)
        yield DistributedSystemState(
            nodes=mk({"P0": "proposer"}), messages=tuple(history),
            event="phase1b_promise",
            description=f"All {len(acceptors)} acceptors respond Promise(n={ballot}, no prior accepted value). Quorum achieved.")

        # Phase 2a: Accept
        for pm in promise_msgs:
            idx = next(j for j, m in enumerate(history) if m.msg_id == pm.msg_id)
            history[idx] = DSMessage(pm.msg_id, pm.src, pm.dst, pm.msg_type, pm.payload, True)
        acc_msgs = [DSMessage(f"m{nxt()}-P0-{a}", "P0", a, "Accept",
                              f"n={ballot}, v={value}") for a in acceptors]
        history.extend(acc_msgs)
        yield DistributedSystemState(
            nodes=mk({"P0": "proposer"}), messages=tuple(history),
            event="phase2a_accept",
            description=f"P0 sends Accept(n={ballot}, v={value}) to all acceptors.")

        # Phase 2b: Accepted
        accepted_logs = {}
        for i, a in enumerate(acceptors):
            idx = next(j for j, m in enumerate(history) if m.msg_id == acc_msgs[i].msg_id)
            history[idx] = DSMessage(acc_msgs[i].msg_id, "P0", a, "Accept",
                                     f"n={ballot}, v={value}", True)
            am = DSMessage(f"m{nxt()}-{a}-P0", a, "P0", "Accepted",
                          f"n={ballot}, v={value}")
            history.append(am)
            accepted_logs[a] = [f"accepted v={value}"]

        final = DistributedSystemState(
            nodes=mk({"P0": "proposer"}, logs=accepted_logs), messages=tuple(history),
            event="consensus_reached",
            description=f"All acceptors accepted v={value}. Consensus reached! "
                        f"Majority ({len(acceptors)}) agreed on value {value}.")
        yield final
        return final
