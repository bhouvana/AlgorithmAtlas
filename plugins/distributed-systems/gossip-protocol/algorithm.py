import json
import random
from typing import Generator
from algorithm_atlas_sdk import AlgorithmMetadata, AlgorithmPlugin, AlgorithmState
from algorithm_atlas_sdk import DistributedSystemState, DSNode, DSMessage
from algorithm_atlas_sdk.types import SimulationParams


class GossipProtocol(AlgorithmPlugin):
    def metadata(self):
        return AlgorithmMetadata(
            slug="gossip-protocol",
            name="Gossip Protocol",
            category="distributed-systems",
            visualization_type="NETWORK_TOPOLOGY",
            description="Epidemic gossip protocol: one infected node spreads a rumor to random neighbors until all nodes know.",
            complexity_time_best="O(log n)",
            complexity_time_average="O(log n)",
            complexity_time_worst="O(n log n)",
            complexity_space="O(n)",
            tags=["distributed", "gossip", "epidemic", "information-dissemination"],
            execution_target="server",
        )

    def initialize(self, params: SimulationParams) -> AlgorithmState:
        random.seed(params.seed)
        n = params.inputs.get("nodes", 6)
        nodes = []
        for i in range(n):
            role = "infected" if i == 0 else "susceptible"
            data = json.dumps({"knows_rumor": i == 0, "heard_from": "origin" if i == 0 else None})
            nodes.append(DSNode(node_id=f"N{i}", role=role, term=0,
                                log=("knows rumor",) if i == 0 else (),
                                inbox=(), data=data))
        return DistributedSystemState(
            nodes=tuple(nodes), messages=(),
            event="init",
            description=f"N0 originates a rumor. {n-1} nodes are susceptible. Gossip begins.",
        )

    def steps(self, state: AlgorithmState) -> Generator[AlgorithmState, None, AlgorithmState]:
        nodes = list(state.nodes)
        n = len(nodes)
        infected = {0}
        step = 0

        while len(infected) < n and step < 30:
            step += 1
            # Each infected node picks a random neighbor to gossip to
            msgs = []
            new_infected = set()
            for i in sorted(infected):
                candidates = [j for j in range(n) if j != i]
                if not candidates:
                    continue
                target = random.choice(candidates)
                msgs.append(DSMessage(
                    msg_id=f"g{step}-{i}-{target}",
                    src=f"N{i}", dst=f"N{target}",
                    msg_type="Gossip",
                    payload="rumor",
                    delivered=False,
                ))
                if target not in infected:
                    new_infected.add(target)

            infected |= new_infected

            updated_nodes = []
            for i, node in enumerate(nodes):
                role = "infected" if i in infected else "susceptible"
                knows = i in infected
                updated_nodes.append(DSNode(
                    node_id=node.node_id, role=role, term=step,
                    log=("knows rumor",) if knows else (),
                    inbox=(), data=json.dumps({"knows_rumor": knows}),
                ))
            nodes = updated_nodes

            yield DistributedSystemState(
                nodes=tuple(nodes), messages=tuple(msgs),
                event=f"gossip_round_{step}",
                description=f"Round {step}: {len(infected)}/{n} nodes infected. "
                            + (f"Newly told: {', '.join(f'N{j}' for j in sorted(new_infected))}" if new_infected else "No new infections this round."),
            )

        yield DistributedSystemState(
            nodes=tuple(nodes), messages=(),
            event="gossip_complete",
            description=f"All {n} nodes know the rumor after {step} rounds. "
                        f"Gossip protocols achieve O(log n) spread.",
        )
        return DistributedSystemState(
            nodes=tuple(nodes), messages=(),
            event="done", description="Gossip fully propagated.",
        )
