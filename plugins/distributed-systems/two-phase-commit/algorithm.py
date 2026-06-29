import json
import random
from typing import Generator
from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, AlgorithmState
from algorithm_atlas_sdk import DistributedSystemState, DSNode, DSMessage
from algorithm_atlas_sdk.types import SimulationParams


class TwoPhaseCommit(AlgorithmPlugin):
    def metadata(self):
        return AlgorithmMetadata(
            slug="two-phase-commit",
            name="Two-Phase Commit",
            category="distributed-systems",
            visualization_type="TIMELINE",
            description="2PC atomic commit protocol: coordinator sends Prepare to all participants; if all vote Yes, sends Commit; otherwise Abort.",
            complexity_time_best="O(n)",
            complexity_time_average="O(n)",
            complexity_time_worst="O(n)",
            complexity_space="O(n)",
            tags=["distributed", "consensus", "atomic-commit", "2pc"],
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> AlgorithmState:
        random.seed(params.seed)
        n = params.inputs.get("participants", 3)
        nodes = [DSNode("C", "coordinator", 0, (), (), "{}")]
        nodes += [DSNode(f"P{i}", "participant", 0, (), (), "{}") for i in range(n)]
        return DistributedSystemState(
            nodes=tuple(nodes), messages=(),
            event="init",
            description=f"1 coordinator + {n} participants. Coordinator will initiate global transaction.",
        )

    def steps(self, state: AlgorithmState) -> Generator[AlgorithmState, None, AlgorithmState]:
        random.seed(42)
        parts = [n.node_id for n in state.nodes if n.node_id != "C"]
        n = len(parts)
        history = []
        step = [0]

        def nxt():
            step[0] += 1
            return step[0]

        def mk_nodes(roles):
            return tuple(DSNode(nid, roles.get(nid, "participant"), 0,
                                log=roles.get(nid + "_log", ()), inbox=(),
                                data="{}") for nid in ["C"] + parts)

        # Phase 1: Prepare
        prepare_msgs = [DSMessage(f"m{nxt()}-C-{p}", "C", p, "Prepare", "txn_id=T1") for p in parts]
        history.extend(prepare_msgs)
        yield DistributedSystemState(
            nodes=mk_nodes({"C": "coordinator"}),
            messages=tuple(history), event="phase1_prepare",
            description="Phase 1: Coordinator sends PREPARE to all participants.")

        # Participants vote
        votes = {}
        vote_msgs = []
        for i, p in enumerate(parts):
            # Randomly decide vote (always Yes for determinism if seed=42)
            vote = "Yes"
            votes[p] = vote
            history[i] = DSMessage(prepare_msgs[i].msg_id, "C", p, "Prepare", "txn_id=T1", True)
            vm = DSMessage(f"m{nxt()}-{p}-C", p, "C", "VoteYes" if vote == "Yes" else "VoteNo",
                          f"vote={vote}")
            vote_msgs.append(vm)
            history.append(vm)
            roles = {"C": "coordinator", p: "voted_yes"}
            yield DistributedSystemState(
                nodes=mk_nodes(roles), messages=tuple(history),
                event=f"vote_{p}", description=f"{p} votes {vote}.")

        # Phase 2: Decision
        all_yes = all(v == "Yes" for v in votes.values())
        decision = "Commit" if all_yes else "Abort"

        # Mark vote msgs delivered
        for vm in vote_msgs:
            idx = next(i for i, m in enumerate(history) if m.msg_id == vm.msg_id)
            history[idx] = DSMessage(vm.msg_id, vm.src, vm.dst, vm.msg_type, vm.payload, True)

        decision_msgs = [DSMessage(f"m{nxt()}-C-{p}", "C", p, decision, f"txn_id=T1") for p in parts]
        history.extend(decision_msgs)
        roles = {"C": "coordinator"}
        for p in parts:
            roles[p] = "committing" if decision == "Commit" else "aborting"
        yield DistributedSystemState(
            nodes=mk_nodes(roles), messages=tuple(history),
            event=f"phase2_{decision.lower()}",
            description=f"Phase 2: All voted Yes. Coordinator sends {decision} to all participants.")

        # Participants acknowledge
        ack_roles = {}
        for i, p in enumerate(parts):
            idx = next(j for j, m in enumerate(history) if m.msg_id == decision_msgs[i].msg_id)
            history[idx] = DSMessage(
                decision_msgs[i].msg_id, "C", p, decision, "txn_id=T1", True)
            am = DSMessage(f"m{nxt()}-{p}-C", p, "C", "Ack", f"{decision.lower()}ed")
            history.append(am)
            ack_roles[p] = "committed" if decision == "Commit" else "aborted"
        ack_roles["C"] = "coordinator"

        final_state = DistributedSystemState(
            nodes=mk_nodes(ack_roles), messages=tuple(history),
            event="done",
            description=f"Transaction {decision}ted. All participants acknowledged. 2PC complete.")
        yield final_state
        return final_state
