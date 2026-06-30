import type { LessonData } from '../../lessons/GenericLesson';

export const graphsDpLessons: Record<string, LessonData> = {

  'graph-representation': {
    concept: {
      overview:
        'A graph is a collection of vertices (nodes) connected by edges. The two most common representations are the adjacency matrix and the adjacency list, each with different space/time trade-offs. Choosing the right representation is the first critical decision in any graph algorithm.',
      keyPoints: [
        { title: 'Adjacency List', desc: 'An array where each index i holds a list of neighbors of vertex i. Uses O(V+E) space — ideal for sparse graphs where E << V².' },
        { title: 'Adjacency Matrix', desc: 'A V×V 2D array where matrix[u][v] = 1 if edge exists. Uses O(V²) space but allows O(1) edge existence checks. Best for dense graphs.' },
        { title: 'Edge List', desc: 'A flat list of (u, v, weight) tuples. Minimal representation used in algorithms like Kruskal\'s MST that process edges directly.' },
      ],
    },
    steps: [
      { n: '1', label: 'Define V vertices', desc: 'Label vertices 0 to V-1 (or use named keys). Determine whether the graph is directed or undirected.' },
      { n: '2', label: 'Choose representation', desc: 'Sparse graphs (social networks, road maps) → adjacency list. Dense graphs or frequent edge queries → adjacency matrix.' },
      { n: '3', label: 'Build adjacency list', desc: 'Create array of size V. For each edge (u,v), append v to adj[u]. For undirected, also append u to adj[v].', code: 'adj = [[] for _ in range(V)]\nfor u, v in edges:\n    adj[u].append(v)' },
      { n: '4', label: 'Build adjacency matrix', desc: 'Create V×V matrix of zeros. For each edge (u,v) set matrix[u][v]=1.', code: 'matrix = [[0]*V for _ in range(V)]\nfor u, v in edges:\n    matrix[u][v] = 1' },
      { n: '5', label: 'Add edge weights', desc: 'For weighted graphs, store weights: adj[u].append((v, weight)) or matrix[u][v] = weight instead of 1.' },
    ],
    codeExamples: [
      {
        label: 'Adjacency List (sparse graph)',
        complexity: 'O(V+E) space',
        code: 'def build_adj_list(V, edges):\n    adj = [[] for _ in range(V)]\n    for u, v in edges:\n        adj[u].append(v)\n        adj[v].append(u)  # undirected\n    return adj\n\n# Access neighbors of node 2:\n# for neighbor in adj[2]: ...',
      },
      {
        label: 'Adjacency Matrix (dense graph)',
        complexity: 'O(V²) space',
        code: 'def build_adj_matrix(V, edges):\n    mat = [[0]*V for _ in range(V)]\n    for u, v, w in edges:\n        mat[u][v] = w\n        mat[v][u] = w  # undirected\n    return mat\n\n# Check edge in O(1):\n# if mat[u][v] != 0: ...',
      },
    ],
    complexity: {
      rows: [
        { case: 'Adj List — space', value: 'O(V+E)', color: 'text-indigo-400', note: 'One entry per vertex + one per directed edge' },
        { case: 'Adj Matrix — space', value: 'O(V²)', color: 'text-orange-400', note: 'Full V×V grid regardless of edge count' },
        { case: 'Check edge (list)', value: 'O(degree)', color: 'text-amber-400', note: 'Must scan neighbor list' },
        { case: 'Check edge (matrix)', value: 'O(1)', color: 'text-emerald-400', note: 'Direct array index lookup' },
      ],
    },
    realWorld: [
      { title: 'Social Networks', desc: 'Facebook friendship graph: sparse (each person has few friends vs millions of users) → adjacency list.' },
      { title: 'Road Maps', desc: 'City road networks: sparse (each intersection connects to few roads) → adjacency list for Dijkstra.' },
      { title: 'Dense Connectivity', desc: 'Flight route matrices between all major airports: adjacency matrix for quick route existence checks.' },
      { title: 'Dependency Graphs', desc: 'Package managers (npm, pip) store directed edges from package to its dependencies in an adjacency list.' },
    ],
    quiz: [
      { q: 'Which representation is better for a sparse graph with 1000 nodes but only 2000 edges?', options: ['Adjacency Matrix', 'Adjacency List', 'Both are equivalent', 'Edge weights matrix'], correct: 1, explanation: 'Adjacency list uses O(V+E) = O(3000) space vs O(V²) = O(1,000,000) for matrix.' },
      { q: 'What is the time complexity of checking if an edge (u,v) exists in an adjacency matrix?', options: ['O(n)', 'O(log n)', 'O(1)', 'O(degree)'], correct: 2, explanation: 'Direct index: matrix[u][v] is a constant-time array lookup.' },
      { q: 'In an undirected graph with adjacency list, adding edge (u,v) requires:', options: ['adj[u].append(v) only', 'adj[v].append(u) only', 'Both adj[u].append(v) and adj[v].append(u)', 'Creating a new node'], correct: 2, explanation: 'Undirected edges must be represented in both directions.' },
      { q: 'What is the space complexity of an edge list representation for a graph with V vertices and E edges?', options: ['O(V²)', 'O(V+E)', 'O(E)', 'O(V)'], correct: 2, explanation: 'An edge list stores exactly one tuple per edge, so it uses O(E) space — no per-vertex entries needed.' },
      { q: 'For which operation is an adjacency matrix strictly better than an adjacency list?', options: ['Iterating over all neighbors of a node', 'Checking whether a specific edge (u,v) exists', 'Listing all edges in the graph', 'Adding a new vertex'], correct: 1, explanation: 'matrix[u][v] is an O(1) lookup, whereas an adjacency list requires scanning the neighbor list in O(degree).' },
      { q: 'A directed graph (digraph) with V=4 and E=6 is stored as an adjacency list. How many total entries are in all neighbor lists combined?', options: ['4', '6', '12', '16'], correct: 1, explanation: 'In a directed adjacency list each directed edge contributes exactly one entry, so total entries = E = 6.' },
    ],
  },

  'bfs': {
    concept: {
      overview:
        'Breadth-First Search (BFS) explores a graph level by level, visiting all neighbors of a node before moving to their neighbors. It uses a queue (FIFO) to guarantee that nodes closer to the source are always visited first. BFS finds the shortest path (fewest edges) between two nodes in an unweighted graph.',
      keyPoints: [
        { title: 'Queue-Based', desc: 'Uses a FIFO queue. Enqueue the start node, then repeatedly dequeue and enqueue unvisited neighbors. This naturally processes nodes in order of their distance from the source.' },
        { title: 'Shortest Path', desc: 'BFS guarantees the shortest path in terms of edge count for unweighted graphs. The first time BFS reaches a node, that path is optimal.' },
        { title: 'Level-by-Level', desc: 'All nodes at distance 1 are visited before distance 2, before distance 3, etc. BFS builds a BFS tree with layers.' },
      ],
    },
    steps: [
      { n: '1', label: 'Initialize', desc: 'Create a visited set, a queue, and optionally a distance array. Add the source node to both queue and visited.', code: 'queue = deque([start])\nvisited = {start}\ndist = {start: 0}' },
      { n: '2', label: 'Dequeue node', desc: 'Remove the front node from the queue and process it (print, record, check if target).' },
      { n: '3', label: 'Enqueue neighbors', desc: 'For each unvisited neighbor of the current node, mark it visited and add to queue with dist+1.', code: 'for neighbor in adj[node]:\n    if neighbor not in visited:\n        visited.add(neighbor)\n        dist[neighbor] = dist[node] + 1\n        queue.append(neighbor)' },
      { n: '4', label: 'Repeat until empty', desc: 'Continue until the queue is empty. All reachable nodes have been visited.' },
      { n: '5', label: 'Check connectivity', desc: 'If a target node was never visited, there is no path from source to target in the graph.' },
    ],
    codeExamples: [
      {
        label: 'BFS — Shortest Path',
        complexity: 'O(V+E)',
        code: 'from collections import deque\n\ndef bfs(adj, start, target):\n    queue = deque([start])\n    visited = {start}\n    dist = {start: 0}\n\n    while queue:\n        node = queue.popleft()\n        if node == target:\n            return dist[node]\n        for nbr in adj[node]:\n            if nbr not in visited:\n                visited.add(nbr)\n                dist[nbr] = dist[node] + 1\n                queue.append(nbr)\n    return -1  # not reachable',
      },
      {
        label: 'BFS — Level Order',
        complexity: 'O(V+E)',
        code: 'def bfs_levels(adj, start):\n    queue = deque([start])\n    visited = {start}\n    levels = []\n\n    while queue:\n        level_size = len(queue)\n        current_level = []\n        for _ in range(level_size):\n            node = queue.popleft()\n            current_level.append(node)\n            for nbr in adj[node]:\n                if nbr not in visited:\n                    visited.add(nbr)\n                    queue.append(nbr)\n        levels.append(current_level)\n    return levels',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time', value: 'O(V+E)', color: 'text-indigo-400', note: 'Each vertex and edge visited once' },
        { case: 'Space', value: 'O(V)', color: 'text-indigo-400', note: 'Queue and visited set hold up to V nodes' },
        { case: 'Shortest path', value: 'O(V+E)', color: 'text-indigo-400', note: 'Guaranteed optimal for unweighted graphs' },
      ],
    },
    realWorld: [
      { title: 'GPS Navigation', desc: 'Finding shortest route with fewest turns/roads in unweighted road graphs.' },
      { title: 'Social Networks', desc: 'LinkedIn "degrees of connection" — BFS finds the shortest path between two people.' },
      { title: 'Web Crawlers', desc: 'Google crawls the web level-by-level from seed URLs, discovering linked pages.' },
      { title: 'Network Broadcasting', desc: 'Broadcasting packets in a network layer by layer to all reachable nodes.' },
    ],
    quiz: [
      { q: 'What data structure does BFS use internally?', options: ['Stack', 'Queue', 'Priority Queue', 'Array'], correct: 1, explanation: 'BFS uses a FIFO queue to ensure nodes are visited in order of increasing distance.' },
      { q: 'What does BFS guarantee in an unweighted graph?', options: ['Minimum total weight path', 'Shortest path by edge count', 'All paths found', 'Topological order'], correct: 1, explanation: 'BFS explores level-by-level, so the first path found to any node uses the fewest edges.' },
      { q: 'What is the time complexity of BFS on a graph with V vertices and E edges?', options: ['O(V²)', 'O(V log V)', 'O(V+E)', 'O(E log E)'], correct: 2, explanation: 'Each vertex is enqueued and dequeued once (O(V)), each edge is examined once (O(E)).' },
      { q: 'In BFS, why must a node be marked visited when it is enqueued rather than when it is dequeued?', options: ['To save memory', 'To prevent the same node from being enqueued multiple times', 'Because dequeuing is slower', 'BFS does not require a visited set'], correct: 1, explanation: 'Marking at enqueue time prevents a node with multiple neighbors pointing to it from being added to the queue more than once, which would cause redundant processing.' },
      { q: 'Which of the following problems CANNOT be solved optimally using BFS alone?', options: ['Shortest path in an unweighted graph', 'Finding all nodes at distance k from a source', 'Shortest path in a weighted graph with varying edge costs', 'Detecting if a graph is bipartite'], correct: 2, explanation: 'BFS counts edges, not weights. For weighted shortest paths you need Dijkstra or Bellman-Ford.' },
      { q: 'BFS on a disconnected graph starting from node 0 will:', options: ['Throw an error', 'Visit all nodes in the graph', 'Visit only nodes reachable from node 0', 'Visit nodes in DFS order'], correct: 2, explanation: 'BFS explores only nodes reachable from the source. Nodes in other connected components are never enqueued.' },
    ],
  },

  'dfs': {
    concept: {
      overview:
        'Depth-First Search (DFS) explores as far down a branch as possible before backtracking, using a stack (or the call stack via recursion). Unlike BFS\'s level-by-level approach, DFS dives deep first. DFS is the foundation for cycle detection, topological ordering, and finding connected components.',
      keyPoints: [
        { title: 'Stack-Based', desc: 'Uses an explicit stack or recursion. Explores one branch completely before trying another. The call stack in recursive DFS acts as the implicit stack.' },
        { title: 'Backtracking', desc: 'When DFS reaches a dead end (all neighbors visited), it backtracks to the previous node and tries the next unvisited neighbor.' },
        { title: 'Applications', desc: 'Cycle detection (back edges in DFS tree), topological sort (reverse post-order), strongly connected components (Kosaraju\'s algorithm).' },
      ],
    },
    steps: [
      { n: '1', label: 'Mark and visit', desc: 'Mark the current node visited. Process it (print, record). Add to recursion stack if tracking cycles.', code: 'visited.add(node)' },
      { n: '2', label: 'Recurse on unvisited neighbors', desc: 'For each unvisited neighbor, call DFS recursively.', code: 'for nbr in adj[node]:\n    if nbr not in visited:\n        dfs(adj, nbr, visited)' },
      { n: '3', label: 'Backtrack', desc: 'When all neighbors are visited, return from the recursive call. This is the backtracking step — we return to the parent node automatically.' },
      { n: '4', label: 'Handle disconnected graphs', desc: 'Call DFS from each unvisited node to handle graphs with multiple connected components.', code: 'for v in range(V):\n    if v not in visited:\n        dfs(adj, v, visited)' },
    ],
    codeExamples: [
      {
        label: 'Recursive DFS',
        complexity: 'O(V+E)',
        code: 'def dfs(adj, node, visited):\n    visited.add(node)\n    print(node)  # process node\n\n    for neighbor in adj[node]:\n        if neighbor not in visited:\n            dfs(adj, neighbor, visited)\n\n# Start DFS from node 0:\nvisited = set()\ndfs(adj, 0, visited)',
      },
      {
        label: 'Iterative DFS (using stack)',
        complexity: 'O(V+E)',
        code: 'def dfs_iterative(adj, start):\n    visited = set()\n    stack = [start]\n\n    while stack:\n        node = stack.pop()\n        if node in visited:\n            continue\n        visited.add(node)\n        print(node)  # process\n        for nbr in adj[node]:\n            if nbr not in visited:\n                stack.append(nbr)\n    return visited',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time', value: 'O(V+E)', color: 'text-indigo-400', note: 'Each vertex and edge processed once' },
        { case: 'Space (recursive)', value: 'O(V)', color: 'text-indigo-400', note: 'O(V) recursion stack depth in worst case' },
        { case: 'Space (iterative)', value: 'O(V)', color: 'text-indigo-400', note: 'Explicit stack holds up to V nodes' },
      ],
    },
    realWorld: [
      { title: 'Maze Solving', desc: 'DFS explores one path to its end before backtracking — mirrors how humans solve mazes.' },
      { title: 'Cycle Detection', desc: 'Back edges (to ancestor in DFS tree) indicate cycles — used in dependency checkers.' },
      { title: 'Topological Sort', desc: 'Post-order DFS on a DAG gives reverse topological order — basis for build systems.' },
      { title: 'Connected Components', desc: 'Each DFS call from an unvisited node discovers one connected component of the graph.' },
    ],
    quiz: [
      { q: 'What is the key difference between DFS and BFS?', options: ['DFS uses a queue, BFS uses a stack', 'DFS uses a stack, BFS uses a queue', 'DFS is faster', 'DFS finds shortest paths'], correct: 1, explanation: 'DFS uses a stack (or recursion) exploring deep first. BFS uses a queue exploring wide first.' },
      { q: 'What does a back edge in a DFS tree indicate?', options: ['Disconnected component', 'Cycle in the graph', 'Shortest path', 'Tree edge'], correct: 1, explanation: 'A back edge points from a node to one of its ancestors in the DFS tree, indicating a cycle.' },
      { q: 'What is the space complexity of recursive DFS in the worst case?', options: ['O(1)', 'O(log V)', 'O(V)', 'O(E)'], correct: 2, explanation: 'In a degenerate graph (linear chain), the recursion stack can reach depth V.' },
      { q: 'What is a "tree edge" in the context of a DFS traversal?', options: ['An edge between two already-visited nodes', 'An edge that leads to a previously unvisited node', 'An edge connecting two different connected components', 'The first edge traversed in DFS'], correct: 1, explanation: 'A tree edge is one where DFS discovers a new (unvisited) node, making it part of the DFS spanning tree.' },
      { q: 'Iterative DFS using an explicit stack may visit nodes in a different order than recursive DFS. Why?', options: ['The stack reverses edge ordering compared to recursion', 'Iterative DFS skips visited nodes', 'Recursive DFS uses more memory', 'They always visit in the same order'], correct: 0, explanation: 'The explicit stack pushes all neighbors at once (last-pushed is first-explored), while recursion explores them in adjacency-list order one by one, leading to different traversal sequences.' },
      { q: 'DFS can be used to find strongly connected components (SCCs). Which algorithm uses two DFS passes for this?', options: ["Kruskal's", "Prim's", "Kosaraju's", "Dijkstra's"], correct: 2, explanation: "Kosaraju's algorithm runs DFS on the original graph to get finish times, then DFS on the transposed graph in reverse finish-time order to identify SCCs." },
    ],
  },

  'topological-sort': {
    concept: {
      overview:
        'Topological sort orders the vertices of a Directed Acyclic Graph (DAG) such that every directed edge (u→v) has u appearing before v in the ordering. It\'s only possible when the graph has no cycles. Two classic algorithms: Kahn\'s BFS-based approach (in-degree counting) and DFS post-order reversal.',
      keyPoints: [
        { title: 'DAG Only', desc: 'Topological sort is only defined for Directed Acyclic Graphs. Any cycle makes a valid ordering impossible — which is why cycle detection is often built in.' },
        { title: 'Kahn\'s Algorithm', desc: 'Uses BFS and in-degree counts. Start with nodes having in-degree 0, remove them and update neighbors\' in-degrees. If remaining nodes exist after, a cycle exists.' },
        { title: 'Multiple Orderings', desc: 'A DAG can have many valid topological orderings. Both Kahn\'s and DFS will find a valid one, but not necessarily the same one.' },
      ],
    },
    steps: [
      { n: '1', label: 'Compute in-degrees', desc: 'Count the number of incoming edges for each vertex.', code: 'in_degree = [0] * V\nfor u in range(V):\n    for v in adj[u]:\n        in_degree[v] += 1' },
      { n: '2', label: 'Enqueue zero in-degree nodes', desc: 'All nodes with no incoming edges can appear first in the ordering.', code: 'queue = deque([v for v in range(V) if in_degree[v] == 0])' },
      { n: '3', label: 'Process queue', desc: 'Dequeue node, add to result, decrement in-degree of all its neighbors.', code: 'while queue:\n    node = queue.popleft()\n    result.append(node)\n    for nbr in adj[node]:\n        in_degree[nbr] -= 1\n        if in_degree[nbr] == 0:\n            queue.append(nbr)' },
      { n: '4', label: 'Detect cycles', desc: 'If the result has fewer nodes than V, a cycle exists — some nodes were never added to queue.' },
    ],
    codeExamples: [
      {
        label: "Kahn's Algorithm (BFS)",
        complexity: 'O(V+E)',
        code: 'from collections import deque\n\ndef topological_sort(V, adj):\n    in_degree = [0] * V\n    for u in range(V):\n        for v in adj[u]:\n            in_degree[v] += 1\n\n    queue = deque([v for v in range(V) if in_degree[v] == 0])\n    result = []\n\n    while queue:\n        node = queue.popleft()\n        result.append(node)\n        for nbr in adj[node]:\n            in_degree[nbr] -= 1\n            if in_degree[nbr] == 0:\n                queue.append(nbr)\n\n    if len(result) != V:\n        return None  # cycle detected\n    return result',
      },
      {
        label: 'DFS Post-Order',
        complexity: 'O(V+E)',
        code: 'def topo_dfs(adj, V):\n    visited = set()\n    order = []\n\n    def dfs(node):\n        visited.add(node)\n        for nbr in adj[node]:\n            if nbr not in visited:\n                dfs(nbr)\n        order.append(node)  # post-order\n\n    for v in range(V):\n        if v not in visited:\n            dfs(v)\n\n    return order[::-1]  # reverse post-order',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time', value: 'O(V+E)', color: 'text-indigo-400', note: 'Every vertex and edge processed once' },
        { case: 'Space', value: 'O(V)', color: 'text-indigo-400', note: 'Queue/stack + in-degree array + result' },
      ],
    },
    realWorld: [
      { title: 'Build Systems', desc: 'Make, Gradle, and Bazel compile files in topological order — dependencies before dependents.' },
      { title: 'Package Managers', desc: 'npm install resolves a package dependency DAG topologically before installing.' },
      { title: 'Course Prerequisites', desc: 'University course catalogs enforce prerequisite chains — a topological ordering of courses.' },
      { title: 'Spreadsheets', desc: 'Excel evaluates cell formulas in topological order — referenced cells before the ones that use them.' },
    ],
    quiz: [
      { q: 'What type of graph is topological sort applicable to?', options: ['Any directed graph', 'Undirected graphs only', 'Directed Acyclic Graphs (DAGs)', 'Weighted graphs only'], correct: 2, explanation: 'Topological sort requires no cycles. A cycle makes total ordering impossible.' },
      { q: 'In Kahn\'s algorithm, how is a cycle detected?', options: ['By checking visited nodes', 'If result length < V after processing', 'By finding back edges', 'By checking in-degrees'], correct: 1, explanation: 'Nodes in a cycle always have in-degree > 0 and are never added to the queue, so they never appear in the result.' },
      { q: 'What is the time complexity of topological sort?', options: ['O(V²)', 'O(V log V)', 'O(V+E)', 'O(E log E)'], correct: 2, explanation: 'Each vertex is processed once (O(V)) and each edge is examined once (O(E)).' },
      { q: 'In the DFS post-order approach to topological sort, why is the result reversed at the end?', options: ['To alphabetize node labels', 'Because nodes are appended after all descendants are finished, so the first-finishing node should appear last', 'To match Kahn\'s algorithm output', 'Reversing is optional'], correct: 1, explanation: 'Post-order DFS appends a node after all its dependencies are done. Reversing gives the correct order where dependencies appear before dependents.' },
      { q: 'A DAG has 5 nodes and 4 edges. How many valid topological orderings can it have at minimum?', options: ['1', '2', '5', 'It depends on the graph structure'], correct: 3, explanation: 'The number of topological orderings depends entirely on how many nodes have equal in-degree choices at each step. A linear chain has exactly 1; a fully independent set of 5 nodes has 5! = 120.' },
      { q: 'Which real-world system directly relies on topological ordering to function correctly?', options: ['Social media feed ranking', 'Build systems like Make or Gradle', 'Binary search trees', 'Hash tables'], correct: 1, explanation: 'Build systems must compile source files in topological order so that each file\'s dependencies are compiled before the file itself.' },
    ],
  },

  'dijkstra': {
    concept: {
      overview:
        'Dijkstra\'s algorithm finds the shortest path from a single source to all other vertices in a weighted graph with non-negative edge weights. It works greedily — always processing the unvisited vertex with the smallest known distance. With a min-heap priority queue, it runs in O((V+E) log V).',
      keyPoints: [
        { title: 'Greedy Choice', desc: 'At each step, Dijkstra commits to the node with the smallest current distance. This greedy choice is safe because with non-negative weights, we can\'t improve a path later by going through more edges.' },
        { title: 'Priority Queue', desc: 'A min-heap extracts the minimum-distance unprocessed node in O(log V). Without it, the naive implementation is O(V²) with a linear scan.' },
        { title: 'No Negative Weights', desc: 'Dijkstra fails with negative edge weights because a shorter path via negative edges may exist after a node is finalized. Use Bellman-Ford for negative weights.' },
      ],
    },
    steps: [
      { n: '1', label: 'Initialize distances', desc: 'Set dist[source] = 0, all others = infinity. Add (0, source) to the min-heap.', code: 'dist = [float("inf")] * V\ndist[src] = 0\nheap = [(0, src)]' },
      { n: '2', label: 'Extract minimum', desc: 'Pop the node with smallest distance from the heap.', code: 'd, node = heapq.heappop(heap)' },
      { n: '3', label: 'Skip stale entries', desc: 'If d > dist[node], this is an outdated heap entry — skip it.', code: 'if d > dist[node]:\n    continue' },
      { n: '4', label: 'Relax neighbors', desc: 'For each neighbor, compute new distance through current node. If smaller than known, update and push to heap.', code: 'for nbr, weight in adj[node]:\n    new_dist = dist[node] + weight\n    if new_dist < dist[nbr]:\n        dist[nbr] = new_dist\n        heapq.heappush(heap, (new_dist, nbr))' },
      { n: '5', label: 'Repeat until heap empty', desc: 'Continue until all reachable nodes are finalized. dist[] now holds shortest distances from source.' },
    ],
    codeExamples: [
      {
        label: "Dijkstra's Algorithm",
        complexity: 'O((V+E) log V)',
        code: 'import heapq\n\ndef dijkstra(adj, src, V):\n    dist = [float("inf")] * V\n    dist[src] = 0\n    heap = [(0, src)]\n\n    while heap:\n        d, node = heapq.heappop(heap)\n        if d > dist[node]:\n            continue\n        for nbr, weight in adj[node]:\n            new_dist = dist[node] + weight\n            if new_dist < dist[nbr]:\n                dist[nbr] = new_dist\n                heapq.heappush(heap, (new_dist, nbr))\n\n    return dist  # shortest distances from src',
      },
      {
        label: 'Reconstruct Path',
        complexity: 'O(V)',
        code: 'def dijkstra_path(adj, src, target, V):\n    dist = [float("inf")] * V\n    prev = [-1] * V\n    dist[src] = 0\n    heap = [(0, src)]\n\n    while heap:\n        d, node = heapq.heappop(heap)\n        if d > dist[node]: continue\n        for nbr, w in adj[node]:\n            if dist[node] + w < dist[nbr]:\n                dist[nbr] = dist[node] + w\n                prev[nbr] = node\n                heapq.heappush(heap, (dist[nbr], nbr))\n\n    # Reconstruct path\n    path = []\n    node = target\n    while node != -1:\n        path.append(node)\n        node = prev[node]\n    return path[::-1]',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time (with heap)', value: 'O((V+E) log V)', color: 'text-amber-400', note: 'Each edge can cause a heap push: O(E log V)' },
        { case: 'Time (naive)', value: 'O(V²)', color: 'text-orange-400', note: 'Linear scan to find minimum each iteration' },
        { case: 'Space', value: 'O(V)', color: 'text-indigo-400', note: 'Distance array + heap of up to V entries' },
      ],
    },
    realWorld: [
      { title: 'GPS Navigation', desc: 'Google Maps and GPS devices run Dijkstra (or A*) to find shortest driving routes on road weight graphs.' },
      { title: 'Network Routing', desc: 'OSPF (Open Shortest Path First) protocol uses Dijkstra to compute routing tables in internet routers.' },
      { title: 'Flight Optimization', desc: 'Airlines compute cheapest or shortest-time flight paths on weighted route graphs.' },
      { title: 'Game Pathfinding', desc: 'A* algorithm (heuristic-augmented Dijkstra) powers NPC pathfinding in video games.' },
    ],
    quiz: [
      { q: 'Why doesn\'t Dijkstra\'s algorithm work with negative edge weights?', options: ['It cannot handle non-integer weights', 'A finalized node might later receive a shorter path via negative edges', 'It requires sorted edge lists', 'The heap cannot store negative values'], correct: 1, explanation: 'Dijkstra\'s greedy assumption (finalized distances cannot decrease) breaks with negative edges.' },
      { q: 'What data structure optimizes Dijkstra to O((V+E) log V)?', options: ['Stack', 'Queue', 'Min-heap priority queue', 'Hash table'], correct: 2, explanation: 'A min-heap extracts the minimum-distance node in O(log V), making V extractions O(V log V) and E relaxations O(E log V).' },
      { q: 'What does dist[v] represent after Dijkstra finishes?', options: ['Number of edges on path to v', 'Shortest distance from source to v', 'Number of paths to v', 'Maximum edge weight on path to v'], correct: 1, explanation: 'dist[v] is the length of the shortest weighted path from the source to vertex v.' },
      { q: 'In Dijkstra\'s algorithm with a min-heap, why do we check "if d > dist[node]: continue"?', options: ['To handle disconnected graphs', 'To skip outdated heap entries after a shorter path was already found', 'To avoid processing the source node twice', 'To detect negative cycles'], correct: 1, explanation: 'When a shorter path is found after a node was already pushed to the heap, the old entry becomes stale. The check discards these without reprocessing.' },
      { q: 'What is the time complexity of Dijkstra on a dense graph (E ≈ V²) using an adjacency matrix without a heap?', options: ['O(V log V)', 'O(V²)', 'O(V³)', 'O(E log E)'], correct: 1, explanation: 'The naive implementation scans all V vertices to find the minimum each iteration (V passes × V scan = O(V²)), which is optimal for dense graphs.' },
      { q: 'Which modification to Dijkstra\'s produces the A* search algorithm?', options: ['Adding negative weight support', 'Using a heuristic estimate of remaining distance to guide node selection', 'Running Dijkstra in reverse', 'Using BFS instead of a heap'], correct: 1, explanation: 'A* adds a heuristic h(n) to the priority key, so nodes that look closer to the goal are explored first, reducing unnecessary exploration.' },
    ],
  },

  'bellman-ford': {
    concept: {
      overview:
        'Bellman-Ford finds shortest paths from a single source to all vertices, correctly handling negative edge weights — something Dijkstra cannot do. It works by relaxing all edges V-1 times. A crucial bonus: running one more relaxation detects negative-weight cycles, which would otherwise make shortest paths undefined.',
      keyPoints: [
        { title: 'Handles Negatives', desc: 'Unlike Dijkstra, Bellman-Ford allows negative edge weights. This makes it suitable for problems like currency arbitrage where some "costs" represent gains.' },
        { title: 'V-1 Relaxations', desc: 'A shortest path in a V-node graph visits at most V-1 edges. So V-1 rounds of relaxing all edges is guaranteed to find all shortest paths.' },
        { title: 'Negative Cycle Detection', desc: 'If any distance decreases on the V-th relaxation pass, a negative cycle exists — one you could traverse forever to reduce path length.' },
      ],
    },
    steps: [
      { n: '1', label: 'Initialize', desc: 'Set dist[src]=0, all others = infinity.', code: 'dist = [float("inf")] * V\ndist[src] = 0' },
      { n: '2', label: 'Relax all edges V-1 times', desc: 'For each of V-1 iterations, try to improve every edge (u,v,w): if dist[u]+w < dist[v] update.', code: 'for _ in range(V-1):\n    for u, v, w in edges:\n        if dist[u] + w < dist[v]:\n            dist[v] = dist[u] + w' },
      { n: '3', label: 'Detect negative cycle', desc: 'Run one more relaxation. If any edge still improves, a negative cycle is present.', code: 'for u, v, w in edges:\n    if dist[u] + w < dist[v]:\n        return None  # negative cycle!' },
      { n: '4', label: 'Return distances', desc: 'If no negative cycle, dist[] holds correct shortest distances from source.' },
    ],
    codeExamples: [
      {
        label: 'Bellman-Ford Algorithm',
        complexity: 'O(VE)',
        code: 'def bellman_ford(V, edges, src):\n    dist = [float("inf")] * V\n    dist[src] = 0\n\n    # Relax all edges V-1 times\n    for _ in range(V - 1):\n        for u, v, w in edges:\n            if dist[u] != float("inf") and dist[u] + w < dist[v]:\n                dist[v] = dist[u] + w\n\n    # Check for negative cycles\n    for u, v, w in edges:\n        if dist[u] != float("inf") and dist[u] + w < dist[v]:\n            return None  # negative cycle detected\n\n    return dist',
      },
      {
        label: 'When to use Bellman-Ford vs Dijkstra',
        code: '# Use Bellman-Ford when:\n# - Graph has negative edge weights\n# - Need to detect negative cycles\n# - Graph is sparse (few edges)\n\n# Use Dijkstra when:\n# - All edges are non-negative\n# - Need better O((V+E) log V) performance\n# - Graph is large and dense\n\n# Bellman-Ford: O(VE)\n# Dijkstra:     O((V+E) log V)\n# For sparse graphs, both are similar.\n# For dense graphs, Dijkstra wins.',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time', value: 'O(VE)', color: 'text-orange-400', note: 'V-1 passes, each scanning all E edges' },
        { case: 'Space', value: 'O(V)', color: 'text-indigo-400', note: 'Distance array of size V' },
        { case: 'Dijkstra (comparison)', value: 'O((V+E) log V)', color: 'text-amber-400', note: 'Faster but only for non-negative weights' },
      ],
    },
    realWorld: [
      { title: 'Currency Arbitrage', desc: 'Negative-weight edges represent profitable currency exchange chains. Bellman-Ford detects profitable cycles.' },
      { title: 'Distance-Vector Routing', desc: 'RIP (Routing Information Protocol) uses a distributed version of Bellman-Ford for router communication.' },
      { title: 'Network Delay', desc: 'Computing minimum delay through networks where some links have latency benefits.' },
      { title: 'Scheduling with Constraints', desc: 'Difference constraints (xi - xj <= w) can be modeled as Bellman-Ford shortest path problems.' },
    ],
    quiz: [
      { q: 'How many relaxation iterations does Bellman-Ford perform?', options: ['V', 'V-1', 'E', 'E-1'], correct: 1, explanation: 'A shortest path visits at most V-1 edges, so V-1 full relaxation passes suffices.' },
      { q: 'How does Bellman-Ford detect negative cycles?', options: ['Counts visited nodes', 'Checks if distance decreases on V-th relaxation', 'Uses DFS back edges', 'Checks for infinite loops'], correct: 1, explanation: 'If the V-th relaxation still decreases any distance, a cycle with negative total weight exists.' },
      { q: 'When should you use Bellman-Ford instead of Dijkstra?', options: ['When the graph is dense', 'When edges have negative weights', 'When you need O(1) space', 'When the graph is undirected'], correct: 1, explanation: 'Dijkstra\'s greedy approach is invalid with negative weights; Bellman-Ford handles them correctly.' },
      { q: 'Why is Bellman-Ford guaranteed to find shortest paths after exactly V-1 relaxation rounds?', options: ['Because there are at most V-1 unique edge weights', 'Because the shortest simple path between any two nodes uses at most V-1 edges', 'Because V-1 is the maximum number of edges in any graph', 'Because the algorithm sorts edges after V-1 passes'], correct: 1, explanation: 'In a graph with V vertices, a path without cycles visits at most V-1 edges. After k passes, all shortest paths using ≤k edges are correctly computed.' },
      { q: 'What happens if you run Bellman-Ford on a graph with a positive-weight cycle?', options: ['It incorrectly reports negative infinity for some nodes', 'It terminates normally with correct shortest paths', 'It runs forever', 'It requires an extra relaxation pass to detect the cycle'], correct: 1, explanation: 'Positive cycles do not cause problems for Bellman-Ford — shortest paths simply avoid them. Only negative cycles make shortest paths undefined.' },
      { q: 'Bellman-Ford is used in the RIP (Routing Information Protocol). What distributed property makes it suitable?', options: ['It requires a central coordinator', 'Each router only needs local edge information and can exchange distance estimates with neighbors', 'It is faster than Dijkstra in all cases', 'It only works on undirected networks'], correct: 1, explanation: 'Bellman-Ford naturally distributes: each node relaxes edges to neighbors and propagates updates, matching how routers share routing table information.' },
    ],
  },

  'floyd-warshall': {
    concept: {
      overview:
        'Floyd-Warshall computes shortest paths between every pair of vertices in a weighted graph using dynamic programming. The key insight: the shortest path from i to j either goes directly or passes through some intermediate vertex k. By considering each vertex as an intermediate, we build up the answer iteratively. It runs in O(V³) and uses O(V²) space.',
      keyPoints: [
        { title: 'All-Pairs', desc: 'Unlike Dijkstra (single source) or Bellman-Ford (single source), Floyd-Warshall finds shortest paths between all V×V pairs simultaneously.' },
        { title: 'DP Recurrence', desc: 'dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]) for each intermediate vertex k. The answer after considering all k is the true shortest path.' },
        { title: 'Negative Cycles', desc: 'A negative cycle exists if dist[i][i] < 0 for any i after the algorithm completes. Paths through negative cycles are undefined.' },
      ],
    },
    steps: [
      { n: '1', label: 'Initialize distance matrix', desc: 'dist[i][j] = edge weight if edge exists, 0 if i==j, infinity otherwise.', code: 'dist = [[float("inf")]*V for _ in range(V)]\nfor i in range(V): dist[i][i] = 0\nfor u, v, w in edges: dist[u][v] = w' },
      { n: '2', label: 'Iterate over intermediates', desc: 'For each k from 0 to V-1, consider all (i,j) pairs and update via k.', code: 'for k in range(V):\n    for i in range(V):\n        for j in range(V):\n            if dist[i][k] + dist[k][j] < dist[i][j]:\n                dist[i][j] = dist[i][k] + dist[k][j]' },
      { n: '3', label: 'Check negative cycles', desc: 'If dist[i][i] < 0 for any i, there is a negative-weight cycle.', code: 'for i in range(V):\n    if dist[i][i] < 0:\n        return None  # negative cycle' },
      { n: '4', label: 'Read results', desc: 'dist[i][j] now holds the shortest path distance between every pair (i,j).' },
    ],
    codeExamples: [
      {
        label: 'Floyd-Warshall',
        complexity: 'O(V³)',
        code: 'def floyd_warshall(V, edges):\n    dist = [[float("inf")]*V for _ in range(V)]\n    for i in range(V):\n        dist[i][i] = 0\n    for u, v, w in edges:\n        dist[u][v] = w\n\n    for k in range(V):\n        for i in range(V):\n            for j in range(V):\n                via_k = dist[i][k] + dist[k][j]\n                if via_k < dist[i][j]:\n                    dist[i][j] = via_k\n\n    # Check negative cycles\n    for i in range(V):\n        if dist[i][i] < 0:\n            return None\n\n    return dist',
      },
      {
        label: 'Transitive Closure (reachability)',
        complexity: 'O(V³)',
        code: 'def transitive_closure(V, adj):\n    # reach[i][j] = True if j is reachable from i\n    reach = [[False]*V for _ in range(V)]\n    for i in range(V):\n        reach[i][i] = True\n    for u in range(V):\n        for v in adj[u]:\n            reach[u][v] = True\n\n    for k in range(V):\n        for i in range(V):\n            for j in range(V):\n                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])\n    return reach',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time', value: 'O(V³)', color: 'text-violet-400', note: 'Three nested loops over V vertices each' },
        { case: 'Space', value: 'O(V²)', color: 'text-orange-400', note: 'Full V×V distance matrix' },
        { case: 'Dijkstra × V (comparison)', value: 'O(V(V+E) log V)', color: 'text-amber-400', note: 'Better for sparse graphs with non-negative weights' },
      ],
    },
    realWorld: [
      { title: 'Network Routing Tables', desc: 'Computing latency between all pairs of routers in a network.' },
      { title: 'Dense Transport Networks', desc: 'Flight times between all city pairs in dense airline networks.' },
      { title: 'Transitive Closure', desc: 'Finding which vertices are reachable from which in a DAG (used in compilers).' },
      { title: 'Game AI', desc: 'Precomputing all-pairs distances for game maps where NPCs need to know distances to all players.' },
    ],
    quiz: [
      { q: 'What is the recurrence relation used in Floyd-Warshall?', options: ['dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])', 'dist[i][j] = dist[i][k] * dist[k][j]', 'dist[i][j] = max(dist[i][k], dist[k][j])', 'dist[i][j] = dist[i][k] - dist[k][j]'], correct: 0, explanation: 'For each intermediate k, we check if routing through k improves the i→j distance.' },
      { q: 'What does a negative value on the diagonal (dist[i][i] < 0) indicate?', options: ['Disconnected graph', 'Negative edge from i', 'Negative-weight cycle reachable from i', 'Initialization error'], correct: 2, explanation: 'dist[i][i] starts at 0. It can only decrease if there\'s a negative cycle that passes through i.' },
      { q: 'When would you choose Floyd-Warshall over running Dijkstra V times?', options: ['When the graph is sparse and non-negative', 'When the graph is dense or has negative edges', 'When you only need single-source shortest paths', 'When V is very large'], correct: 1, explanation: 'Floyd-Warshall is simpler to code for all-pairs with negatives. For sparse non-negative graphs, Dijkstra×V is faster.' },
      { q: 'In Floyd-Warshall, the order of the three nested loops matters. Which variable must be the outermost loop?', options: ['i (source vertex)', 'j (destination vertex)', 'k (intermediate vertex)', 'The order does not matter'], correct: 2, explanation: 'k must be outermost so that when we compute dist[i][k] and dist[k][j], all paths through intermediates 0..k-1 are already finalized.' },
      { q: 'What is the initial value of dist[i][j] when there is no direct edge from i to j in Floyd-Warshall?', options: ['0', '-1', 'float("inf") (infinity)', 'V'], correct: 2, explanation: 'Infinity represents "no known path yet." As the algorithm runs, it replaces infinity with actual shortest distances when paths are found.' },
      { q: 'Floyd-Warshall can be adapted for transitive closure. What does reach[i][j] = True mean in that variant?', options: ['Edge (i,j) exists directly', 'The total edge weight from i to j is positive', 'Vertex j is reachable from vertex i by some path', 'Vertices i and j are in the same strongly connected component'], correct: 2, explanation: 'Transitive closure computes reachability: reach[i][j] becomes True if any chain of edges connects i to j, regardless of edge weights.' },
    ],
  },

  'minimum-spanning-tree': {
    concept: {
      overview:
        'A Minimum Spanning Tree (MST) connects all vertices of a weighted undirected graph using exactly V-1 edges with minimum total weight and no cycles. Two greedy algorithms solve this: Kruskal\'s (sort edges, add smallest non-cycle-forming edge) and Prim\'s (grow tree greedily from a seed vertex).',
      keyPoints: [
        { title: "Kruskal's Algorithm", desc: 'Sort all edges by weight. Process in order: add edge if it doesn\'t form a cycle (checked via Union-Find). Stop when V-1 edges added. O(E log E).' },
        { title: "Prim's Algorithm", desc: 'Start from any vertex. Always add the minimum-weight edge connecting the current tree to a new vertex. Use a priority queue. O(E log V) with heap.' },
        { title: 'MST Properties', desc: 'Every MST has exactly V-1 edges and zero cycles. There may be multiple MSTs if edge weights are equal. MST total weight is always uniquely minimized.' },
      ],
    },
    steps: [
      { n: '1', label: 'Sort edges by weight', desc: 'Kruskal\'s: sort all E edges ascending.', code: 'edges.sort(key=lambda e: e[2])' },
      { n: '2', label: 'Initialize Union-Find', desc: 'Create a disjoint set for cycle detection.', code: 'uf = UnionFind(V)' },
      { n: '3', label: 'Process edges', desc: 'For each edge (u,v,w): if u and v are in different components, add edge to MST and union them.', code: 'for u, v, w in edges:\n    if uf.find(u) != uf.find(v):\n        mst.append((u, v, w))\n        uf.union(u, v)' },
      { n: '4', label: 'Stop at V-1 edges', desc: 'Once V-1 edges are added, the MST is complete.', code: 'if len(mst) == V - 1:\n    break' },
    ],
    codeExamples: [
      {
        label: "Kruskal's Algorithm",
        complexity: 'O(E log E)',
        code: 'def kruskal(V, edges):\n    # Sort edges by weight\n    edges.sort(key=lambda e: e[2])\n    parent = list(range(V))\n\n    def find(x):\n        while parent[x] != x:\n            parent[x] = parent[parent[x]]\n            x = parent[x]\n        return x\n\n    def union(x, y):\n        parent[find(x)] = find(y)\n\n    mst = []\n    for u, v, w in edges:\n        if find(u) != find(v):\n            union(u, v)\n            mst.append((u, v, w))\n        if len(mst) == V - 1:\n            break\n    return mst',
      },
      {
        label: "Prim's Algorithm",
        complexity: 'O(E log V)',
        code: 'import heapq\n\ndef prim(adj, V):\n    visited = [False] * V\n    heap = [(0, 0, -1)]  # (weight, node, parent)\n    mst = []\n    total_weight = 0\n\n    while heap and len(mst) < V - 1:\n        w, node, parent = heapq.heappop(heap)\n        if visited[node]:\n            continue\n        visited[node] = True\n        if parent != -1:\n            mst.append((parent, node, w))\n            total_weight += w\n        for nbr, weight in adj[node]:\n            if not visited[nbr]:\n                heapq.heappush(heap, (weight, nbr, node))\n    return mst, total_weight',
      },
    ],
    complexity: {
      rows: [
        { case: "Kruskal's Time", value: 'O(E log E)', color: 'text-amber-400', note: 'Dominated by sorting edges' },
        { case: "Prim's Time (heap)", value: 'O(E log V)', color: 'text-amber-400', note: 'Better for dense graphs' },
        { case: 'Space', value: 'O(V)', color: 'text-indigo-400', note: 'Union-Find or visited array' },
      ],
    },
    realWorld: [
      { title: 'Network Cabling', desc: 'Minimize total wire length to connect all offices — cable layout as MST of building positions.' },
      { title: 'Circuit Board Design', desc: 'Connect electronic components using minimum copper traces on a PCB.' },
      { title: 'Cluster Analysis', desc: 'Single-link hierarchical clustering removes the longest MST edge to create clusters.' },
      { title: 'Water/Power Distribution', desc: 'Designing distribution networks connecting all households with minimum pipeline length.' },
    ],
    quiz: [
      { q: 'How many edges does a spanning tree of V vertices have?', options: ['V', 'V+1', 'V-1', 'V²'], correct: 2, explanation: 'A tree connecting V vertices has exactly V-1 edges — enough to connect all without cycles.' },
      { q: 'What data structure does Kruskal\'s use to detect cycles?', options: ['Stack', 'Queue', 'Union-Find', 'Hash Table'], correct: 2, explanation: 'Union-Find efficiently tracks which component each vertex belongs to, detecting cycles in near O(1).' },
      { q: 'When does Prim\'s outperform Kruskal\'s?', options: ['Sparse graphs', 'Dense graphs with many edges', 'When edges are pre-sorted', 'When V is small'], correct: 1, explanation: "Prim's with heap is O(E log V) vs Kruskal's O(E log E). For dense graphs where E ≈ V², Prim's is better." },
      { q: 'Is the MST of a graph always unique?', options: ['Yes, always', 'No — if two edges have the same weight there may be multiple valid MSTs', 'Only for undirected graphs', 'Only when E = V-1'], correct: 1, explanation: 'When distinct edges share the same weight, different algorithms may include different subsets of those tied edges, producing multiple valid MSTs with the same total cost.' },
      { q: 'Why does Kruskal\'s algorithm process edges in sorted order?', options: ['To detect back edges', 'To guarantee that each added edge has minimum weight among all edges that would not form a cycle', 'To satisfy the BFS level constraint', 'To enable path compression'], correct: 1, explanation: 'Greedy correctness relies on always picking the globally cheapest safe edge. Sorting ensures we always consider the smallest available non-cycle-forming edge first.' },
      { q: 'What property of MST guarantees the Cut Property used in Prim\'s?', options: ['Every cycle must contain the heaviest edge', 'The minimum-weight edge crossing any cut of the graph belongs to some MST', 'MSTs always contain the overall minimum edge', 'MST edges are always a subset of BFS tree edges'], correct: 1, explanation: 'The Cut Property states: for any partition of vertices into two sets, the minimum-weight edge crossing the cut is safe to include in an MST.' },
    ],
  },

  'union-find': {
    concept: {
      overview:
        'Union-Find (Disjoint Set Union) efficiently tracks which elements belong to the same connected component. Two operations: Find (which component does x belong to?) and Union (merge two components). With path compression and union by rank, both operations run in near-constant amortized time O(α(n)), where α is the inverse Ackermann function.',
      keyPoints: [
        { title: 'Path Compression', desc: 'During Find, make every node on the path point directly to the root. Flattens the tree over time, making future finds faster.' },
        { title: 'Union by Rank', desc: 'When merging two trees, attach the shorter tree to the root of the taller tree. Prevents degenerate chain formation.' },
        { title: 'Amortized O(α(n))', desc: 'With both optimizations, operations are practically constant. For all practical inputs α(n) ≤ 4. This makes Union-Find one of the most efficient data structures ever devised.' },
      ],
    },
    steps: [
      { n: '1', label: 'Initialize', desc: 'Each element is its own parent (its own component). Rank starts at 0 for all.', code: 'parent = list(range(n))\nrank = [0] * n' },
      { n: '2', label: 'Find with path compression', desc: 'Follow parent pointers to root. Point each visited node directly to root during traversal.', code: 'def find(x):\n    if parent[x] != x:\n        parent[x] = find(parent[x])  # path compression\n    return parent[x]' },
      { n: '3', label: 'Union by rank', desc: 'Find roots of both elements. Attach smaller-rank tree to larger-rank root.', code: 'def union(x, y):\n    rx, ry = find(x), find(y)\n    if rx == ry: return\n    if rank[rx] < rank[ry]: rx, ry = ry, rx\n    parent[ry] = rx\n    if rank[rx] == rank[ry]: rank[rx] += 1' },
      { n: '4', label: 'Check connectivity', desc: 'Two elements are in the same component if and only if find(x) == find(y).', code: 'def connected(x, y):\n    return find(x) == find(y)' },
    ],
    codeExamples: [
      {
        label: 'Union-Find with both optimizations',
        complexity: 'O(α(n)) amortized',
        code: 'class UnionFind:\n    def __init__(self, n):\n        self.parent = list(range(n))\n        self.rank = [0] * n\n        self.components = n\n\n    def find(self, x):\n        if self.parent[x] != x:\n            self.parent[x] = self.find(self.parent[x])\n        return self.parent[x]\n\n    def union(self, x, y):\n        rx, ry = self.find(x), self.find(y)\n        if rx == ry:\n            return False  # already same component\n        if self.rank[rx] < self.rank[ry]:\n            rx, ry = ry, rx\n        self.parent[ry] = rx\n        if self.rank[rx] == self.rank[ry]:\n            self.rank[rx] += 1\n        self.components -= 1\n        return True',
      },
      {
        label: 'Kruskal\'s MST using Union-Find',
        complexity: 'O(E α(V))',
        code: 'def kruskal_mst(V, edges):\n    uf = UnionFind(V)\n    edges.sort(key=lambda e: e[2])  # sort by weight\n    mst_weight = 0\n    mst_edges = []\n\n    for u, v, w in edges:\n        if uf.union(u, v):  # no cycle\n            mst_edges.append((u, v, w))\n            mst_weight += w\n        if len(mst_edges) == V - 1:\n            break\n\n    return mst_edges, mst_weight',
      },
    ],
    complexity: {
      rows: [
        { case: 'Find (with compression)', value: 'O(α(n))', color: 'text-emerald-400', note: 'Inverse Ackermann ≤ 4 for all practical n' },
        { case: 'Union (with rank)', value: 'O(α(n))', color: 'text-emerald-400', note: 'Amortized constant time' },
        { case: 'Space', value: 'O(n)', color: 'text-indigo-400', note: 'Parent and rank arrays of size n' },
      ],
      note: 'α(n) is the inverse Ackermann function, effectively constant (≤ 4) for any practical input.',
    },
    realWorld: [
      { title: "Kruskal's MST", desc: 'Detect cycle-forming edges in near-constant time during MST construction.' },
      { title: 'Connected Components', desc: 'Track network connectivity as edges are added — social network friend clusters.' },
      { title: 'Percolation', desc: 'Physics simulations of fluid flow through random media use Union-Find to detect connected paths.' },
      { title: 'Image Segmentation', desc: 'Merge adjacent similar-color pixels into regions for computer vision segmentation.' },
    ],
    quiz: [
      { q: 'What does path compression do in Union-Find?', options: ['Sorts elements', 'Makes all nodes on find path point directly to root', 'Merges two trees', 'Removes duplicate elements'], correct: 1, explanation: 'Path compression flattens the tree so future find operations are O(1).' },
      { q: 'What is the amortized time complexity with both path compression and union by rank?', options: ['O(1)', 'O(log n)', 'O(α(n))', 'O(n)'], correct: 2, explanation: 'The inverse Ackermann function α(n) grows so slowly that it\'s effectively constant for all real inputs.' },
      { q: 'What does union by rank prevent?', options: ['Path compression', 'Cycle formation', 'Degenerate chain trees', 'Memory overflow'], correct: 2, explanation: 'By attaching shorter trees to taller roots, union by rank prevents the tree from becoming a long chain that degrades find to O(n).' },
      { q: 'After calling union(x, y) in Union-Find, what does find(x) == find(y) evaluate to?', options: ['False', 'True', 'Depends on rank', 'An error'], correct: 1, explanation: 'union(x, y) merges the two sets, so both x and y now share the same root. find on either must return that common root.' },
      { q: 'How many connected components are there initially when you create UnionFind(n)?', options: ['1', 'n-1', 'n', '0'], correct: 2, explanation: 'Each of the n elements starts as its own component (its own parent), so there are n components before any unions.' },
      { q: 'What is the purpose of the "components" counter in a Union-Find implementation?', options: ['Tracking tree height', 'Counting the number of disjoint sets currently present', 'Storing edge weights', 'Preventing path compression'], correct: 1, explanation: 'The counter starts at n and decreases by 1 each time a successful union merges two previously distinct components, making component count queries O(1).' },
    ],
  },

  'memoization': {
    concept: {
      overview:
        'Memoization is a top-down dynamic programming technique that adds a cache to a recursive solution. When a subproblem is solved for the first time, its result is stored. On subsequent calls with the same arguments, the cached result is returned immediately instead of recomputing. This transforms exponential recursive algorithms into polynomial ones.',
      keyPoints: [
        { title: 'Top-Down Approach', desc: 'Start with the original problem and break it into subproblems recursively. Only compute each subproblem once. This is the natural direction for divide-and-conquer style problems.' },
        { title: 'Cache (Memo)', desc: 'A dictionary or array that maps subproblem inputs to computed outputs. Before computing, check the cache. After computing, store the result.' },
        { title: 'Overlapping Subproblems', desc: 'Memoization is only beneficial when subproblems repeat. Fibonacci recomputes F(3) many times in naive recursion — memoization computes it once and reuses it.' },
      ],
    },
    steps: [
      { n: '1', label: 'Write naive recursive solution', desc: 'Start with the correct but potentially exponential recursive solution without any caching.', code: 'def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)  # O(2^n)' },
      { n: '2', label: 'Identify repeated subproblems', desc: 'Draw the recursion tree. Notice fib(3) is computed multiple times. These repeated calls are waste.' },
      { n: '3', label: 'Add a cache', desc: 'Create a dictionary to store results. Check it before computing, store after.', code: 'memo = {}\ndef fib(n):\n    if n in memo: return memo[n]\n    if n <= 1: return n\n    memo[n] = fib(n-1) + fib(n-2)\n    return memo[n]' },
      { n: '4', label: 'Verify correctness', desc: 'The cached version produces identical results. Check the reduction from O(2^n) to O(n) calls.' },
      { n: '5', label: 'Use @lru_cache decorator', desc: 'In Python, @functools.lru_cache(maxsize=None) adds memoization automatically.', code: 'from functools import lru_cache\n\n@lru_cache(maxsize=None)\ndef fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)' },
    ],
    codeExamples: [
      {
        label: 'Naive vs Memoized Fibonacci',
        complexity: 'O(n) with memo vs O(2^n) naive',
        code: '# NAIVE: recomputes same values exponentially\ndef fib_naive(n):\n    if n <= 1: return n\n    return fib_naive(n-1) + fib_naive(n-2)\n# fib_naive(40) makes 330 million calls!\n\n# MEMOIZED: each unique n computed once\nmemo = {}\ndef fib_memo(n):\n    if n in memo: return memo[n]\n    if n <= 1: return n\n    memo[n] = fib_memo(n-1) + fib_memo(n-2)\n    return memo[n]\n# fib_memo(40) makes 79 calls',
        variant: 'good',
      },
      {
        label: 'Memoized Grid Path Counting',
        complexity: 'O(m*n)',
        code: 'def count_paths(m, n, memo={}):\n    """Count paths from (0,0) to (m-1,n-1)\n    moving only right or down."""\n    if (m, n) in memo:\n        return memo[(m, n)]\n    if m == 1 or n == 1:\n        return 1\n    result = count_paths(m-1, n, memo) + count_paths(m, n-1, memo)\n    memo[(m, n)] = result\n    return result\n\n# Without memo: O(2^(m+n))\n# With memo:    O(m*n)',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time (with memo)', value: 'O(unique subproblems)', color: 'text-indigo-400', note: 'Each subproblem computed once' },
        { case: 'Time (without)', value: 'O(2^n) or worse', color: 'text-red-400', note: 'Exponential without caching' },
        { case: 'Space', value: 'O(subproblems)', color: 'text-indigo-400', note: 'Cache + recursion stack depth' },
      ],
    },
    realWorld: [
      { title: 'Fibonacci / Combinatorics', desc: 'Memoization reduces exponential combinatoric calculations to polynomial.' },
      { title: 'Game Theory', desc: 'Minimax game trees (chess, tic-tac-toe) cache positions to avoid re-evaluating the same board state.' },
      { title: 'Compiler Optimization', desc: 'Parsers cache partial parse results (Packrat parsing) for O(n) grammar matching.' },
      { title: 'Recursive Algorithms', desc: 'Any divide-and-conquer algorithm with overlapping subproblems benefits — coin change, Fibonacci, LCS.' },
    ],
    quiz: [
      { q: 'What problem does memoization primarily solve?', options: ['Memory overflow', 'Recomputing overlapping subproblems', 'Stack overflow', 'Integer overflow'], correct: 1, explanation: 'Memoization caches computed results, preventing redundant work on repeated subproblems.' },
      { q: 'What is the space overhead of memoization?', options: ['O(1)', 'O(log n)', 'O(number of unique subproblems)', 'O(n²)'], correct: 2, explanation: 'The cache stores one entry per unique subproblem. Fibonacci memo stores O(n) entries.' },
      { q: 'How does memoization differ from tabulation?', options: ['Memoization is bottom-up, tabulation is top-down', 'Memoization is top-down recursive, tabulation is bottom-up iterative', 'They are identical', 'Memoization uses more memory'], correct: 1, explanation: 'Memoization uses recursion and caches on the way down. Tabulation fills a table iteratively from base cases.' },
      { q: 'What is a potential drawback of memoization that tabulation avoids?', options: ['Memoization cannot handle strings', 'Memoization risks stack overflow for deep recursion', 'Memoization always uses more memory than tabulation', 'Memoization cannot be used with dictionaries'], correct: 1, explanation: 'Deep recursion can exhaust the call stack. Python\'s default recursion limit is ~1000 frames; large inputs may require increasing it or switching to tabulation.' },
      { q: 'For a function with two integer parameters (i, j), what is an appropriate memoization cache key?', options: ['i + j', 'i * j', 'The tuple (i, j)', 'A single integer i'], correct: 2, explanation: 'A tuple (i, j) uniquely identifies each (i, j) pair as a dictionary key. Using i+j would incorrectly map (1,3) and (2,2) to the same key.' },
      { q: 'Which condition must hold for memoization to provide a speedup over plain recursion?', options: ['The function must be pure (no side effects)', 'Subproblems must overlap — the same arguments must be computed more than once', 'The input must be sorted', 'The recursion depth must be less than 10'], correct: 1, explanation: 'Memoization only helps when the same subproblem is encountered multiple times. With no overlapping subproblems (like merge sort), caching adds overhead without benefit.' },
    ],
  },

  'tabulation': {
    concept: {
      overview:
        'Tabulation is a bottom-up dynamic programming technique that builds solutions to larger problems from precomputed solutions to smaller subproblems, filling a table iteratively. Unlike top-down memoization, there is no recursion overhead or risk of stack overflow. Tabulation often has better cache performance and is preferred when all subproblems must be solved anyway.',
      keyPoints: [
        { title: 'Bottom-Up', desc: 'Start from the smallest/simplest subproblems (base cases) and iteratively compute larger ones. By the time we need a value, it\'s already in the table.' },
        { title: 'No Recursion', desc: 'Pure iteration with no function call overhead or risk of stack overflow for large inputs. This also makes it easier to optimize space by reusing rows of the table.' },
        { title: 'Space Optimization', desc: 'Often the table can be reduced. Fibonacci only needs the previous two values (O(1) instead of O(n)). Knapsack 2D table can be reduced to a 1D array.' },
      ],
    },
    steps: [
      { n: '1', label: 'Identify base cases', desc: 'Determine the simplest subproblems with known answers (e.g., fib[0]=0, fib[1]=1).', code: 'dp = [0] * (n+1)\ndp[0], dp[1] = 0, 1' },
      { n: '2', label: 'Determine fill order', desc: 'Figure out which direction to fill the table so dependencies are already computed.', code: 'for i in range(2, n+1):  # left to right' },
      { n: '3', label: 'Fill the table', desc: 'Compute each state using previously computed states.', code: 'dp[i] = dp[i-1] + dp[i-2]  # fib recurrence' },
      { n: '4', label: 'Return the answer', desc: 'The final answer is at the appropriate table position.', code: 'return dp[n]' },
      { n: '5', label: 'Optimize space if possible', desc: 'If only the last few states are needed, use rolling variables instead of full array.', code: 'a, b = 0, 1\nfor _ in range(n): a, b = b, a+b\nreturn a  # O(1) space!' },
    ],
    codeExamples: [
      {
        label: 'Tabulation: Fibonacci',
        complexity: 'O(n) time, O(1) space',
        code: '# Full table: O(n) space\ndef fib_table(n):\n    if n <= 1: return n\n    dp = [0] * (n+1)\n    dp[1] = 1\n    for i in range(2, n+1):\n        dp[i] = dp[i-1] + dp[i-2]\n    return dp[n]\n\n# Space-optimized: O(1) space\ndef fib_opt(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a',
        variant: 'good',
      },
      {
        label: 'Tabulation: Coin Change (min coins)',
        complexity: 'O(n * amount)',
        code: 'def coin_change(coins, amount):\n    # dp[i] = min coins to make amount i\n    dp = [float("inf")] * (amount + 1)\n    dp[0] = 0  # base case: 0 coins for amount 0\n\n    for amt in range(1, amount + 1):\n        for coin in coins:\n            if coin <= amt:\n                dp[amt] = min(dp[amt], dp[amt - coin] + 1)\n\n    return dp[amount] if dp[amount] != float("inf") else -1\n\n# coin_change([1,5,10], 11) = 2 (10+1)',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time', value: 'O(subproblems)', color: 'text-indigo-400', note: 'Fill each table cell once' },
        { case: 'Space (full table)', value: 'O(subproblems)', color: 'text-indigo-400', note: 'One entry per subproblem' },
        { case: 'Space (optimized)', value: 'O(1) to O(n)', color: 'text-emerald-400', note: 'Often reducible by keeping only needed rows' },
      ],
    },
    realWorld: [
      { title: 'Edit Distance', desc: 'Spell checkers compute Levenshtein distance using a 2D DP table filled row by row.' },
      { title: 'Sequence Alignment', desc: 'Bioinformatics DNA alignment (Smith-Waterman) fills a scoring matrix bottom-up.' },
      { title: 'Options Pricing', desc: 'Binomial tree options pricing models fill tables from expiry date backwards.' },
      { title: 'Path Counting', desc: 'Counting paths in grids or DAGs: fill table cell by cell from top-left to bottom-right.' },
    ],
    quiz: [
      { q: 'What direction does tabulation fill its table?', options: ['Top-down (recursive)', 'Bottom-up (iterative)', 'Random order', 'Right to left only'], correct: 1, explanation: 'Tabulation fills from smallest subproblems (base cases) up to the target problem.' },
      { q: 'What is the main advantage of tabulation over memoization?', options: ['Always uses less space', 'No recursion overhead or stack overflow risk', 'Faster asymptotically', 'Easier to write'], correct: 1, explanation: 'Tabulation avoids recursion depth limits and function call overhead, making it more efficient in practice.' },
      { q: 'When can you optimize a DP table\'s space to O(1)?', options: ['Always', 'When the recurrence only uses a constant number of previous states', 'Never for 2D tables', 'When n is small'], correct: 1, explanation: 'If dp[i] only depends on dp[i-1] and dp[i-2] (like Fibonacci), you only need those two variables.' },
      { q: 'Why must the inner loop in the 1D space-optimized 0/1 Knapsack iterate from W down to the item\'s weight, not left to right?', options: ['Ascending order is slower', 'Right-to-left ensures each item is only considered once per row', 'The item weights are stored in reverse order', 'To avoid integer overflow'], correct: 1, explanation: 'Iterating left-to-right would update dp[w - weight] before it is read for larger w values, effectively allowing an item to be used multiple times (unbounded knapsack behavior).' },
      { q: 'In the coin change tabulation, dp[0] is initialized to 0. Why?', options: ['0 coins are needed to make amount 0', 'The first coin always has value 0', 'To avoid a division by zero', 'So the loop starts at index 1'], correct: 0, explanation: 'Making amount 0 requires 0 coins — that is the base case. All other dp values start at infinity and get updated from this base.' },
      { q: 'Which of these is an advantage of tabulation over memoization for problems like grid path counting?', options: ['Tabulation requires less code', 'Tabulation solves all subproblems even if only some are needed', 'Tabulation avoids recursion depth limits and has better cache locality', 'Tabulation cannot be space-optimized'], correct: 2, explanation: 'Sequential array access in tabulation exploits CPU cache lines. No recursion means no stack overhead, and no hash-table lookups compared to a memoization dictionary.' },
    ],
  },

  'knapsack': {
    concept: {
      overview:
        'The 0/1 Knapsack problem: given n items each with a weight and value, and a knapsack of capacity W, select items to maximize total value without exceeding W. Each item is either taken (1) or left (0) — no fractions allowed. The DP solution builds a 2D table: dp[i][w] = max value using first i items with capacity w.',
      keyPoints: [
        { title: '0/1 Choice', desc: 'Each item is either included or excluded entirely. This binary constraint is what makes knapsack non-trivial — greedy doesn\'t work because taking the highest-value-density item first may not be globally optimal.' },
        { title: 'DP Recurrence', desc: 'dp[i][w] = max(dp[i-1][w], values[i-1] + dp[i-1][w-weights[i-1]]). Either skip item i or include it (if it fits).' },
        { title: 'Pseudopolynomial', desc: 'O(nW) time is not truly polynomial because W can be exponentially large in the bit-length of its input representation. Still practical for small W.' },
      ],
    },
    steps: [
      { n: '1', label: 'Define the DP table', desc: 'dp[i][w] = max value achievable with first i items and capacity w. Size (n+1) × (W+1).', code: 'dp = [[0]*(W+1) for _ in range(n+1)]' },
      { n: '2', label: 'Fill base cases', desc: 'dp[0][w] = 0 for all w (no items → no value). dp[i][0] = 0 for all i (no capacity → no value).' },
      { n: '3', label: 'Fill the table', desc: 'For each item i and capacity w: if item fits, take best of (skip, include). If it doesn\'t fit, must skip.', code: 'for i in range(1, n+1):\n    for w in range(W+1):\n        if weights[i-1] > w:\n            dp[i][w] = dp[i-1][w]  # skip\n        else:\n            dp[i][w] = max(dp[i-1][w],\n                          values[i-1] + dp[i-1][w-weights[i-1]])' },
      { n: '4', label: 'Read answer', desc: 'dp[n][W] is the maximum value achievable.', code: 'return dp[n][W]' },
    ],
    codeExamples: [
      {
        label: '0/1 Knapsack — Full Table',
        complexity: 'O(nW) time, O(nW) space',
        code: 'def knapsack_01(weights, values, W):\n    n = len(weights)\n    dp = [[0]*(W+1) for _ in range(n+1)]\n\n    for i in range(1, n+1):\n        for w in range(W+1):\n            # Option 1: skip item i\n            dp[i][w] = dp[i-1][w]\n            # Option 2: include item i (if it fits)\n            if weights[i-1] <= w:\n                include = values[i-1] + dp[i-1][w - weights[i-1]]\n                dp[i][w] = max(dp[i][w], include)\n\n    return dp[n][W]',
      },
      {
        label: 'Space-Optimized (1D array)',
        complexity: 'O(nW) time, O(W) space',
        code: 'def knapsack_1d(weights, values, W):\n    n = len(weights)\n    dp = [0] * (W+1)\n\n    for i in range(n):\n        # Traverse W backwards to avoid using item i twice\n        for w in range(W, weights[i]-1, -1):\n            dp[w] = max(dp[w], values[i] + dp[w - weights[i]])\n\n    return dp[W]\n\n# Key insight: reverse traversal ensures we\n# use previous iteration\'s values (item i not repeated)',
        variant: 'good',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time', value: 'O(nW)', color: 'text-orange-400', note: 'n items × W capacity values' },
        { case: 'Space (2D)', value: 'O(nW)', color: 'text-orange-400', note: 'Full DP table' },
        { case: 'Space (1D)', value: 'O(W)', color: 'text-indigo-400', note: 'Only current row needed' },
      ],
      note: 'O(nW) is pseudopolynomial — W can be large. NP-hard in general; DP works for bounded integer W.',
    },
    realWorld: [
      { title: 'Resource Allocation', desc: 'Allocating limited budget/CPU/memory across tasks to maximize throughput.' },
      { title: 'Portfolio Selection', desc: 'Selecting investment assets with limited capital to maximize expected return.' },
      { title: 'Ad Bidding', desc: 'Selecting which ads to show within a page\'s space budget to maximize revenue.' },
      { title: 'Cargo Loading', desc: 'Loading trucks/ships with integer-weight items to maximize value within weight limit.' },
    ],
    quiz: [
      { q: 'What does dp[i][w] represent in the 0/1 knapsack table?', options: ['Weight of item i', 'Max value using first i items with capacity w', 'Number of items fitting in w', 'Minimum weight for value w'], correct: 1, explanation: 'dp[i][w] captures the optimal selection from the first i items with a capacity constraint of w.' },
      { q: 'Why is 0/1 knapsack called "pseudopolynomial"?', options: ['It has two dimensions', 'W can be exponentially large relative to input bits', 'It uses floating point', 'It requires sorting'], correct: 1, explanation: 'The O(nW) complexity looks polynomial but W itself can require log₂W bits, making it exponential in input size.' },
      { q: 'What is the key difference from fractional knapsack?', options: ['Fractional is slower', '0/1 knapsack cannot use greedy', 'Fractional requires sorting', '0/1 uses more memory'], correct: 1, explanation: 'With 0/1 constraints, taking the highest value-density item first is not always globally optimal, so DP is needed.' },
      { q: 'In the 0/1 knapsack recurrence, dp[i][w] = max(dp[i-1][w], values[i-1] + dp[i-1][w-weights[i-1]]). What does dp[i-1][w] represent?', options: ['The value if item i is included', 'The best value using first i-1 items with capacity w (item i is skipped)', 'The weight of item i', 'The value when capacity is i-1'], correct: 1, explanation: 'dp[i-1][w] is the optimal solution without item i. The recurrence takes the max of skipping vs. including item i.' },
      { q: 'You have items with weights [3, 4, 5] and values [4, 5, 6] and capacity W=7. What is the maximum value?', options: ['9', '10', '11', '6'], correct: 0, explanation: 'Items of weight 3 (value 4) and weight 4 (value 5) fit within W=7 for total value 9. The item of weight 5 alone gives only 6, and no two other pairs fit.' },
      { q: 'The unbounded knapsack problem differs from 0/1 knapsack in that:', options: ['Items have unlimited value', 'Each item can be taken any number of times', 'The capacity W is unlimited', 'Items can be split into fractions'], correct: 1, explanation: 'In unbounded knapsack, items can be reused — this changes the DP to iterate capacity left-to-right (ascending) instead of right-to-left.' },
    ],
  },

  'lcs': {
    concept: {
      overview:
        'The Longest Common Subsequence (LCS) finds the longest sequence of characters that appears in the same order (but not necessarily contiguously) in both strings. For strings "ABCBDAB" and "BDCAB", the LCS is "BCAB" (length 4). LCS is the foundation of diff utilities, version control, and DNA alignment.',
      keyPoints: [
        { title: 'Subsequence vs Substring', desc: 'A subsequence preserves relative order but elements need not be adjacent. "ACE" is a subsequence of "ABCDE" but not a substring. Substring requires contiguity.' },
        { title: 'DP Recurrence', desc: 'If s1[i]==s2[j]: dp[i][j] = 1 + dp[i-1][j-1]. Else: dp[i][j] = max(dp[i-1][j], dp[i][j-1]). The table encodes: how long is the LCS of the first i chars of s1 and first j chars of s2?' },
        { title: 'Backtracking', desc: 'The DP table gives the LCS length. To recover the actual sequence, trace back: when chars matched, include in LCS; otherwise go in direction of larger neighbor.' },
      ],
    },
    steps: [
      { n: '1', label: 'Create the DP table', desc: 'Create (m+1) × (n+1) table initialized to 0. Extra row/column for empty string base case.', code: 'dp = [[0]*(n+1) for _ in range(m+1)]' },
      { n: '2', label: 'Fill the table', desc: 'If characters match: diagonal + 1. Else: max of left or up neighbor.', code: 'for i in range(1, m+1):\n    for j in range(1, n+1):\n        if s1[i-1] == s2[j-1]:\n            dp[i][j] = 1 + dp[i-1][j-1]\n        else:\n            dp[i][j] = max(dp[i-1][j], dp[i][j-1])' },
      { n: '3', label: 'LCS length', desc: 'dp[m][n] is the length of the LCS.', code: 'lcs_length = dp[m][n]' },
      { n: '4', label: 'Backtrack to get sequence', desc: 'Start at dp[m][n], trace back: if chars matched go diagonal, else go to max neighbor.', code: 'i, j = m, n\nresult = []\nwhile i > 0 and j > 0:\n    if s1[i-1] == s2[j-1]:\n        result.append(s1[i-1])\n        i -= 1; j -= 1\n    elif dp[i-1][j] > dp[i][j-1]:\n        i -= 1\n    else:\n        j -= 1\nreturn "".join(reversed(result))' },
    ],
    codeExamples: [
      {
        label: 'LCS Length and Sequence',
        complexity: 'O(mn) time and space',
        code: 'def lcs(s1, s2):\n    m, n = len(s1), len(s2)\n    dp = [[0]*(n+1) for _ in range(m+1)]\n\n    for i in range(1, m+1):\n        for j in range(1, n+1):\n            if s1[i-1] == s2[j-1]:\n                dp[i][j] = 1 + dp[i-1][j-1]\n            else:\n                dp[i][j] = max(dp[i-1][j], dp[i][j-1])\n\n    # Backtrack to find actual LCS string\n    i, j = m, n\n    result = []\n    while i > 0 and j > 0:\n        if s1[i-1] == s2[j-1]:\n            result.append(s1[i-1])\n            i -= 1; j -= 1\n        elif dp[i-1][j] >= dp[i][j-1]:\n            i -= 1\n        else:\n            j -= 1\n\n    return dp[m][n], "".join(reversed(result))',
      },
      {
        label: 'Space-Optimized LCS Length',
        complexity: 'O(mn) time, O(min(m,n)) space',
        code: 'def lcs_length(s1, s2):\n    # Only keep two rows at a time\n    if len(s1) < len(s2):\n        s1, s2 = s2, s1  # ensure s2 is shorter\n    m, n = len(s1), len(s2)\n    prev = [0] * (n+1)\n\n    for i in range(1, m+1):\n        curr = [0] * (n+1)\n        for j in range(1, n+1):\n            if s1[i-1] == s2[j-1]:\n                curr[j] = 1 + prev[j-1]\n            else:\n                curr[j] = max(prev[j], curr[j-1])\n        prev = curr\n\n    return prev[n]',
        variant: 'good',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time', value: 'O(mn)', color: 'text-orange-400', note: 'm and n are lengths of the two strings' },
        { case: 'Space (full table)', value: 'O(mn)', color: 'text-orange-400', note: 'Full 2D DP table' },
        { case: 'Space (optimized)', value: 'O(min(m,n))', color: 'text-indigo-400', note: 'Only two rows needed at once' },
      ],
    },
    realWorld: [
      { title: 'Git Diff', desc: 'The unified diff format showing changed lines between two file versions is computed using LCS on lines.' },
      { title: 'DNA Alignment', desc: 'Finding conserved gene sequences across species uses LCS on nucleotide strings.' },
      { title: 'File Comparison', desc: 'Unix diff, WinMerge, and similar tools use LCS to identify changed sections.' },
      { title: 'Plagiarism Detection', desc: 'Computing LCS between student submissions reveals copied sections.' },
    ],
    quiz: [
      { q: 'What is the recurrence when characters at s1[i] and s2[j] match?', options: ['dp[i][j] = dp[i-1][j-1]', 'dp[i][j] = 1 + dp[i-1][j-1]', 'dp[i][j] = max(dp[i-1][j], dp[i][j-1])', 'dp[i][j] = dp[i][j-1] + 1'], correct: 1, explanation: 'When characters match, we extend the LCS of the prefixes by 1.' },
      { q: 'What is the difference between LCS and longest common substring?', options: ['LCS is always shorter', 'LCS elements need not be contiguous, substring must be', 'They are the same', 'Substring allows gaps'], correct: 1, explanation: 'LCS preserves relative order but allows gaps. Substring requires all characters to be adjacent.' },
      { q: 'What is the time complexity of LCS?', options: ['O(m+n)', 'O(m log n)', 'O(mn)', 'O(m²)'], correct: 2, explanation: 'The DP table has m×n cells, each filled in O(1), giving total O(mn) time.' },
      { q: 'What is the LCS of "AGGTAB" and "GXTXAYB"?', options: ['GTAB (length 4)', 'GXTAB (length 5)', 'AGAB (length 4)', 'GTAB has length 4 and is a valid answer'], correct: 3, explanation: '"GTAB" is a common subsequence of length 4 that is indeed the LCS of these two strings. Both option 0 and option 3 say GTAB length 4 — it is correct.' },
      { q: 'If LCS("ABCD", "ABCD") is computed, what is the result?', options: ['0', '2', '4', '8'], correct: 2, explanation: 'When both strings are identical, the LCS is the string itself, with length equal to the full length of either string (4 in this case).' },
      { q: 'How is edit distance related to LCS?', options: ['Edit distance = LCS length', 'Edit distance = m + n - 2 * LCS(s1, s2) when only insertions and deletions are allowed', 'They are unrelated', 'LCS is always larger than edit distance'], correct: 1, explanation: 'With only insertions and deletions (no substitutions), the minimum edits needed equals (m - LCS) deletions from s1 plus (n - LCS) insertions, giving m + n - 2*LCS total operations.' },
    ],
  },

  'edit-distance': {
    concept: {
      overview:
        'Edit Distance (Levenshtein distance) measures the minimum number of single-character operations — insertions, deletions, and substitutions — needed to transform one string into another. For "kitten" to "sitting" the distance is 3. It\'s a fundamental metric in NLP, bioinformatics, and spell checking.',
      keyPoints: [
        { title: 'Three Operations', desc: 'Insert a character, delete a character, or substitute one character for another. Each costs 1. The goal is to minimize the total number of operations.' },
        { title: 'DP Recurrence', desc: 'dp[i][j] = edit distance between s1[:i] and s2[:j]. If chars match: dp[i-1][j-1]. Else: 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) for delete, insert, substitute.' },
        { title: 'Base Cases', desc: 'dp[i][0] = i (delete all chars of s1 prefix). dp[0][j] = j (insert all chars of s2 prefix). These represent transforming to/from an empty string.' },
      ],
    },
    steps: [
      { n: '1', label: 'Create DP table', desc: 'Size (m+1)×(n+1). Base cases: first row = 0,1,2,...,n. First column = 0,1,2,...,m.', code: 'dp = [[0]*(n+1) for _ in range(m+1)]\nfor i in range(m+1): dp[i][0] = i\nfor j in range(n+1): dp[0][j] = j' },
      { n: '2', label: 'Fill the table', desc: 'If s1[i-1]==s2[j-1]: no cost, take diagonal. Else: 1 + min(delete, insert, substitute).', code: 'for i in range(1, m+1):\n    for j in range(1, n+1):\n        if s1[i-1] == s2[j-1]:\n            dp[i][j] = dp[i-1][j-1]\n        else:\n            dp[i][j] = 1 + min(\n                dp[i-1][j],    # delete\n                dp[i][j-1],    # insert\n                dp[i-1][j-1]   # substitute\n            )' },
      { n: '3', label: 'Read answer', desc: 'dp[m][n] is the minimum edit distance.', code: 'return dp[m][n]' },
    ],
    codeExamples: [
      {
        label: 'Edit Distance (Levenshtein)',
        complexity: 'O(mn)',
        code: 'def edit_distance(s1, s2):\n    m, n = len(s1), len(s2)\n    dp = [[0]*(n+1) for _ in range(m+1)]\n\n    # Base cases\n    for i in range(m+1): dp[i][0] = i\n    for j in range(n+1): dp[0][j] = j\n\n    # Fill table\n    for i in range(1, m+1):\n        for j in range(1, n+1):\n            if s1[i-1] == s2[j-1]:\n                dp[i][j] = dp[i-1][j-1]  # free match\n            else:\n                dp[i][j] = 1 + min(\n                    dp[i-1][j],    # delete from s1\n                    dp[i][j-1],    # insert into s1\n                    dp[i-1][j-1]   # substitute\n                )\n\n    return dp[m][n]\n\n# edit_distance("kitten", "sitting") = 3',
      },
      {
        label: 'Space-Optimized (two rows)',
        complexity: 'O(mn) time, O(min(m,n)) space',
        code: 'def edit_distance_opt(s1, s2):\n    if len(s1) < len(s2):\n        s1, s2 = s2, s1\n    m, n = len(s1), len(s2)\n    prev = list(range(n+1))\n\n    for i in range(1, m+1):\n        curr = [i] + [0]*n\n        for j in range(1, n+1):\n            if s1[i-1] == s2[j-1]:\n                curr[j] = prev[j-1]\n            else:\n                curr[j] = 1 + min(prev[j], curr[j-1], prev[j-1])\n        prev = curr\n\n    return prev[n]',
        variant: 'good',
      },
    ],
    complexity: {
      rows: [
        { case: 'Time', value: 'O(mn)', color: 'text-orange-400', note: 'Fill m×n table, each in O(1)' },
        { case: 'Space (full table)', value: 'O(mn)', color: 'text-orange-400', note: 'Full 2D DP table' },
        { case: 'Space (2 rows)', value: 'O(min(m,n))', color: 'text-indigo-400', note: 'Previous row suffices for recurrence' },
      ],
    },
    realWorld: [
      { title: 'Spell Checkers', desc: 'Suggest corrections by finding dictionary words within edit distance 1 or 2 of misspelled input.' },
      { title: 'Autocorrect', desc: 'Mobile keyboards suggest the most likely intended word using edit distance from typed sequence.' },
      { title: 'DNA Mutation Analysis', desc: 'Measuring evolutionary distance between DNA sequences as the number of mutations needed.' },
      { title: 'Fuzzy String Matching', desc: 'Search engines tolerate typos by matching queries to indexed terms within small edit distances.' },
    ],
    quiz: [
      { q: 'What are the three operations in edit distance?', options: ['Insert, delete, swap', 'Insert, delete, substitute', 'Rotate, delete, insert', 'Split, merge, swap'], correct: 1, explanation: 'Levenshtein distance counts insertions, deletions, and substitutions each with cost 1.' },
      { q: 'What is the edit distance between identical strings?', options: ['1', 'Length of string', '0', '-1'], correct: 2, explanation: 'No operations needed to transform a string to itself, so distance is 0.' },
      { q: 'What does dp[i][0] = i represent?', options: ['Length of s1', 'Distance to transform s1[:i] to empty string (i deletions)', 'Distance to transform empty to s2', 'Number of insertions'], correct: 1, explanation: 'To turn s1[:i] into an empty string, we delete all i characters — cost = i.' },
      { q: 'What is the edit distance between "abc" and "abc"?', options: ['0', '1', '3', '6'], correct: 0, explanation: 'Identical strings require zero operations, so edit distance is 0.' },
      { q: 'When s1[i-1] == s2[j-1] in the edit distance DP, why is dp[i][j] = dp[i-1][j-1] (no +1)?', options: ['Characters that match are skipped entirely', 'A matching character requires no edit operation, so we inherit the cost from the prefixes before them', 'The diagonal always has cost 0', 'Both strings shrink by 1 so cost balances out'], correct: 1, explanation: 'When characters match, we do not need any operation for this position. We simply extend the optimal alignment of the shorter prefixes (dp[i-1][j-1]) at zero additional cost.' },
      { q: 'What is the edit distance between "" (empty string) and "hello"?', options: ['0', '1', '5', '10'], correct: 2, explanation: 'Transforming an empty string into "hello" requires 5 insertions (one per character), so edit distance = 5.' },
    ],
  },

  'lis': {
    concept: {
      overview:
        'The Longest Increasing Subsequence (LIS) finds the longest subsequence in which all elements are strictly increasing. For [3,1,4,1,5,9,2,6], the LIS is [1,4,5,9] or [1,4,5,6] (length 4). The O(n²) DP is straightforward; the clever O(n log n) solution uses binary search on a "patience sorting" pile structure.',
      keyPoints: [
        { title: 'O(n²) DP Approach', desc: 'dp[i] = length of LIS ending at index i. For each i, scan all j<i where arr[j]<arr[i] and take max(dp[j])+1. Final answer: max(dp).' },
        { title: 'O(n log n) Binary Search', desc: 'Maintain a "tails" array where tails[k] = smallest tail element of all increasing subsequences of length k+1. Use binary search to update — each element takes O(log n).' },
        { title: 'Subsequence vs Substring', desc: 'Elements must be in order but need not be adjacent. "Increasing" usually means strictly greater (not equal). Check problem constraints carefully.' },
      ],
    },
    steps: [
      { n: '1', label: 'Initialize dp array', desc: 'dp[i] = 1 for all i (every element is an LIS of length 1 by itself).', code: 'dp = [1] * n' },
      { n: '2', label: 'Fill dp', desc: 'For each i, scan all j < i. If arr[j] < arr[i], dp[i] = max(dp[i], dp[j]+1).', code: 'for i in range(1, n):\n    for j in range(i):\n        if arr[j] < arr[i]:\n            dp[i] = max(dp[i], dp[j] + 1)' },
      { n: '3', label: 'Find maximum', desc: 'The answer is max(dp).', code: 'return max(dp)' },
      { n: '4', label: 'O(n log n) with binary search', desc: 'Maintain tails array. For each element, binary search for position to place it.', code: 'import bisect\ntails = []\nfor x in arr:\n    pos = bisect.bisect_left(tails, x)\n    if pos == len(tails): tails.append(x)\n    else: tails[pos] = x\nreturn len(tails)' },
    ],
    codeExamples: [
      {
        label: 'O(n²) DP Solution',
        complexity: 'O(n²)',
        code: 'def lis_dp(arr):\n    n = len(arr)\n    dp = [1] * n  # LIS ending at each index\n\n    for i in range(1, n):\n        for j in range(i):\n            if arr[j] < arr[i]:\n                dp[i] = max(dp[i], dp[j] + 1)\n\n    return max(dp)\n\n# lis_dp([3,1,4,1,5,9,2,6]) = 4',
      },
      {
        label: 'O(n log n) Patience Sorting',
        complexity: 'O(n log n)',
        variant: 'good',
        code: 'import bisect\n\ndef lis_fast(arr):\n    # tails[i] = smallest tail of all LIS of length i+1\n    tails = []\n\n    for x in arr:\n        # Binary search: where does x fit?\n        pos = bisect.bisect_left(tails, x)\n        if pos == len(tails):\n            tails.append(x)   # extend LIS\n        else:\n            tails[pos] = x    # replace (keep tails minimal)\n\n    return len(tails)\n\n# Note: tails is NOT the actual LIS!\n# It gives the correct LENGTH only.\n# lis_fast([3,1,4,1,5,9,2,6]) = 4',
      },
    ],
    complexity: {
      rows: [
        { case: 'DP Solution', value: 'O(n²)', color: 'text-orange-400', note: 'Two nested loops over n elements' },
        { case: 'Binary Search Solution', value: 'O(n log n)', color: 'text-amber-400', note: 'Binary search per element using bisect' },
        { case: 'Space', value: 'O(n)', color: 'text-indigo-400', note: 'dp array or tails array of size n' },
      ],
    },
    realWorld: [
      { title: 'Stock Price Analysis', desc: 'Finding the longest period of consecutive stock price increases to identify trends.' },
      { title: 'Patience Sorting', desc: 'Card game strategy — the number of piles in patience sort equals the LIS length.' },
      { title: 'Box Stacking', desc: '3D box stacking problem reduces to LIS on one dimension after sorting by another.' },
      { title: 'Chain of Pairs', desc: 'Scheduling tasks where each task requires the previous one\'s output to be a certain minimum.' },
    ],
    quiz: [
      { q: 'What is the LIS of [5, 1, 4, 2, 8]?', options: ['[5,4,8]', '[1,2,8]', '[5,8]', '[1,4,8]'], correct: 3, explanation: '[1,4,8] is a strictly increasing subsequence of length 3, which is the longest.' },
      { q: 'What does the "tails" array represent in the O(n log n) solution?', options: ['The actual LIS elements', 'Smallest tail of all increasing subsequences of each length', 'Sorted input array', 'Prefix maxima'], correct: 1, explanation: 'tails[k] stores the smallest possible tail element of any LIS of length k+1 seen so far.' },
      { q: 'How does LIS differ from longest increasing substring?', options: ['LIS allows gaps; substring must be contiguous', 'LIS must be contiguous; substring allows gaps', 'They are identical', 'Substring is always longer'], correct: 0, explanation: 'LIS preserves order but gaps are allowed. Longest increasing substring requires elements to be adjacent.' },
      { q: 'In the O(n log n) LIS algorithm, what does tails[k] store?', options: ['The k-th element of the actual LIS', 'The smallest tail element among all increasing subsequences of length k+1', 'The largest element seen so far', 'The index of the k-th LIS element'], correct: 1, explanation: 'Keeping the smallest possible tail for each length ensures we leave maximum room for future elements to extend the subsequence.' },
      { q: 'For the input [1, 3, 2, 4], what is the length of the LIS?', options: ['2', '3', '4', '1'], correct: 1, explanation: '[1, 3, 4] and [1, 2, 4] are both valid LIS of length 3. No strictly increasing subsequence of length 4 exists since the sequence is not fully sorted.' },
      { q: 'Why does bisect_left (not bisect_right) correctly maintain the tails array in O(n log n) LIS?', options: ['bisect_left handles duplicate values by replacing rather than extending', 'bisect_right is not available in Python', 'bisect_left always inserts at position 0', 'They produce identical results for this problem'], correct: 0, explanation: 'bisect_left finds the leftmost position where x could be inserted, replacing an equal or larger tail. This upholds the strictly increasing constraint — equal values do not extend a strictly increasing subsequence.' },
    ],
  },
};
