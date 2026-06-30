import type { LessonData } from '../../lessons/GenericLesson';

export const realWorldLessons: Record<string, LessonData> = {
  'how-google-search-works': {
    concept: {
      overview: `You type "best pizza near me" and 0.1 seconds later Google shows you millions of ranked results. How? Three interlocking algorithms make this possible: a BFS-based web crawler that maps the internet, an inverted index that lets Google find every page mentioning "pizza" in milliseconds, and PageRank that decides which pages to show first.

Web crawlers start from a seed set of URLs and use Breadth-First Search to fan out across the web — visiting every link they find, adding new links to the queue. Google's crawler visits billions of pages per day this way.

PageRank treats the web as a directed graph where each link is an edge. Pages that receive many high-quality links get higher rank — just like academic papers that are cited by important papers carry more weight. It's essentially an eigenvector computation on a 50-billion-node graph.

The insight is beautiful: you can rank the importance of every page on the internet using only the structure of links between them, without reading the content at all.`,
      keyPoints: [
        {
          title: 'BFS Web Crawling',
          desc: 'Crawlers use a queue (BFS) to discover pages level by level: start with seed URLs → follow every link → add unseen URLs to the queue → repeat. This ensures breadth-first coverage of the web.',
          code: `from collections import deque

def crawl(seed_urls):
    visited = set(seed_urls)
    queue = deque(seed_urls)
    while queue:
        url = queue.popleft()
        links = fetch_and_parse(url)   # download & extract links
        for link in links:
            if link not in visited:
                visited.add(link)
                queue.append(link)`,
        },
        {
          title: 'Inverted Index',
          desc: 'Google builds a massive hash table: word → list of (page, position) pairs. When you search "best pizza", it looks up both words, intersects their page lists, and returns pages containing both — in microseconds.',
          code: `# Building an inverted index
index = {}
for page_id, text in documents.items():
    for word in tokenize(text):
        if word not in index:
            index[word] = []
        index[word].append(page_id)

# Querying: pages with BOTH "best" and "pizza"
results = set(index["best"]) & set(index["pizza"])`,
        },
        {
          title: 'PageRank',
          desc: 'PageRank models a random web surfer: at each page, follow a random link (or teleport to a random page 15% of the time). The fraction of time the surfer spends on each page converges to its PageRank — its importance score.',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Seed the Crawler', desc: 'Start with a set of known trusted URLs (e.g., Wikipedia, major news sites). These go into the crawl queue.' },
      { n: '2', label: 'BFS Traversal', desc: 'Dequeue a URL, download the page, parse all href links. Add unseen links to the queue. Mark visited to avoid loops.' },
      { n: '3', label: 'Build Inverted Index', desc: 'For every word on every page, record which pages contain it. This turns "find pages with X" from O(n pages) to O(1).' },
      { n: '4', label: 'Compute PageRank', desc: 'Run iterative matrix multiplication on the link graph until scores converge. Pages with many high-PR inbound links float to the top.' },
      { n: '5', label: 'Rank & Return', desc: 'Combine relevance (inverted index match quality) with authority (PageRank) to produce the final ranking. Return top 10 in under 100ms.' },
    ],
    codeExamples: [
      {
        label: 'PageRank (simplified)',
        complexity: 'O(iterations × E)',
        variant: 'default',
        code: `def pagerank(graph, d=0.85, iterations=100):
    N = len(graph)
    rank = {node: 1.0 / N for node in graph}

    for _ in range(iterations):
        new_rank = {}
        for node in graph:
            # Sum contributions from all pages linking to this node
            incoming = [src for src, dsts in graph.items() if node in dsts]
            new_rank[node] = (1 - d) / N + d * sum(
                rank[src] / len(graph[src]) for src in incoming
            )
        rank = new_rank
    return rank

# Result: {"wikipedia.org": 0.0043, "tiny-blog.com": 0.0000001, ...}`,
      },
      {
        label: 'BFS Web Crawler',
        complexity: 'O(V + E) — V pages, E links',
        variant: 'good',
        code: `from collections import deque

def web_crawl(seeds, max_pages=1000):
    visited = set(seeds)
    queue = deque(seeds)
    index = {}          # word → [page_ids]

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        try:
            html = fetch(url)
            # Index this page's words
            for word in extract_words(html):
                index.setdefault(word, []).append(url)
            # Discover new links
            for link in extract_links(html):
                if link not in visited:
                    visited.add(link)
                    queue.append(link)
        except Exception:
            pass  # Skip broken pages

    return index`,
      },
    ],
    complexity: {
      rows: [
        { case: 'BFS Crawl', value: 'O(V + E)', color: 'text-emerald-400', note: 'V = pages, E = links' },
        { case: 'Index Lookup', value: 'O(1)', color: 'text-emerald-400', note: 'Hash table per word' },
        { case: 'Query (intersection)', value: 'O(k)', color: 'text-emerald-400', note: 'k = results count' },
        { case: 'PageRank', value: 'O(i × E)', color: 'text-amber-400', note: 'i = iterations (~50)' },
      ],
      note: 'Google runs PageRank on a ~50 billion node graph. They use distributed computing, not a single machine.',
    },
    realWorld: [
      { title: 'Google Search', desc: 'Processes 99,000 searches per second. Every result page required crawling, indexing, and ranking billions of pages.' },
      { title: 'Academic Citation', desc: 'Google Scholar uses the same PageRank logic to rank research papers — highly cited papers from top journals rank highest.' },
    ],
    commonMistakes: [
      { wrong: 'Thinking Google reads your query in real time', right: 'All work is done in advance', explain: 'When you search, Google looks up pre-built indexes and pre-computed PageRanks. The hard work happens before you ever search.' },
      { wrong: 'Assuming more links always = higher rank', explain: 'PageRank cares about the quality of links, not just quantity. A link from one authoritative site can outweigh 1000 links from spam blogs.' },
    ],
    quiz: [
      { q: 'What traversal algorithm does a web crawler use to discover new pages?', options: ['DFS (depth-first)', 'BFS (breadth-first)', 'Dijkstra', 'A*'], correct: 1, explanation: 'Web crawlers use BFS via a URL queue — they process pages level by level, discovering new links and adding them to the queue.' },
      { q: 'What does an inverted index map?', options: ['Page URL → content', 'Word → list of pages containing it', 'Page → its PageRank score', 'URL → all outbound links'], correct: 1, explanation: 'An inverted index maps each word to the list of pages (documents) that contain it, enabling O(1) lookup for any search term.' },
      { q: 'How does PageRank determine a page\'s importance?', options: ['By counting the total words on the page', 'By measuring how fast the page loads', 'By the number and quality of inbound links', 'By how recently the page was updated'], correct: 2, explanation: 'PageRank scores pages based on the quantity and quality of pages linking to them — like an academic citation count, but for the web.' },
      { q: 'Why is a link from a high-PageRank site worth more than many links from low-ranked sites?', options: ['High-PR sites have more visitors', 'PageRank distributes its own score through outbound links', 'Search engines trust verified sites', 'Low-ranked links are ignored'], correct: 1, explanation: 'PageRank flows through links: when a high-PR page links to you, it passes proportionally more of its PageRank score, elevating your own rank.' },
      { q: 'What data structure makes query intersection (finding pages with BOTH "best" AND "pizza") fast?', options: ['Sorted array + binary search', 'Hash sets with intersection', 'Graph BFS', 'Priority queue'], correct: 1, explanation: 'Storing each word\'s page list as a hash set allows O(n) set intersection, finding pages containing all query words efficiently.' },
      { q: 'Why does Google pre-build indexes and PageRanks instead of computing them live when you search?', options: ['It would violate user privacy', 'Live computation would take hours, not milliseconds', 'The algorithms only work on static data', 'Legal requirements mandate pre-computation'], correct: 1, explanation: 'Real-time PageRank on 50B pages would be impossibly slow. Pre-computation (done offline) means lookups at query time take milliseconds.' },
    ],
  },

  'how-gps-works': {
    concept: {
      overview: `You tap "navigate to airport" and within seconds your phone finds the fastest route through thousands of roads. This is Dijkstra's algorithm — invented by Edsger Dijkstra in 1959 while thinking about the shortest path between two Dutch cities.

The road network is a weighted graph: intersections are nodes, roads are edges, and driving time is the edge weight. Dijkstra's algorithm starts at your current location and "relaxes" edges outward in order of cumulative time — always processing the closest unvisited node next.

A* (pronounced "A star") is the GPS's actual workhorse. It improves on Dijkstra by adding a heuristic: the straight-line distance to the destination. This guides the search toward the destination rather than exploring uniformly in all directions, making it dramatically faster on large maps.

When you ask Google Maps for "avoid toll roads", it applies constraints to edge traversal. When it gives live traffic updates, it's re-running the algorithm with updated edge weights in real time. A city's entire road graph fits comfortably in memory (San Francisco has ~50K intersections), and modern smartphones can run this in under a second.`,
      keyPoints: [
        {
          title: "Dijkstra's Algorithm",
          desc: 'Uses a min-heap priority queue. Always processes the node with the smallest cumulative distance from the source. When a shorter path to a node is found, it "relaxes" that node\'s distance.',
          code: `import heapq

def dijkstra(graph, source):
    dist = {node: float('inf') for node in graph}
    dist[source] = 0
    heap = [(0, source)]      # (cumulative_time, node)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]: continue   # stale entry
        for v, weight in graph[u]:
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                heapq.heappush(heap, (dist[v], v))

    return dist`,
        },
        {
          title: 'A* Search',
          desc: 'Adds a heuristic h(n) = straight-line distance to goal. Priority = actual_cost + heuristic. This focuses the search toward the destination, skipping roads going the wrong direction.',
          code: `def heuristic(node, goal, coords):
    # Haversine distance (straight-line on Earth's surface)
    lat1, lon1 = coords[node]
    lat2, lon2 = coords[goal]
    return haversine(lat1, lon1, lat2, lon2)

# A* uses f(n) = g(n) + h(n)
# g(n) = actual time from start
# h(n) = estimated time to goal (never overestimates)`,
        },
        {
          title: 'Live Traffic Updates',
          desc: 'Edge weights change as traffic data comes in. Google Maps re-runs A* periodically during your trip, which is why it reroutes you when a new jam appears ahead.',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Build the Road Graph', desc: 'Every intersection is a node. Every road segment is a directed edge with a weight = estimated travel time (based on speed limit + current traffic).' },
      { n: '2', label: 'Initialize Priority Queue', desc: 'Insert your current location with cost 0. All other nodes start at infinity. This is the starting state of Dijkstra / A*.' },
      { n: '3', label: 'Expand Nearest Node', desc: 'Pop the intersection with the lowest accumulated cost. Examine all roads leaving it. If a road offers a shorter total path to the next intersection, update it.' },
      { n: '4', label: 'Relax Edges', desc: 'For each neighbor, if (current_cost + road_time) < neighbor\'s best known cost, update and re-insert into the priority queue.' },
      { n: '5', label: 'Reach Destination', desc: 'When the destination node is popped from the heap, its cost is guaranteed to be the shortest path. Backtrack through parent pointers to reconstruct the route.' },
    ],
    codeExamples: [
      {
        label: "Dijkstra's shortest path",
        complexity: 'O((V + E) log V)',
        variant: 'default',
        code: `import heapq

def shortest_path(graph, start, end):
    dist = {start: 0}
    prev = {start: None}
    heap = [(0, start)]

    while heap:
        cost, u = heapq.heappop(heap)
        if u == end:
            break
        if cost > dist.get(u, float('inf')):
            continue
        for v, weight in graph.get(u, []):
            new_cost = cost + weight
            if new_cost < dist.get(v, float('inf')):
                dist[v] = new_cost
                prev[v] = u
                heapq.heappush(heap, (new_cost, v))

    # Reconstruct path
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = prev.get(node)
    return list(reversed(path)), dist.get(end, float('inf'))`,
      },
      {
        label: 'A* with geographic heuristic',
        complexity: 'O((V + E) log V) — faster in practice',
        variant: 'good',
        code: `import heapq, math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def astar(graph, coords, start, goal):
    h = lambda n: haversine(*coords[n], *coords[goal])
    open_set = [(h(start), 0, start)]
    g_cost = {start: 0}

    while open_set:
        _, g, u = heapq.heappop(open_set)
        if u == goal: return g
        for v, w in graph.get(u, []):
            ng = g + w
            if ng < g_cost.get(v, float('inf')):
                g_cost[v] = ng
                heapq.heappush(open_set, (ng + h(v), ng, v))`,
      },
    ],
    complexity: {
      rows: [
        { case: "Dijkstra's", value: 'O((V+E) log V)', color: 'text-amber-400', note: 'V = intersections, E = road segments' },
        { case: 'A* (typical GPS)', value: 'O((V+E) log V)', color: 'text-emerald-400', note: 'Much faster in practice due to heuristic' },
        { case: 'Space', value: 'O(V)', color: 'text-emerald-400', note: 'Stores distance + parent for each node' },
      ],
      note: 'San Francisco has ~50K intersections. A* on a smartphone finds routes in under 100ms even for cross-country trips.',
    },
    realWorld: [
      { title: 'Google Maps & Waze', desc: 'Both use A* on massive road graphs with real-time traffic weights. Waze also crowd-sources traffic data from millions of active drivers.' },
      { title: 'Network Routing', desc: 'Internet routers use similar shortest-path algorithms (OSPF uses Dijkstra) to find the fastest path for your packets through the internet.' },
    ],
    commonMistakes: [
      { wrong: 'Using BFS for weighted shortest paths', right: 'Use Dijkstra or A*', explain: 'BFS finds the path with fewest hops, not shortest time. On a road network where a short road might take longer due to traffic, BFS gives wrong answers.' },
      { wrong: 'Forgetting to check for stale heap entries', explain: 'When you update a node\'s distance, the old entry stays in the heap. Always check if the popped cost matches the current known distance before processing.' },
    ],
    quiz: [
      { q: 'What does "edge weight" represent in a GPS road graph?', options: ['The physical length of the road in meters', 'The number of traffic lights on the road', 'The estimated travel time on that road segment', 'The speed limit of the road'], correct: 2, explanation: 'GPS graphs use travel time (not distance) as edge weights, incorporating speed limits, traffic, and road type.' },
      { q: "What data structure does Dijkstra's algorithm use to always process the nearest node next?", options: ['Stack (LIFO)', 'Regular queue (FIFO)', 'Min-heap priority queue', 'Hash map'], correct: 2, explanation: 'A min-heap lets Dijkstra always extract the unvisited node with the lowest cumulative cost in O(log V) time.' },
      { q: 'How does A* improve on Dijkstra for GPS navigation?', options: ['It uses multiple CPU cores', 'It adds a straight-line distance estimate to guide search toward the goal', 'It pre-computes all possible routes', 'It limits the graph to major highways'], correct: 1, explanation: 'A* adds a heuristic h(n) — the straight-line distance to the goal — to the priority function, directing the search toward the destination and skipping irrelevant roads.' },
      { q: 'When you ask for "avoid tolls", what changes in the algorithm?', options: ['The heuristic function changes', 'Toll road edges are removed or given infinite weight', 'A different algorithm is used entirely', 'The graph is rebuilt from scratch'], correct: 1, explanation: 'Toll roads simply get very high (or infinite) edge weights, so the shortest-path algorithm naturally avoids them when seeking the minimum-cost route.' },
      { q: 'Why does GPS reroute when traffic suddenly appears ahead?', options: ['The algorithm is running continuously', 'Edge weights are updated with real-time traffic, and A* is re-run', 'GPS uses a pre-computed offline route database', 'Satellites detect your new route automatically'], correct: 1, explanation: 'Traffic data continuously updates edge weights. GPS periodically re-runs A* with new weights, triggering a reroute if a faster alternative now exists.' },
      { q: "What is the time complexity of Dijkstra's algorithm with a binary heap?", options: ['O(V²)', 'O(V + E)', 'O((V + E) log V)', 'O(V log E)'], correct: 2, explanation: 'With a binary min-heap, each of the V extractions costs O(log V) and each of the E edge relaxations costs O(log V), giving O((V+E) log V) total.' },
    ],
  },

  'how-netflix-recommends': {
    concept: {
      overview: `Netflix's homepage is different for every one of its 260 million subscribers. You see different thumbnails, different rows, even different orderings — all personalized. How does an algorithm learn your taste better than your closest friends?

The secret is collaborative filtering: "people who liked what you liked also liked X." Build a bipartite graph connecting users to movies they've rated. To recommend movies to you, Netflix finds users with similar taste graphs, then traverses to movies those users loved that you haven't seen yet.

But Netflix doesn't just use what you explicitly rate. They track implicit signals too: did you pause 10 minutes into a movie and never return? Did you finish a documentary at 2am? Did you rewatch the same episode? All of these update your taste profile in real time.

The core insight: your preferences aren't random — they cluster. People who love Christopher Nolan films tend to also love Denis Villeneuve films. Once you find your "cluster" of similar users, their collective wisdom predicts your preferences with surprising accuracy. This is fundamentally a graph problem solved with matrix decomposition and nearest-neighbor search.`,
      keyPoints: [
        {
          title: 'User-Item Similarity Graph',
          desc: 'Build a bipartite graph: users on one side, movies on the other. An edge with weight = rating connects users to movies they rated. Finding similar users = finding users with overlapping edge sets.',
          code: `# Cosine similarity between two users' rating vectors
def user_similarity(ratings, user_a, user_b):
    movies_a = set(ratings[user_a].keys())
    movies_b = set(ratings[user_b].keys())
    common = movies_a & movies_b
    if not common: return 0

    dot = sum(ratings[user_a][m] * ratings[user_b][m] for m in common)
    norm_a = sum(v**2 for v in ratings[user_a].values()) ** 0.5
    norm_b = sum(v**2 for v in ratings[user_b].values()) ** 0.5
    return dot / (norm_a * norm_b)`,
        },
        {
          title: 'Collaborative Filtering',
          desc: 'For each movie you haven\'t seen, predict your rating by taking a weighted average of similar users\' ratings. Recommend movies with the highest predicted ratings.',
        },
        {
          title: 'Matrix Factorization',
          desc: 'Netflix\'s actual approach: decompose the user×movie rating matrix into two smaller matrices (user features × latent factors × movie features). Users and movies are mapped to the same latent space; similarity = dot product.',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Collect Implicit & Explicit Signals', desc: 'Track what you watch, how long, when you rewatch, what you pause. Each interaction updates your taste vector.' },
      { n: '2', label: 'Build Similarity Graph', desc: 'For each pair of users, compute cosine similarity of their rating vectors. Store k-nearest neighbors per user (k ≈ 100-200).' },
      { n: '3', label: 'Find Your Neighborhood', desc: 'At recommendation time, retrieve your k most similar users in O(k) using pre-computed neighbors.' },
      { n: '4', label: 'Aggregate Neighbor Preferences', desc: 'For each movie your neighbors loved that you haven\'t seen, compute a predicted rating = weighted average of neighbor ratings.' },
      { n: '5', label: 'Rank & Present', desc: 'Sort candidate movies by predicted rating. Apply business rules (diversity, freshness, licensing). Present as personalized rows with personalized thumbnails.' },
    ],
    codeExamples: [
      {
        label: 'Collaborative filtering recommendation',
        complexity: 'O(U × M) to build, O(k × M) to predict',
        variant: 'default',
        code: `def recommend(user_id, ratings, similarity, k=50, n=10):
    # Find k most similar users
    neighbors = sorted(
        (uid for uid in ratings if uid != user_id),
        key=lambda uid: similarity(ratings, user_id, uid),
        reverse=True
    )[:k]

    # Movies the user hasn't seen
    seen = set(ratings.get(user_id, {}).keys())
    candidates = {}

    for neighbor in neighbors:
        sim = similarity(ratings, user_id, neighbor)
        for movie, rating in ratings[neighbor].items():
            if movie not in seen:
                if movie not in candidates:
                    candidates[movie] = (0, 0)  # (weighted_sum, weight_sum)
                ws, w = candidates[movie]
                candidates[movie] = (ws + sim * rating, w + sim)

    # Predicted ratings
    predicted = {m: ws / w for m, (ws, w) in candidates.items()}
    return sorted(predicted, key=predicted.get, reverse=True)[:n]`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Similarity computation', value: 'O(U²× M)', color: 'text-red-400', note: 'Done offline, cached' },
        { case: 'Retrieve k neighbors', value: 'O(k)', color: 'text-emerald-400', note: 'From pre-built index' },
        { case: 'Predict ratings', value: 'O(k × M)', color: 'text-amber-400', note: 'k=100, M=5000 candidates' },
        { case: 'Space (rating matrix)', value: 'O(U × M)', color: 'text-amber-400', note: 'Sparse in practice' },
      ],
      note: 'Netflix processes 100M+ ratings. They use distributed matrix factorization (SGD), not direct similarity — which scales much better.',
    },
    realWorld: [
      { title: 'Netflix', desc: '80% of shows watched on Netflix come from their recommendation algorithm — not from users searching manually. The algorithm drives the majority of viewing.' },
      { title: 'Spotify Discover Weekly', desc: 'Uses collaborative filtering + audio analysis. Your Discover Weekly playlist is generated by finding users with similar listening graphs and extracting songs they loved that you missed.' },
    ],
    commonMistakes: [
      { wrong: 'Thinking Netflix just recommends what is "popular"', explain: 'Popularity-based recommendations work poorly. Most people don\'t want to watch the same blockbuster everyone else is watching. Collaborative filtering finds your specific niche.' },
      { wrong: 'Cold start problem: recommending to new users', explain: 'With no rating history, similarity can\'t be computed. Netflix solves this by asking new users to rate a few titles during onboarding — gathering just enough data to bootstrap recommendations.' },
    ],
    quiz: [
      { q: 'What does "collaborative filtering" mean in recommendation systems?', options: ['Users explicitly collaborate to write reviews together', 'Users who liked what you liked tend to like similar things', 'The algorithm filters out content you have already watched', 'Netflix employees manually curate recommendations'], correct: 1, explanation: 'Collaborative filtering leverages the collective behavior of similar users: find people who rated things like you did, then recommend what they loved that you haven\'t seen.' },
      { q: 'What type of graph structure represents users and movies in collaborative filtering?', options: ['Directed graph', 'Bipartite graph', 'Complete graph', 'Tree'], correct: 1, explanation: 'A bipartite graph has two distinct node sets (users and movies) with edges only between sets (user rated movie), never within the same set.' },
      { q: 'What metric is commonly used to measure how similar two users\' tastes are?', options: ['Hamming distance', 'Manhattan distance', 'Cosine similarity', 'Euclidean distance'], correct: 2, explanation: 'Cosine similarity measures the angle between two rating vectors — users who rate the same movies similarly (regardless of scale) have high cosine similarity.' },
      { q: 'What is the "cold start problem" in recommendation systems?', options: ['The server takes too long to start up', 'New users have no history, making similarity impossible to compute', 'Old recommendations become stale over time', 'The algorithm runs out of movies to recommend'], correct: 1, explanation: 'Without any viewing history, there\'s no data to compute similarity with other users. Netflix solves this by asking new users to rate a few titles during onboarding.' },
      { q: 'Why does Netflix use matrix factorization instead of raw cosine similarity at scale?', options: ['Matrix factorization gives better accuracy on small datasets', 'It reduces O(U² × M) similarity computation to something tractable for 260M users', 'Matrix operations are easier to implement', 'Cosine similarity doesn\'t work on rating data'], correct: 1, explanation: 'Computing pairwise similarity between 260M users is infeasible. Matrix factorization decomposes the rating matrix into compact user and movie embeddings, making similarity a simple dot product in low-dimensional space.' },
      { q: 'Besides explicit ratings, what implicit signals does Netflix track?', options: ['Only explicit 5-star ratings', 'What you search for in other apps', 'Watch time, rewatch behavior, pause points, time of day watched', 'Your social media posts about movies'], correct: 2, explanation: 'Implicit signals are often more powerful than explicit ratings. Finishing a movie at 2am or rewatching an episode signals strong preference without requiring the user to click a star.' },
    ],
  },

  'how-compression-works': {
    concept: {
      overview: `Right now, every photo you send, every file you download, and every song you stream is compressed. Without compression, a single HD movie would be 50 GB. With compression, it's under 4 GB. How?

Huffman coding is the elegant algorithm at the heart of ZIP, JPEG, and MP3 compression. The key observation: in any English text, 'e' appears far more often than 'z'. If you encode 'e' with fewer bits and 'z' with more bits, you use less total space — even though some characters take more space.

Huffman's algorithm builds an optimal prefix-free code using a greedy approach: always merge the two least-frequent symbols. Repeat until you have a single tree. The path from root to each leaf (0 = go left, 1 = go right) defines that character's bit code.

The resulting code is mathematically optimal — no other prefix-free code can represent the same data in fewer bits. It achieves entropy (the theoretical minimum). This is why Huffman coding is everywhere: it's not just good, it's provably the best possible fixed-statistics code.`,
      keyPoints: [
        {
          title: 'Frequency Analysis',
          desc: 'Count how often each character appears. Common characters get short codes; rare ones get long codes. In English text, "the" alone accounts for 6% of all words.',
          code: `from collections import Counter

text = "huffman coding is elegant"
freq = Counter(text)
# {'e': 3, ' ': 3, 'i': 2, 'n': 2, ...}
# 'e' appears most → gets the shortest bit code`,
        },
        {
          title: 'Build the Huffman Tree (Greedy)',
          desc: 'Use a min-heap. Repeatedly extract the two nodes with lowest frequency, merge them into a parent node with combined frequency, and reinsert. Repeat until one tree remains.',
          code: `import heapq

def build_tree(freq):
    heap = [[f, [ch, ""]] for ch, f in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]: pair[1] = '0' + pair[1]
        for pair in hi[1:]: pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0]+hi[0]] + lo[1:] + hi[1:])
    return sorted(heap[0][1:], key=lambda x: len(x[1]))`,
        },
        {
          title: 'Encode & Decode',
          desc: 'Replace each character with its Huffman code. To decode: walk the tree bit by bit — 0 = left, 1 = right — until a leaf is reached. The code is prefix-free, so decoding is always unambiguous.',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Count Frequencies', desc: 'Scan the input and count how often each character (or byte, or symbol) appears. O(n) pass through the data.' },
      { n: '2', label: 'Build Min-Heap', desc: 'Create a leaf node for each unique character, weighted by frequency. Insert all into a min-heap.' },
      { n: '3', label: 'Merge Greedily', desc: 'Extract the two minimum-frequency nodes. Merge into a parent node with frequency = sum of both. Reinsert the parent. Repeat until 1 node remains.' },
      { n: '4', label: 'Assign Codes', desc: 'Traverse the final tree. At each left branch, append "0". At each right branch, append "1". Each leaf\'s path is its Huffman code.' },
      { n: '5', label: 'Encode Data', desc: 'Replace every character in the original with its Huffman code. Write bits to output. Store the tree alongside (needed for decoding).' },
    ],
    codeExamples: [
      {
        label: 'Huffman encoding (full)',
        complexity: 'O(n + k log k) — n input length, k unique symbols',
        variant: 'default',
        code: `import heapq
from collections import Counter

def huffman_encode(text):
    freq = Counter(text)
    heap = [[f, [ch, ""]] for ch, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]: pair[1] = '0' + pair[1]
        for pair in hi[1:]: pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0]+hi[0]] + lo[1:] + hi[1:])

    codes = {ch: code for ch, code in heap[0][1:]}

    # Encode
    encoded = ''.join(codes[ch] for ch in text)
    original_bits = len(text) * 8
    compressed_bits = len(encoded)
    ratio = (1 - compressed_bits / original_bits) * 100

    print(f"Original:    {original_bits} bits")
    print(f"Compressed:  {compressed_bits} bits ({ratio:.1f}% smaller)")
    return encoded, codes

# Example on "huffman coding is elegant and optimal"
# Result: ~35-40% compression on natural language`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Frequency count', value: 'O(n)', color: 'text-emerald-400', note: 'Single pass through data' },
        { case: 'Build Huffman tree', value: 'O(k log k)', color: 'text-emerald-400', note: 'k = unique symbols (≤ 256 for bytes)' },
        { case: 'Encode data', value: 'O(n)', color: 'text-emerald-400', note: 'Replace each char with its code' },
        { case: 'Space', value: 'O(k)', color: 'text-emerald-400', note: 'Store tree for decoding' },
      ],
      note: 'Huffman coding achieves the theoretical entropy limit for symbol-by-symbol codes. Modern compressors (zlib, brotli) combine Huffman with LZ77 dictionary compression for even better ratios.',
    },
    realWorld: [
      { title: 'ZIP / gzip / brotli', desc: 'All use Huffman coding as a final stage. The LZ77 algorithm first finds repeated sequences, then Huffman codes the remaining symbols.' },
      { title: 'JPEG & PNG Images', desc: 'JPEG uses Huffman coding to compress the DCT (frequency domain) coefficients. PNG uses a predictor + deflate (which is Huffman). Lossy vs lossless depends on the stage before Huffman.' },
    ],
    commonMistakes: [
      { wrong: 'Thinking Huffman is lossy (loses data)', right: 'Huffman is lossless', explain: 'Huffman coding is perfectly lossless — the original data can be perfectly reconstructed. JPEG feels lossy because of the DCT quantization step before Huffman, not Huffman itself.' },
      { wrong: 'Compressing already-compressed data', explain: 'If you ZIP a JPEG or MP3, the file barely shrinks. The entropy is already minimized. Huffman can only compress when frequencies are unequal — already-compressed data looks random.' },
    ],
    quiz: [
      { q: 'What is the core idea behind Huffman coding?', options: ['Assign equal-length codes to all characters', 'Assign shorter codes to more frequent characters', 'Remove duplicate characters from the text', 'Encrypt data to make it smaller'], correct: 1, explanation: 'Huffman assigns shorter bit sequences to more frequent characters and longer sequences to rarer ones, reducing total bits while preserving all information.' },
      { q: 'What data structure is used to build the Huffman tree efficiently?', options: ['Stack', 'Queue', 'Min-heap (priority queue)', 'Hash table'], correct: 2, explanation: 'A min-heap always gives O(log k) access to the two lowest-frequency nodes, which is exactly what the greedy merging step needs.' },
      { q: 'Is Huffman coding lossy or lossless?', options: ['Lossy — some data is discarded', 'Lossless — original data is perfectly recoverable', 'It depends on the compression ratio chosen', 'It is lossy for images, lossless for text'], correct: 1, explanation: 'Huffman coding is perfectly lossless. Every bit of the original data can be recovered exactly by decoding the Huffman tree.' },
      { q: 'What makes Huffman coding "optimal" for prefix-free codes?', options: ['It always achieves 50% compression', 'No other prefix-free code can represent the same data in fewer expected bits', 'It uses the fewest unique characters', 'It runs in O(1) time'], correct: 1, explanation: 'Huffman coding is provably optimal among all prefix-free codes — it minimizes the expected bit length given the symbol frequencies. This is a consequence of Shannon\'s entropy theorem.' },
      { q: 'Why does compressing an already-compressed ZIP file not help?', options: ['ZIP files have a protection flag that prevents re-compression', 'Compressed data has near-uniform byte frequencies (high entropy), leaving nothing for Huffman to exploit', 'The file system prevents double compression', 'ZIP uses a different algorithm than Huffman'], correct: 1, explanation: 'Huffman works by exploiting frequency imbalances. After compression, all byte values appear roughly equally often (the output looks random), so there\'s nothing left to exploit.' },
      { q: 'Which of these real-world formats uses Huffman coding?', options: ['Only ZIP files', 'Only JPEG images', 'ZIP, JPEG, MP3, PNG, HTTP compression (gzip)', 'Only text files'], correct: 2, explanation: 'Huffman coding is ubiquitous: it\'s used in ZIP (as part of deflate), JPEG (to compress DCT coefficients), MP3, PNG, gzip, brotli, and many more.' },
    ],
  },

  'how-passwords-stay-safe': {
    concept: {
      overview: `LinkedIn was breached in 2012. 117 million passwords were stolen. Yet most users were still safe, because LinkedIn stored hashed passwords — not the passwords themselves. What does that mean?

A cryptographic hash function takes any input and produces a fixed-size "fingerprint". SHA-256 produces a 256-bit output. The crucial property: it's a one-way function. Computing the hash is trivial. Finding an input that produces a given hash is computationally impossible (would take longer than the age of the universe with current hardware).

When you create a password, the server hashes it and stores only the hash. When you log in, it hashes what you typed and compares hashes. The server never sees your actual password — and if the database is stolen, hackers only get hashes.

But there's a catch: if two users have the same password, they get the same hash. Hackers use "rainbow tables" — precomputed hash→password lookups — to crack weak hashes. The fix is "salting": add a unique random string to each password before hashing. Now identical passwords produce different hashes, and rainbow tables are useless.`,
      keyPoints: [
        {
          title: 'Hash Function Properties',
          desc: 'Three critical properties: (1) Deterministic: same input → same hash always. (2) One-way: hash → input is infeasible. (3) Avalanche effect: changing one bit changes ~50% of output bits.',
          code: `import hashlib

# SHA-256 in Python
password = "mysecretpassword"
h = hashlib.sha256(password.encode()).hexdigest()
print(h)
# → "89e0a50e6e53...a96" (64 hex characters = 256 bits)

# Even a tiny change → completely different hash
h2 = hashlib.sha256("mysecretpasswort".encode()).hexdigest()
# → "d4c27f9e3b..." — entirely different!`,
        },
        {
          title: 'Salting Against Rainbow Tables',
          desc: 'A salt is a unique random string stored alongside each user\'s hash. It\'s prepended to the password before hashing. Identical passwords → different salts → completely different hashes.',
          code: `import hashlib, os

def hash_password(password: str) -> tuple[str, str]:
    salt = os.urandom(32).hex()          # 32 random bytes
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hashed, salt                  # store both in DB

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    return hashlib.sha256((salt + password).encode()).hexdigest() == stored_hash`,
        },
        {
          title: 'bcrypt / Argon2 — Slow by Design',
          desc: 'SHA-256 hashes a billion passwords per second on a GPU. Modern password hashing uses bcrypt or Argon2 — intentionally slow algorithms designed to take 100ms per hash. This makes brute-force attacks take centuries instead of seconds.',
        },
      ],
    },
    steps: [
      { n: '1', label: 'User Creates Password', desc: 'User types "mysecret123". Server generates a random salt (e.g., "a9f3b2c8...").' },
      { n: '2', label: 'Combine and Hash', desc: 'Concatenate salt + password → "a9f3b2c8mysecret123". Run bcrypt/Argon2. Store (hash, salt) in the database. Discard the original password immediately.' },
      { n: '3', label: 'User Logs In', desc: 'User types "mysecret123" again. Server looks up their stored salt and hash.' },
      { n: '4', label: 'Verify', desc: 'Compute hash(salt + typed_password). Compare with stored hash. Match → authenticate. No match → reject. The server never reconstructs the original password.' },
      { n: '5', label: 'Data Breach Scenario', desc: 'Attacker steals the database — they get (hash, salt) pairs. Without knowing the password, they can\'t reverse the hash. They must guess each password, hash it with the salt, and compare — taking years with bcrypt.' },
    ],
    codeExamples: [
      {
        label: 'Secure password hashing with bcrypt',
        complexity: 'O(2^cost) per hash — intentionally slow',
        variant: 'good',
        code: `import bcrypt

# Registration: hash the password
def register_user(username: str, password: str):
    # bcrypt automatically generates a salt and includes it in the hash
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    # Store username + hashed (salt is embedded in the hash string)
    db.save(username, hashed)

# Login: verify the password
def login(username: str, password: str) -> bool:
    stored_hash = db.get(username)
    # bcrypt.checkpw extracts the embedded salt and compares
    return bcrypt.checkpw(password.encode(), stored_hash)

# Why rounds=12?
# rounds=10 → ~100ms per hash (good)
# rounds=12 → ~400ms per hash (better)
# rounds=14 → ~1600ms per hash (very strong, use for high-value accounts)`,
      },
    ],
    complexity: {
      rows: [
        { case: 'SHA-256 (fast — avoid for passwords)', value: 'O(n)', color: 'text-red-400', note: '~1 billion/sec on GPU' },
        { case: 'bcrypt (rounds=12)', value: 'O(2^12)', color: 'text-emerald-400', note: '~400ms — attacker checks 2-3 passwords/second' },
        { case: 'Argon2 (modern standard)', value: 'O(time × memory)', color: 'text-emerald-400', note: 'Adjustable time + memory cost' },
        { case: 'Space per user', value: 'O(1)', color: 'text-emerald-400', note: 'Just store the hash string (~60 bytes)' },
      ],
      note: 'Speed is the enemy of password security. A fast hash lets attackers try billions of guesses. bcrypt\'s slowness is a feature, not a bug.',
    },
    realWorld: [
      { title: 'The LinkedIn Breach (2012)', desc: '117M passwords leaked. Those stored as plain SHA-1 (fast, unsalted) were cracked within days. SHA-1 salted took weeks. Properly bcrypt-hashed passwords were never cracked.' },
      { title: 'Blockchain / Bitcoin', desc: 'SHA-256 is used to "mine" Bitcoin. Miners hash block headers millions of times per second, looking for a hash starting with enough zeros. This makes blocks hard to forge.' },
    ],
    commonMistakes: [
      { wrong: 'Storing passwords in plaintext "encrypted"', right: 'Hash passwords, never encrypt', explain: 'Encryption is two-way — if you have the key, you can decrypt. Hashing is one-way — even the server can\'t recover the password. Use hashing, not encryption, for passwords.' },
      { wrong: 'Using MD5 or SHA-1 for passwords', right: 'Use bcrypt, Argon2, or scrypt', explain: 'MD5 and SHA-1 are fast (billions per second on a GPU). That\'s great for checksums, terrible for passwords. Use password-specific algorithms designed to be slow.' },
    ],
    quiz: [
      { q: 'Why is a hash function called "one-way"?', options: ['It only accepts one type of input', 'You can compute hash(input) easily but not input from hash(input)', 'It can only hash each password once', 'It runs on a single CPU core'], correct: 1, explanation: 'Computing the hash from input is trivial (milliseconds). Finding an input that produces a given hash requires trying ~2^256 possibilities — computationally infeasible.' },
      { q: 'What is the purpose of a "salt" in password hashing?', options: ['To speed up the hashing process', 'To encrypt the password before hashing', 'To ensure identical passwords produce different hashes, defeating precomputed rainbow tables', 'To add an extra layer of encryption'], correct: 2, explanation: 'A salt is a unique random value mixed into each password before hashing. Two users with the same password get different hashes, making mass lookup attacks (rainbow tables) useless.' },
      { q: 'Why is bcrypt preferred over SHA-256 for passwords?', options: ['bcrypt produces longer hashes', 'bcrypt is a newer algorithm', 'bcrypt is intentionally slow (~400ms), making brute-force attacks impractically slow', 'bcrypt is more secure mathematically'], correct: 2, explanation: 'SHA-256 can hash a billion passwords per second on a GPU. bcrypt takes ~400ms per hash by design, reducing an attacker\'s throughput to about 2-3 guesses per second.' },
      { q: 'When a website is breached and hashed passwords are stolen, what must an attacker do to crack them?', options: ['Decrypt the hashes using the server\'s private key', 'Guess passwords, hash each guess, and compare to stored hashes', 'Request the original passwords from the server', 'Use the salt values to reverse the hash'], correct: 1, explanation: 'Without reversibility, attackers must brute-force: guess a password, compute hash(salt + guess), compare to stored hash. With bcrypt, this takes impractically long for strong passwords.' },
      { q: 'What property ensures a 1-character change in a password produces a completely different hash?', options: ['Determinism', 'Collision resistance', 'Avalanche effect', 'Prefix-free property'], correct: 2, explanation: 'The avalanche effect means a small input change causes ~50% of output bits to flip. This prevents attackers from making small adjustments to a guessed hash to find nearby passwords.' },
      { q: 'Which approach is correct for a web application storing user passwords?', options: ['Store passwords encrypted with AES', 'Store passwords as SHA-256 hashes', 'Store passwords as bcrypt hashes with per-user salts', 'Store passwords in plaintext for easy verification'], correct: 2, explanation: 'bcrypt with per-user salts is the modern best practice. It\'s slow enough to deter brute force, salted to prevent rainbow tables, and one-way so even admins can\'t see passwords.' },
    ],
  },

  'how-social-networks-work': {
    concept: {
      overview: `"People You May Know." This feature — appearing in some form on every major social network — is powered by graph algorithms running on some of the largest graphs ever built. Facebook's social graph has over 3 billion users and hundreds of billions of edges (friendships).

The simplest friend recommendation: "find people who share many mutual friends with you." This is a 2-hop BFS problem. Start from your node, do BFS up to depth 2, count how many times each node appears — that count is your mutual friend count with that person.

But social networks do much more. They compute your "social clusters" — communities of users who are densely connected among themselves. Graph partitioning algorithms find these communities. Content you see is influenced by what your cluster engages with.

Viral content propagation is also a graph problem: a post spreads through a graph like an epidemic — the rate depends on the "connectivity" of the infected nodes. Network centrality measures (betweenness, eigenvector, degree) identify influencers: users who, when they share something, can make it reach millions.`,
      keyPoints: [
        {
          title: 'Mutual Friends via 2-Hop BFS',
          desc: 'BFS from your node to depth 2 collects all friends-of-friends. Count how many times each non-friend appears — that\'s your mutual friend count. Sort by count → top recommendations.',
          code: `from collections import defaultdict, deque

def mutual_friend_count(graph, user):
    direct_friends = set(graph[user])
    mutual_count = defaultdict(int)

    for friend in direct_friends:
        for fof in graph[friend]:          # friend of friend
            if fof != user and fof not in direct_friends:
                mutual_count[fof] += 1

    # Sort by most mutual friends
    return sorted(mutual_count, key=mutual_count.get, reverse=True)`,
        },
        {
          title: 'Six Degrees of Separation',
          desc: 'BFS from any user on Facebook reaches any other user in at most 3.5 hops on average (not 6 — the real number is smaller because Facebook\'s graph is so dense). This is the small-world property.',
        },
        {
          title: 'Community Detection',
          desc: 'Algorithms like Louvain method find clusters of highly-connected users (e.g., "your college friends" or "your coworkers"). Content and ads are targeted at these clusters.',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Build the Friendship Graph', desc: 'Each user is a node. Each friendship is an undirected edge. On Facebook, this graph has 3B+ nodes and hundreds of billions of edges, stored in distributed systems.' },
      { n: '2', label: 'BFS to Depth 2', desc: 'For user U, run BFS. Level 1 = direct friends. Level 2 = friends of friends. Record all depth-2 nodes not already direct friends.' },
      { n: '3', label: 'Count Mutual Friends', desc: 'For each depth-2 node V, count how many of your direct friends also directly connect to V. This is the mutual friend count.' },
      { n: '4', label: 'Apply Additional Signals', desc: 'Mutual friends is just the start. Add: same school, same employer, same city, recent message exchanges, photo co-appearances — each adds signal to the recommendation score.' },
      { n: '5', label: 'Rank and Display', desc: 'Sort candidates by composite score. Show top ~10 recommendations in the "People You May Know" widget. Refresh periodically as the graph changes.' },
    ],
    codeExamples: [
      {
        label: 'Friend recommendation via graph BFS',
        complexity: 'O(k²) where k = average friends per user',
        variant: 'default',
        code: `from collections import defaultdict

def recommend_friends(graph, user, top_n=10):
    """Recommend friends-of-friends by mutual friend count."""
    my_friends = set(graph.get(user, []))

    # Count mutual friends for each candidate
    candidate_score = defaultdict(int)
    for friend in my_friends:
        for fof in graph.get(friend, []):
            if fof != user and fof not in my_friends:
                candidate_score[fof] += 1

    # Sort by mutual friend count (highest first)
    ranked = sorted(candidate_score.items(),
                    key=lambda x: x[1], reverse=True)
    return [(person, count) for person, count in ranked[:top_n]]

# Example:
graph = {
    'Alice': ['Bob', 'Carol', 'Dave'],
    'Bob': ['Alice', 'Eve', 'Frank'],
    'Carol': ['Alice', 'Eve'],
    'Dave': ['Alice', 'Frank'],
    'Eve': ['Bob', 'Carol'],
    'Frank': ['Bob', 'Dave'],
}
print(recommend_friends(graph, 'Alice'))
# → [('Eve', 2), ('Frank', 2)]  # Eve and Frank each share 2 mutual friends`,
      },
    ],
    complexity: {
      rows: [
        { case: '2-Hop BFS per user', value: 'O(k²)', color: 'text-amber-400', note: 'k = avg degree (~200 on Facebook)' },
        { case: 'Full graph BFS', value: 'O(V + E)', color: 'text-amber-400', note: 'V=3B users, E=hundreds of billions' },
        { case: 'Space (graph storage)', value: 'O(V + E)', color: 'text-red-400', note: 'Requires distributed storage at Facebook\'s scale' },
      ],
      note: 'Facebook stores its social graph in a distributed system called TAO. They pre-compute recommendations offline and cache results, making the "People You May Know" feature feel instant.',
    },
    realWorld: [
      { title: 'Facebook "People You May Know"', desc: 'Uses mutual friends + common workplaces/schools + contact list matches. Powered by graph algorithms running on a 3B-node graph.' },
      { title: 'LinkedIn "2nd Connections"', desc: 'Shows users exactly 2 hops away in the professional graph. The "2nd" / "3rd" connection indicators are BFS depth labels.' },
    ],
    commonMistakes: [
      { wrong: 'Thinking social networks just track followers/friends', explain: 'Social networks build full graph indices and run graph algorithms at massive scale. The friend list is just the raw data; the BFS, centrality, and community detection are the intelligence layer.' },
      { wrong: 'Ignoring the cold-start problem', explain: 'New users with few friends have limited 2-hop neighborhoods. Social networks use phone contacts, email imports, and demographic data to seed initial recommendations.' },
    ],
    quiz: [
      { q: 'In a social network graph, what do nodes and edges represent?', options: ['Nodes = posts, edges = likes', 'Nodes = users, edges = friendships', 'Nodes = interests, edges = users who share them', 'Nodes = messages, edges = replies'], correct: 1, explanation: 'In a friendship graph, each user is a node and each friendship (or follow) is an edge connecting two user nodes.' },
      { q: 'What algorithm finds "people who share mutual friends with you"?', options: ['Dijkstra\'s shortest path', '2-hop BFS and counting repeated nodes', 'Merge sort on friend lists', 'Topological sort'], correct: 1, explanation: 'BFS to depth 2 from your node discovers all friends-of-friends. Nodes that appear multiple times at depth 2 are people who share multiple mutual friends with you.' },
      { q: 'What is "Six Degrees of Separation" in graph terms?', options: ['Every graph has exactly 6 connected components', 'Any two users in a social network are within 6 BFS hops of each other', 'Users have at most 6 direct friends', 'Social networks partition into exactly 6 communities'], correct: 1, explanation: 'The small-world property: in most large social graphs, the average shortest path between any two nodes is surprisingly small (3-6 hops), due to a few highly-connected "hub" users.' },
      { q: 'Why does Facebook pre-compute "People You May Know" offline instead of computing it live?', options: ['To protect user privacy', 'Because the 2-hop BFS on 3B users is too slow for real-time computation', 'Because the graph doesn\'t change often enough', 'To save bandwidth'], correct: 1, explanation: 'Running BFS across a 3-billion-node graph in real time for every page load would be impossibly slow. Recommendations are computed in batch, cached, and refreshed periodically.' },
      { q: 'What is "betweenness centrality" and why do social networks care about it?', options: ['The total number of friends a user has', 'How often a user lies on the shortest path between other users — identifies key bridges', 'The average age of a user\'s friends', 'The number of groups a user belongs to'], correct: 1, explanation: 'High betweenness centrality nodes are "bridges" between communities. Targeting these users with viral content causes it to spread across communities rapidly — making them key influencers.' },
      { q: 'What does "community detection" find in a social graph?', options: ['Bots and fake accounts', 'Dense clusters of mutually connected users (e.g., college friend groups)', 'The geographically closest users', 'Users who post the most content'], correct: 1, explanation: 'Community detection algorithms (like Louvain or Girvan-Newman) partition the graph into densely connected subgraphs — naturally corresponding to real-world social groups like classmates or coworkers.' },
    ],
  },

  'how-autocomplete-works': {
    concept: {
      overview: `You type "alg" into Google and instantly see "algorithm", "algebra", "algorithms and data structures". In under 50 milliseconds. For millions of simultaneous users. How?

The data structure is called a Trie (pronounced "try" — from "retrieval"). A Trie is a tree where each path from root to leaf represents one word or phrase. The key property: all words sharing a prefix share a path. So searching for completions of "alg" means: traverse from root → 'a' → 'l' → 'g', then collect every word reachable from that node.

This makes prefix lookup O(m) where m is the prefix length — completely independent of how many words are stored. A Trie with 10 million words looks up "alg" in exactly 3 steps, same as a Trie with 10 words.

Google's autocomplete adds ranking: each Trie node also stores a popularity score. After finding all completions, they're ranked by search frequency. The prefix "the" might have billions of possible completions — but showing the top 10 most searched is all you need.`,
      keyPoints: [
        {
          title: 'Trie Structure',
          desc: 'Each node represents one character. Children are the possible next characters. A word ending at a node is marked with a flag. Paths from root to marked nodes spell out complete words.',
          code: `class TrieNode:
    def __init__(self):
        self.children = {}      # char → TrieNode
        self.is_end = False
        self.frequency = 0      # for ranking completions

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, freq: int = 1):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.frequency = freq`,
        },
        {
          title: 'Prefix Search = Subtree Collection',
          desc: 'Walk the Trie following the prefix characters. If you fall off (a character not found), there are zero completions. Otherwise, collect all words in the subtree rooted at the last matched node.',
          code: `def autocomplete(trie, prefix, top_n=5):
    node = trie.root
    for char in prefix:
        if char not in node.children:
            return []           # No completions
        node = node.children[char]

    # Collect all words in this subtree
    results = []
    def dfs(node, current):
        if node.is_end:
            results.append((current, node.frequency))
        for char, child in node.children.items():
            dfs(child, current + char)

    dfs(node, prefix)
    return sorted(results, key=lambda x: -x[1])[:top_n]`,
        },
        {
          title: 'Ranked Completions',
          desc: 'Pure alphabetical completions are useless. Each terminal node stores a search frequency count. After DFS collects all completions, sort by frequency descending and return top 10.',
        },
      ],
    },
    steps: [
      { n: '1', label: 'Build the Trie', desc: 'Insert every word/phrase into the Trie. For Google, this is trillions of historical search queries aggregated and pruned to the most meaningful completions.' },
      { n: '2', label: 'User Types a Character', desc: 'Each keystroke narrows the prefix. The Trie only needs to walk one additional edge per character typed — the state is preserved from the previous keystroke.' },
      { n: '3', label: 'Traverse to Prefix Node', desc: 'Walk from root, following one edge per character in the prefix. If any character is missing, return empty (no completions exist).' },
      { n: '4', label: 'DFS Subtree Collection', desc: 'From the prefix node, run DFS to collect all words in the subtree. Each leaf-to-root path spells one completion.' },
      { n: '5', label: 'Rank by Frequency and Return', desc: 'Sort collected completions by search frequency. Apply personalisation signals (your past searches). Return top 5-10 in the dropdown.' },
    ],
    codeExamples: [
      {
        label: 'Trie autocomplete with frequency ranking',
        complexity: 'O(m + k) — m=prefix length, k=completions count',
        variant: 'default',
        code: `class AutocompleteSystem:
    def __init__(self):
        self.root = {}          # Nested dicts for simplicity

    def insert(self, word: str, freq: int):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node['_end'] = freq     # store frequency at terminal

    def search(self, prefix: str, top: int = 5):
        node = self.root
        for ch in prefix:
            if ch not in node:
                return []
            node = node[ch]

        # DFS to collect all completions
        results = []
        def dfs(n, word):
            if '_end' in n:
                results.append((word, n['_end']))
            for ch, child in n.items():
                if ch != '_end':
                    dfs(child, word + ch)
        dfs(node, prefix)

        results.sort(key=lambda x: -x[1])
        return [word for word, _ in results[:top]]

# Usage
ac = AutocompleteSystem()
for word, freq in [("algorithm", 5000), ("algebra", 3000),
                   ("algorithms and data structures", 2000), ("algo", 1000)]:
    ac.insert(word, freq)

print(ac.search("alg"))
# → ['algorithm', 'algebra', 'algorithms and data structures', 'algo']`,
      },
    ],
    complexity: {
      rows: [
        { case: 'Insert word', value: 'O(m)', color: 'text-emerald-400', note: 'm = word length' },
        { case: 'Prefix lookup', value: 'O(m)', color: 'text-emerald-400', note: 'Independent of dictionary size!' },
        { case: 'Collect completions', value: 'O(k)', color: 'text-emerald-400', note: 'k = number of completions' },
        { case: 'Space', value: 'O(ALPHABET × N × m)', color: 'text-amber-400', note: 'Can be large; compressed tries help' },
      ],
      note: 'The magic of a Trie: lookup time is O(m) — the length of the prefix — regardless of whether you store 1,000 or 1,000,000,000 words.',
    },
    realWorld: [
      { title: 'Google Search Autocomplete', desc: 'Powered by a distributed Trie with trillions of past queries. Each node stores popularity scores by geography, time, and personalization.' },
      { title: 'VS Code / IDE IntelliSense', desc: 'Code completion is a Trie lookup over all identifiers in scope. When you type "arr.p", the Trie finds "push", "pop", "push", "padStart" in under a millisecond.' },
    ],
    commonMistakes: [
      { wrong: 'Using binary search on a sorted word list for autocomplete', explain: 'Binary search finds the prefix\'s position in O(log n) but collecting all completions then requires scanning forward — O(k). A Trie\'s O(m) lookup and O(k) collection is faster and more natural.' },
      { wrong: 'Storing full words at every node', explain: 'A Trie shares prefixes between words — "cat", "catch", and "category" share the path "cat". Storing full words at each node wastes memory and misses the point of the structure.' },
    ],
    quiz: [
      { q: 'What is the key property that makes a Trie perfect for autocomplete?', options: ['It stores words in sorted order', 'All words sharing a prefix share a path, making prefix lookup O(prefix length)', 'It uses less memory than a hash table', 'It supports in-order traversal'], correct: 1, explanation: 'In a Trie, the prefix path is shared by all words starting with that prefix. Finding completions means traversing one edge per character then collecting the entire subtree.' },
      { q: 'How fast is a Trie prefix lookup compared to a hash table lookup?', options: ['Slower — O(n) vs O(1)', 'The same — both O(1)', 'Depends on the prefix length — O(m) where m is prefix length', 'Faster — O(log n) vs O(1)'], correct: 2, explanation: 'Trie lookup is O(m) where m is the prefix length, completely independent of how many words are stored. A hash table gives O(m) per exact match but can\'t enumerate all prefix completions efficiently.' },
      { q: 'How does a Trie represent the end of a word like "cat" that is also a prefix of "catch"?', options: ['It stores a duplicate node for "cat"', 'The node for the last character (\'t\') has an is_end flag set to True', 'A special separator character is inserted', '"cat" and "catch" are stored in separate branches'], correct: 1, explanation: 'Each node can have an is_end flag (and a frequency/count). The \'t\' in "cat" has is_end=True, while the path continues through \'c\'→\'h\' for "catch".' },
      { q: 'What does the DFS after finding the prefix node accomplish?', options: ['It verifies the prefix exists', 'It collects all complete words reachable in the subtree rooted at that node', 'It deletes outdated entries', 'It balances the Trie structure'], correct: 1, explanation: 'After navigating to the prefix node, DFS explores the entire subtree below it, collecting every path that leads to an is_end node — each is one possible completion.' },
      { q: 'Why does Google show only the top 10 completions even though millions may exist?', options: ['The Trie only stores 10 completions per prefix', 'Showing too many would cause privacy violations', 'They rank by search frequency and show only the most popular ones', 'Technical limitations prevent showing more'], correct: 2, explanation: 'After collecting all completions, they\'re ranked by search frequency (how many people searched that exact term). Only the top 10 most popular completions are shown, since those are most likely what you want.' },
      { q: 'What happens in a Trie when you type a character that doesn\'t exist as a child of the current node?', options: ['It backtracks to the root', 'It returns zero completions immediately — no words have this prefix', 'It searches adjacent branches', 'It suggests the closest matching character'], correct: 1, explanation: 'If a character doesn\'t exist as a child, no words in the Trie have this prefix. The autocomplete immediately returns an empty list without exploring further.' },
    ],
  },
};
