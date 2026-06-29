"""
Raft Leader Election plugin for Algorithm Atlas.
Simulates a 5-node Raft cluster going through a leader election.
Visualization: NETWORK_TOPOLOGY
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


class RaftLeaderElection(AlgorithmPlugin):
    def metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="raft-leader-election",
            name="Raft Leader Election",
            category="distributed-systems",
            visualization_type="NETWORK_TOPOLOGY",
            description=(
                "Demonstrates the Raft consensus leader election algorithm. "
                "Five nodes start as followers. One node times out, becomes a candidate, "
                "solicits votes, and a majority wins making it the leader."
            ),
            time_complexity="O(n)",
            space_complexity="O(n)",
            tags=("distributed", "consensus", "raft", "election"),
        )

    def initialize(self, params: dict, seed: int) -> AlgorithmState:
        random.seed(seed)
        # All 5 nodes start as followers at term 0
        nodes = tuple(
            DSNode(
                node_id=f"N{i}",
                role="follower",
                term=0,
                log=(),
                inbox=(),
                data=json.dumps({"votes_received": 0, "voted_for": None}),
            )
            for i in range(5)
        )
        ds_state = DistributedSystemState(
            nodes=nodes,
            messages=(),
            event="init",
            description="All 5 nodes start as followers at term 0. Waiting for heartbeat timeout.",
        )
        return AlgorithmState(
            step=0,
            data={"phase": "follower_wait", "candidate": None, "votes": {}, "leader": None},
            visualization=ds_state,
            is_complete=False,
        )

    def steps(self, state: AlgorithmState) -> Generator[AlgorithmState, None, None]:
        step = state.step
        ds: DistributedSystemState = state.visualization

        # --- Phase 0: Node N2 times out and becomes candidate ---
        # Step 1: N2 times out
        step += 1
        candidate_id = "N2"
        new_term = 1
        nodes = tuple(
            DSNode(
                node_id=n.node_id,
                role="candidate" if n.node_id == candidate_id else "follower",
                term=new_term if n.node_id == candidate_id else n.term,
                log=n.log,
                inbox=n.inbox,
                data=json.dumps({"votes_received": 1, "voted_for": candidate_id})
                if n.node_id == candidate_id
                else json.dumps({"votes_received": 0, "voted_for": None}),
            )
            for n in ds.nodes
        )
        ds = DistributedSystemState(
            nodes=nodes,
            messages=(),
            event="timeout",
            description=f"N2 election timeout fires. N2 increments term to {new_term} and becomes candidate. N2 votes for itself.",
        )
        yield AlgorithmState(
            step=step,
            data={"phase": "candidacy", "candidate": candidate_id, "votes": {"N2": True}, "leader": None},
            visualization=ds,
            is_complete=False,
        )

        # Step 2: N2 sends RequestVote to all other nodes
        step += 1
        other_nodes = [n.node_id for n in nodes if n.node_id != candidate_id]
        vote_messages = tuple(
            DSMessage(
                msg_id=f"msg-{step}-{candidate_id}-{dst}",
                src=candidate_id,
                dst=dst,
                msg_type="RequestVote",
                payload=json.dumps({"term": new_term, "candidate_id": candidate_id}),
                delivered=False,
            )
            for dst in other_nodes
        )
        ds = DistributedSystemState(
            nodes=nodes,
            messages=vote_messages,
            event="request_vote_sent",
            description=f"N2 broadcasts RequestVote(term={new_term}) to N0, N1, N3, N4.",
        )
        yield AlgorithmState(
            step=step,
            data={"phase": "request_vote", "candidate": candidate_id, "votes": {"N2": True}, "leader": None},
            visualization=ds,
            is_complete=False,
        )

        # Steps 3-6: Each node receives and responds to RequestVote
        votes = {"N2": True}
        current_messages = list(vote_messages)
        for i, dst in enumerate(other_nodes):
            step += 1
            # Mark this message as delivered
            updated_msgs = tuple(
                DSMessage(
                    msg_id=m.msg_id,
                    src=m.src,
                    dst=m.dst,
                    msg_type=m.msg_type,
                    payload=m.payload,
                    delivered=(m.dst == dst or m.delivered),
                )
                for m in current_messages
            )
            # Node grants vote (all grant in a clean election)
            votes[dst] = True
            # Update dst node: set voted_for, update term
            nodes = tuple(
                DSNode(
                    node_id=n.node_id,
                    role=n.role,
                    term=new_term,
                    log=n.log,
                    inbox=(),
                    data=json.dumps({"votes_received": n.node_id == candidate_id and len(votes) or 0,
                                     "voted_for": candidate_id if n.node_id == dst else
                                     (json.loads(n.data).get("voted_for"))})
                    if n.node_id != candidate_id else
                    json.dumps({"votes_received": len(votes), "voted_for": candidate_id}),
                )
                for n in nodes
            )
            # Add VoteGranted reply message
            reply = DSMessage(
                msg_id=f"msg-{step}-{dst}-{candidate_id}",
                src=dst,
                dst=candidate_id,
                msg_type="VoteGranted",
                payload=json.dumps({"term": new_term, "vote_granted": True}),
                delivered=False,
            )
            all_msgs = updated_msgs + (reply,)
            ds = DistributedSystemState(
                nodes=nodes,
                messages=all_msgs,
                event="vote_granted",
                description=f"{dst} receives RequestVote, grants vote to N2. N2 now has {len(votes)}/5 votes.",
            )
            yield AlgorithmState(
                step=step,
                data={"phase": "collecting_votes", "candidate": candidate_id, "votes": dict(votes), "leader": None},
                visualization=ds,
                is_complete=False,
            )
            current_messages = list(all_msgs)

        # Step 7: N2 has majority (3+ votes) — becomes leader
        step += 1
        nodes = tuple(
            DSNode(
                node_id=n.node_id,
                role="leader" if n.node_id == candidate_id else "follower",
                term=new_term,
                log=n.log,
                inbox=(),
                data=json.dumps({"votes_received": len(votes), "voted_for": candidate_id})
                if n.node_id == candidate_id
                else json.dumps({"voted_for": candidate_id}),
            )
            for n in nodes
        )
        ds = DistributedSystemState(
            nodes=nodes,
            messages=(),
            event="leader_elected",
            description=f"N2 received {len(votes)}/5 votes (majority). N2 is now the LEADER for term {new_term}.",
        )
        yield AlgorithmState(
            step=step,
            data={"phase": "leader_elected", "candidate": candidate_id, "votes": dict(votes), "leader": candidate_id},
            visualization=ds,
            is_complete=False,
        )

        # Steps 8-12: Leader sends initial heartbeat (empty AppendEntries) to all followers
        step += 1
        follower_ids = [n.node_id for n in nodes if n.node_id != candidate_id]
        heartbeat_msgs = tuple(
            DSMessage(
                msg_id=f"msg-{step}-{candidate_id}-{dst}",
                src=candidate_id,
                dst=dst,
                msg_type="AppendEntries",
                payload=json.dumps({"term": new_term, "entries": [], "leader_id": candidate_id}),
                delivered=False,
            )
            for dst in follower_ids
        )
        ds = DistributedSystemState(
            nodes=nodes,
            messages=heartbeat_msgs,
            event="heartbeat_sent",
            description=f"Leader N2 sends initial heartbeat (empty AppendEntries) to all followers to assert authority.",
        )
        yield AlgorithmState(
            step=step,
            data={"phase": "heartbeat", "candidate": candidate_id, "votes": dict(votes), "leader": candidate_id},
            visualization=ds,
            is_complete=False,
        )

        # Steps 13-16: Followers acknowledge heartbeat
        current_hb = list(heartbeat_msgs)
        for i, dst in enumerate(follower_ids):
            step += 1
            updated_hb = tuple(
                DSMessage(
                    msg_id=m.msg_id, src=m.src, dst=m.dst,
                    msg_type=m.msg_type, payload=m.payload,
                    delivered=(m.dst == dst or m.delivered),
                )
                for m in current_hb
            )
            ack = DSMessage(
                msg_id=f"msg-{step}-{dst}-{candidate_id}",
                src=dst,
                dst=candidate_id,
                msg_type="AppendEntriesAck",
                payload=json.dumps({"term": new_term, "success": True}),
                delivered=False,
            )
            all_hb = updated_hb + (ack,)
            ds = DistributedSystemState(
                nodes=nodes,
                messages=all_hb,
                event="heartbeat_ack",
                description=f"{dst} acknowledges heartbeat from leader N2. Follower confirms term {new_term}.",
            )
            yield AlgorithmState(
                step=step,
                data={"phase": "stabilizing", "candidate": candidate_id, "votes": dict(votes), "leader": candidate_id},
                visualization=ds,
                is_complete=False,
            )
            current_hb = list(all_hb)

        # Final step: Cluster stable
        step += 1
        ds = DistributedSystemState(
            nodes=nodes,
            messages=(),
            event="election_complete",
            description=(
                f"Election complete. N2 is the stable leader for term {new_term}. "
                "All followers have acknowledged heartbeat. Cluster is ready to serve client requests."
            ),
        )
        yield AlgorithmState(
            step=step,
            data={"phase": "complete", "candidate": candidate_id, "votes": dict(votes), "leader": candidate_id},
            visualization=ds,
            is_complete=True,
        )
