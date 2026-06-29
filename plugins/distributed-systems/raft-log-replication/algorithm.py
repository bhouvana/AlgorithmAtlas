"""
Raft Log Replication plugin for Algorithm Atlas.
Pre-elected leader replicates 5 client commands to 4 followers via AppendEntries RPCs.
Visualization: TIMELINE
"""
import json
import random
from typing import Generator

from algorithm_atlas_sdk import (
    AlgorithmMetadata,
    AlgorithmPlugin,
    AlgorithmState,
    DistributedSystemState,
    DSNode,
    DSMessage,
)

COMMANDS = ("SET x=1", "SET y=2", "DEL z", "SET w=10", "INCR counter")


class RaftLogReplication(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="raft-log-replication",
            name="Raft Log Replication",
            category="distributed-systems",
            visualization_type="TIMELINE",
            description=(
                "A pre-elected Raft leader replicates 5 client commands to 4 followers "
                "using AppendEntries RPCs. Shows commit once a majority acknowledges each entry."
            ),
            time_complexity="O(n)",
            space_complexity="O(n log n)",
            tags=("distributed", "consensus", "raft", "replication"),
        )

    def initialize(self, params: dict, seed: int) -> AlgorithmState:
        random.seed(seed)
        leader = DSNode(
            node_id="L0",
            role="leader",
            term=1,
            log=(),
            inbox=(),
            data=json.dumps({"commit_index": -1, "next_index": {f"F{i}": 0 for i in range(4)}}),
        )
        followers = tuple(
            DSNode(
                node_id=f"F{i}",
                role="follower",
                term=1,
                log=(),
                inbox=(),
                data=json.dumps({"commit_index": -1}),
            )
            for i in range(4)
        )
        nodes = (leader,) + followers
        ds_state = DistributedSystemState(
            nodes=nodes,
            messages=(),
            event="init",
            description="Raft cluster ready. L0 is leader (term 1). Waiting for client commands.",
        )
        return AlgorithmState(
            step=0,
            data={"log": [], "commit_index": -1, "pending_cmd": None},
            visualization=ds_state,
            is_complete=False,
        )

    def steps(self, state: AlgorithmState) -> Generator[AlgorithmState, None, None]:
        step = state.step
        ds: DistributedSystemState = state.visualization
        nodes = list(ds.nodes)
        current_log = []
        commit_index = -1

        for cmd_idx, cmd in enumerate(COMMANDS):
            # Phase A: Client sends command to leader
            step += 1
            entry = f"[{cmd_idx}:{cmd}]"
            current_log = current_log + [entry]
            leader_data = json.loads(nodes[0].data)
            leader_data["next_index"] = {f"F{i}": cmd_idx for i in range(4)}
            nodes[0] = DSNode(
                node_id="L0",
                role="leader",
                term=1,
                log=tuple(current_log),
                inbox=(),
                data=json.dumps(leader_data),
            )
            client_msg = DSMessage(
                msg_id=f"msg-{step}-client-L0",
                src="client",
                dst="L0",
                msg_type="ClientRequest",
                payload=json.dumps({"command": cmd, "index": cmd_idx}),
                delivered=True,
            )
            ds = DistributedSystemState(
                nodes=tuple(nodes),
                messages=(client_msg,),
                event="client_request",
                description=f"Client sends command '{cmd}' to leader L0. L0 appends entry {cmd_idx} to its log.",
            )
            yield AlgorithmState(
                step=step,
                data={"log": list(current_log), "commit_index": commit_index, "pending_cmd": cmd},
                visualization=ds,
                is_complete=False,
            )

            # Phase B: Leader sends AppendEntries to all followers
            step += 1
            ae_messages = tuple(
                DSMessage(
                    msg_id=f"msg-{step}-L0-F{i}",
                    src="L0",
                    dst=f"F{i}",
                    msg_type="AppendEntries",
                    payload=json.dumps({
                        "term": 1,
                        "leader_id": "L0",
                        "prev_log_index": cmd_idx - 1,
                        "entries": [{"index": cmd_idx, "term": 1, "command": cmd}],
                        "leader_commit": commit_index,
                    }),
                    delivered=False,
                )
                for i in range(4)
            )
            ds = DistributedSystemState(
                nodes=tuple(nodes),
                messages=ae_messages,
                event="append_entries_sent",
                description=f"L0 sends AppendEntries(index={cmd_idx}, cmd='{cmd}') to all 4 followers.",
            )
            yield AlgorithmState(
                step=step,
                data={"log": list(current_log), "commit_index": commit_index, "pending_cmd": cmd},
                visualization=ds,
                is_complete=False,
            )

            # Phase C: Followers receive and acknowledge (show first 2 fast acks = majority)
            ack_msgs = []
            for i in range(4):
                step += 1
                # Follower appends entry
                follower_idx = i + 1
                nodes[follower_idx] = DSNode(
                    node_id=f"F{i}",
                    role="follower",
                    term=1,
                    log=tuple(current_log),
                    inbox=(),
                    data=json.dumps({"commit_index": commit_index}),
                )
                # Mark delivered
                updated_ae = tuple(
                    DSMessage(
                        msg_id=m.msg_id, src=m.src, dst=m.dst,
                        msg_type=m.msg_type, payload=m.payload,
                        delivered=(m.dst == f"F{i}" or m.delivered),
                    )
                    for m in ae_messages
                )
                ack = DSMessage(
                    msg_id=f"msg-{step}-F{i}-L0",
                    src=f"F{i}",
                    dst="L0",
                    msg_type="AppendEntriesAck",
                    payload=json.dumps({"term": 1, "success": True, "match_index": cmd_idx}),
                    delivered=False,
                )
                ack_msgs.append(ack)
                all_msgs = updated_ae + tuple(ack_msgs)
                majority = i + 2  # leader + i+1 followers
                ds = DistributedSystemState(
                    nodes=tuple(nodes),
                    messages=all_msgs,
                    event="append_ack",
                    description=(
                        f"F{i} appends log entry {cmd_idx} and sends ACK to L0. "
                        f"L0 has {majority}/5 confirmations."
                        + (" Majority reached!" if majority >= 3 else "")
                    ),
                )
                yield AlgorithmState(
                    step=step,
                    data={"log": list(current_log), "commit_index": commit_index, "pending_cmd": cmd},
                    visualization=ds,
                    is_complete=False,
                )

            # Phase D: Leader commits (majority = 3 of 5: leader + 2 followers)
            step += 1
            commit_index = cmd_idx
            leader_data = json.loads(nodes[0].data)
            leader_data["commit_index"] = commit_index
            nodes[0] = DSNode(
                node_id="L0",
                role="leader",
                term=1,
                log=tuple(current_log),
                inbox=(),
                data=json.dumps(leader_data),
            )
            # Notify followers of commit via next AppendEntries (leader_commit updated)
            ds = DistributedSystemState(
                nodes=tuple(nodes),
                messages=(),
                event="committed",
                description=(
                    f"L0 commits log entry {cmd_idx} (command='{cmd}'). "
                    f"commit_index={commit_index}. Responds SUCCESS to client."
                ),
            )
            yield AlgorithmState(
                step=step,
                data={"log": list(current_log), "commit_index": commit_index, "pending_cmd": None},
                visualization=ds,
                is_complete=(cmd_idx == len(COMMANDS) - 1),
            )

        # Final committed state
        step += 1
        final_nodes = tuple(
            DSNode(
                node_id=n.node_id,
                role=n.role,
                term=1,
                log=tuple(current_log),
                inbox=(),
                data=json.dumps({"commit_index": commit_index}),
            )
            for n in nodes
        )
        ds = DistributedSystemState(
            nodes=final_nodes,
            messages=(),
            event="replication_complete",
            description=(
                f"All {len(COMMANDS)} commands committed and replicated to all followers. "
                "Log is consistent across the cluster."
            ),
        )
        yield AlgorithmState(
            step=step,
            data={"log": list(current_log), "commit_index": commit_index, "pending_cmd": None},
            visualization=ds,
            is_complete=True,
        )
