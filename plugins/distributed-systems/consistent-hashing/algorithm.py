import json
from typing import Generator
from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, AlgorithmState
from algorithm_atlas_sdk import DistributedSystemState, DSNode, DSMessage
from algorithm_atlas_sdk.types import SimulationParams


class ConsistentHashing(AlgorithmPlugin):
    def metadata(self):
        return AlgorithmMetadata(
            slug="consistent-hashing",
            name="Consistent Hashing",
            category="distributed-systems",
            visualization_type="NETWORK_TOPOLOGY",
            description="Consistent hashing ring: keys are assigned to the next clockwise server. Adding/removing a server only remaps 1/n keys.",
            complexity_time_best="O(log n)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(log n)",
            complexity_space="O(n + k)",
            tags=["distributed", "hashing", "load-balancing", "scalability"],
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> AlgorithmState:
        # 4 servers at positions 0, 90, 180, 270 on a 0-359 ring
        servers = {"S0": 0, "S1": 90, "S2": 180, "S3": 270}
        # 8 keys at various positions
        keys = {f"K{i}": (i * 37 + 11) % 360 for i in range(8)}
        nodes = [DSNode(nid, "server", pos // 10, (), (),
                        json.dumps({"pos": pos, "type": "server"}))
                 for nid, pos in servers.items()]
        nodes += [DSNode(nid, "key", pos // 10, (), (),
                         json.dumps({"pos": pos, "type": "key"}))
                  for nid, pos in keys.items()]
        return DistributedSystemState(
            nodes=tuple(nodes), messages=(),
            event="init",
            description="4 servers on consistent hash ring (positions 0°,90°,180°,270°). 8 keys to be assigned.",
        )

    def _assign(self, servers, keys):
        """Assign each key to its successor server on the ring."""
        sorted_servers = sorted(servers.items(), key=lambda x: x[1])
        assignments = {}
        for kname, kpos in keys.items():
            # Find first server with pos >= kpos (clockwise)
            succ = None
            for sname, spos in sorted_servers:
                if spos >= kpos:
                    succ = sname; break
            if succ is None:
                succ = sorted_servers[0][0]  # wrap around
            assignments[kname] = succ
        return assignments

    def steps(self, state: AlgorithmState) -> Generator[AlgorithmState, None, AlgorithmState]:
        servers = {"S0": 0, "S1": 90, "S2": 180, "S3": 270}
        keys = {f"K{i}": (i * 37 + 11) % 360 for i in range(8)}
        history = []
        step = 0

        def mk_nodes(assign=None):
            nlist = []
            for nid, pos in servers.items():
                owned = [k for k, s in (assign or {}).items() if s == nid]
                nlist.append(DSNode(nid, "server", len(owned), tuple(owned),
                                    (), json.dumps({"pos": pos, "keys": owned})))
            for nid, pos in keys.items():
                owner = (assign or {}).get(nid, "?")
                nlist.append(DSNode(nid, "key", pos // 10, (),
                                    (), json.dumps({"pos": pos, "owner": owner})))
            return tuple(nlist)

        # Show key assignments one by one
        assign = self._assign(servers, keys)
        for kname, kpos in keys.items():
            step += 1
            owner = assign[kname]
            msg = DSMessage(f"m{step}-{kname}-{owner}", kname, owner,
                            "Assign", f"key@{kpos}°", False)
            history.append(msg)
            yield DistributedSystemState(
                nodes=mk_nodes({k: assign[k] for k in list(keys.keys())[:step]}),
                messages=tuple(history),
                event=f"assign_{kname}",
                description=f"{kname} (pos={kpos}°) → {owner} (pos={servers[owner]}°). "
                            f"Next server clockwise from {kpos}°.")

        # Mark all assigned
        for i in range(len(history)):
            m = history[i]
            history[i] = DSMessage(m.msg_id, m.src, m.dst, m.msg_type, m.payload, True)

        yield DistributedSystemState(
            nodes=mk_nodes(assign), messages=tuple(history),
            event="assignment_complete",
            description=f"All 8 keys assigned. Distribution: "
                        + ", ".join(f"{s}:{sum(1 for k,v in assign.items() if v==s)}" for s in servers) + " keys.")

        # Now add a new server S4 at position 135
        step += 1
        new_server = "S4"
        servers[new_server] = 135
        new_assign = self._assign(servers, keys)
        remapped = [k for k in keys if assign[k] != new_assign[k]]

        remap_msgs = [DSMessage(f"m{step+i}-{k}-{new_server}", k, new_server,
                               "Remap", f"was {assign[k]}", False)
                     for i, k in enumerate(remapped)]
        history.extend(remap_msgs)

        yield DistributedSystemState(
            nodes=mk_nodes(new_assign), messages=tuple(history),
            event="server_added",
            description=f"S4 joins at 135°. Only {len(remapped)} key(s) remapped: "
                        f"{', '.join(remapped)}. Other keys unchanged — consistent hashing property!")

        final = DistributedSystemState(
            nodes=mk_nodes(new_assign), messages=tuple(history),
            event="done",
            description="Consistent hashing ensures minimal disruption when servers join/leave.")
        return final
