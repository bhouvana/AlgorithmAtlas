import json
from typing import Generator
from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, AlgorithmState
from algorithm_atlas_sdk import DistributedSystemState, DSNode, DSMessage
from algorithm_atlas_sdk.types import SimulationParams


class ChordDHT(AlgorithmPlugin):
    def metadata(self):
        return AlgorithmMetadata(
            slug="chord-dht",
            name="Chord DHT",
            category="distributed-systems",
            visualization_type="NETWORK_TOPOLOGY",
            description="Chord distributed hash table: nodes arranged in a ring, lookups follow finger table pointers in O(log n) hops.",
            complexity_time_best="O(1)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(log n)",
            tags=["distributed", "dht", "chord", "peer-to-peer", "consistent-hashing"],
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> AlgorithmState:
        # 8-node Chord ring with m=3 (IDs 0-7)
        node_ids = [0, 1, 3, 5, 6, 7]  # 6 nodes in ring; gaps at 2, 4
        nodes = [DSNode(f"N{nid}", "chord_node", nid, (), (),
                        json.dumps({"id": nid, "role": "node"}))
                 for nid in node_ids]
        return DistributedSystemState(
            nodes=tuple(nodes), messages=(),
            event="init",
            description="6-node Chord ring, m=3 bits (IDs 0-7). Looking up key K=4 starting from N1.")

    def _successor(self, node_ids, k):
        """Find the successor of key k in sorted ring."""
        sorted_ids = sorted(node_ids)
        for nid in sorted_ids:
            if nid >= k:
                return nid
        return sorted_ids[0]  # wrap around

    def _finger_table(self, n, node_ids, m=3):
        """Finger table for node n: entry i = successor(n + 2^i mod 2^m)."""
        ring_size = 2 ** m
        return {i: self._successor(node_ids, (n + 2**i) % ring_size)
                for i in range(m)}

    def steps(self, state: AlgorithmState) -> Generator[AlgorithmState, None, AlgorithmState]:
        node_ids = [0, 1, 3, 5, 6, 7]
        m = 3
        ring_size = 2 ** m  # 8
        lookup_key = 4
        start_node = 1
        history = []
        step = [0]

        def nxt():
            step[0] += 1
            return step[0]

        def mk_nodes(active_node=None, found=False):
            nodes = []
            for nid in node_ids:
                ft = self._finger_table(nid, node_ids, m)
                role = ("found" if found and nid == active_node
                        else "active" if nid == active_node
                        else "chord_node")
                nodes.append(DSNode(
                    f"N{nid}", role, nid, (), (),
                    json.dumps({"id": nid, "finger_table": ft})))
            return tuple(nodes)

        # Show the ring topology
        yield DistributedSystemState(
            nodes=mk_nodes(start_node), messages=(),
            event="ring_built",
            description=f"Chord ring built. Nodes: {sorted(node_ids)}. "
                        f"Key={lookup_key} → successor is N{self._successor(node_ids, lookup_key)}. "
                        f"Starting lookup at N{start_node}.")

        # Show finger table for start node
        ft_start = self._finger_table(start_node, node_ids, m)
        yield DistributedSystemState(
            nodes=mk_nodes(start_node), messages=(),
            event="finger_table",
            description=f"N{start_node} finger table: "
                        + ", ".join(f"FT[{i}]=N{ft_start[i]}" for i in range(m))
                        + f". Finger entries point to successor(N{start_node}+2^i).")

        # Lookup traversal: from N1 find K=4
        current = start_node
        path = [current]

        # Hop 1: N1 checks finger table — FT[1]=N3 (1+2=3), FT[2]=N5 (1+4=5 mod 8)
        # Largest finger ≤ K=4 is N3 (FT[1]=3, 3 ≤ 4)
        ft_1 = self._finger_table(1, node_ids, m)
        best = 1
        for i in range(m):
            f = ft_1[i]
            if f <= lookup_key and (f > best or best == 1):
                best = f
        hop1 = best if best != current else ft_1[0]
        # Actually use correct Chord forward: find largest finger id < key
        candidates = [(ft_1[i], i) for i in range(m) if ft_1[i] < lookup_key]
        if candidates:
            hop1 = max(candidates, key=lambda x: x[0])[0]
        else:
            hop1 = start_node

        if hop1 != current:
            msg1 = DSMessage(f"m{nxt()}-N{current}-N{hop1}", f"N{current}", f"N{hop1}",
                             "Lookup", f"key={lookup_key}")
            history.append(msg1)
            yield DistributedSystemState(
                nodes=mk_nodes(hop1), messages=tuple(history),
                event=f"hop_to_N{hop1}",
                description=f"N{current}: largest finger < {lookup_key} is N{hop1}. "
                            f"Forwarding lookup to N{hop1}.")
            idx = next(j for j, m_ in enumerate(history) if m_.msg_id == msg1.msg_id)
            history[idx] = DSMessage(msg1.msg_id, msg1.src, msg1.dst, msg1.msg_type,
                                     msg1.payload, True)
            current = hop1
            path.append(current)

        # Hop 2: from current node, check if successor holds the key
        ft_cur = self._finger_table(current, node_ids, m)
        succ_of_cur = self._successor(node_ids, current + 1)
        # If successor >= key, we're done next hop
        if succ_of_cur >= lookup_key or current >= lookup_key:
            final_node = self._successor(node_ids, lookup_key)
        else:
            # One more hop
            candidates2 = [(ft_cur[i], i) for i in range(m) if ft_cur[i] < lookup_key]
            if candidates2:
                hop2 = max(candidates2, key=lambda x: x[0])[0]
                msg2 = DSMessage(f"m{nxt()}-N{current}-N{hop2}", f"N{current}", f"N{hop2}",
                                 "Lookup", f"key={lookup_key}")
                history.append(msg2)
                yield DistributedSystemState(
                    nodes=mk_nodes(hop2), messages=tuple(history),
                    event=f"hop_to_N{hop2}",
                    description=f"N{current}: still not reached key={lookup_key}. Forwarding to N{hop2}.")
                idx = next(j for j, m_ in enumerate(history) if m_.msg_id == msg2.msg_id)
                history[idx] = DSMessage(msg2.msg_id, msg2.src, msg2.dst, msg2.msg_type,
                                         msg2.payload, True)
                current = hop2
                path.append(current)
            final_node = self._successor(node_ids, lookup_key)

        # Final hop: current node → successor of key
        final_node = self._successor(node_ids, lookup_key)
        if current != final_node:
            msg_final = DSMessage(f"m{nxt()}-N{current}-N{final_node}", f"N{current}",
                                  f"N{final_node}", "Found", f"key={lookup_key}")
            history.append(msg_final)
            path.append(final_node)
            yield DistributedSystemState(
                nodes=mk_nodes(final_node, found=True), messages=tuple(history),
                event="found",
                description=f"N{current} sees successor N{final_node} ≥ key={lookup_key}. "
                            f"Key={lookup_key} is stored at N{final_node}!")
        else:
            yield DistributedSystemState(
                nodes=mk_nodes(current, found=True), messages=tuple(history),
                event="found",
                description=f"Key={lookup_key} found at N{current} in {len(path)-1} hops!")

        final = DistributedSystemState(
            nodes=mk_nodes(final_node, found=True), messages=tuple(history),
            event="done",
            description=f"Chord lookup complete. Path: {' → '.join('N'+str(p) for p in path)} → N{final_node}. "
                        f"O(log n) = O({m}) hops in a ring of {len(node_ids)} nodes.")
        yield final
        return final
