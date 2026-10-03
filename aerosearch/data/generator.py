"""Demo dataset generator generating 5,000+ realistic engineering, aerospace, and science documents."""

import random
from typing import Any

from aerosearch.core.models import Document

TOPICS: list[dict[str, Any]] = [
    {
        "category": "Systems Engineering",
        "tag": "distributed-systems",
        "templates": [
            (
                "Distributed Consensus with {proto}: Scalability and Fault Tolerance",
                "The {proto} consensus protocol provides state machine replication across unreliable networks. "
                "By decoupling leader election from log replication, systems achieve high throughput under Byzantine "
                "faults and network partitions. Quorum slices and lease mechanisms prevent split-brain anomalies in distributed databases.",
            ),
            (
                "High-Throughput In-Memory Storage Using {tech}",
                "Modern low-latency architectures leverage {tech} to eliminate disk I/O bottlenecks. "
                "Zero-copy serialization, lock-free ring buffers, and SIMD-accelerated filtering deliver sub-microsecond query resolution. "
                "Memory compaction and cache-line aligned hash tables maximize CPU cache locality under concurrent workloads.",
            ),
            (
                "Lock-Free Concurrency and Memory Reclamation with {tech}",
                "Designing lock-free data structures requires careful hazard pointer management and epoch-based reclamation. "
                "Using atomic compare-and-swap operations prevents thread starvation and priority inversion while scaling across NUMA sockets. "
                "Benchmarking proves linear scalability compared to traditional mutex locking schemes under high contention.",
            ),
        ],
        "variables": {
            "proto": [
                "Raft",
                "Paxos",
                "Multi-Paxos",
                "Zab",
                "Viewstamped Replication",
                "PBFT",
                "HotStuff",
            ],
            "tech": [
                "Inverted Indices",
                "Prefix Trees",
                "B-Tree Indices",
                "LSM-Trees",
                "Skip Lists",
                "Ring Buffers",
                "Memory-Mapped Files",
            ],
        },
    },
    {
        "category": "Aerospace & Aeronautics",
        "tag": "aerospace",
        "templates": [
            (
                "Aerodynamics of {vehicle}: Boundary Layer Transition at {regime}",
                "Investigating shockwave boundary layer interactions on {vehicle} during atmospheric flight. "
                "Computational fluid dynamics (CFD) reveals laminar separation bubbles and turbulent transition regimes at {regime}. "
                "Aeroacoustic dissipation and thermal barrier coatings ensure structural integrity at extreme dynamic pressures.",
            ),
            (
                "Next-Generation Propulsion Systems: {propulsion} for Deep Space Trajectories",
                "Advanced {propulsion} offers specific impulse exceeding 4,000 seconds, revolutionizing interplanetary transit. "
                "Utilizing magnetic confinement and electrostatic acceleration, ion thrusters deliver continuous low-thrust orbital transfers. "
                "Mission simulations for Mars and Europa demonstrate 40% fuel mass reduction compared to bipropellant chemical engines.",
            ),
            (
                "Autonomous Flight Navigation and Guidance with {nav}",
                "Precision guidance navigation and control (GNC) algorithms for {vehicle} employ extended Kalman filters and optical flow. "
                "Real-time sensor fusion with {nav} enables terrain relative navigation during planetary entry, descent, and landing phases. "
                "Decentralized swarming logic guarantees obstacle avoidance in GPS-denied environments.",
            ),
        ],
        "variables": {
            "vehicle": [
                "Hypersonic Glider X-43",
                "Reusable Orbital Booster",
                "Stratospheric Drone",
                "Supersonic Airliner",
                "Lunar Lander Nova",
            ],
            "regime": [
                "Mach 5.8",
                "Transonic Speeds",
                "Hypersonic Boundary",
                "Stratospheric Cruising Altitude",
                "Dynamic Max-Q",
            ],
            "propulsion": [
                "Hall Effect Thrusters",
                "Magnetoplasmadynamic Drives",
                "Nuclear Thermal Rockets",
                "Dual-Stage Ion Engines",
            ],
            "nav": [
                "Star Trackers and IMU Fusion",
                "LiDAR Odometry",
                "Optical Terrain Navigation",
                "Kalman State Estimators",
            ],
        },
    },
    {
        "category": "Artificial Intelligence & Algorithms",
        "tag": "ai-algorithms",
        "templates": [
            (
                "Algorithmic Foundations of {algo}: Complexity Analysis and Benchmarks",
                "The {algo} algorithm achieves optimal asymptotic complexity for full-text retrieval and nearest neighbor queries. "
                "Through hierarchical partitioning and inverted posting traversal, lookup latency scales logarithmically with corpus size. "
                "Comparative empirical evaluations confirm significant throughput gains over linear scan baselines.",
            ),
            (
                "Neural Language Models and {algo} in High-Dimension Spaces",
                "Combining dense semantic embeddings with sparse {algo} produces state-of-the-art hybrid search architectures. "
                "Reciprocal rank fusion harmonizes lexical precision with semantic generalization. "
                "Quantization techniques compress float vectors to 8-bit integers without degrading retrieval recall.",
            ),
        ],
        "variables": {
            "algo": [
                "Okapi BM25",
                "Trie Prefix Search",
                "Hierarchical Navigable Small World",
                "Levenshtein Automata",
                "TF-IDF Weighting",
                "Aho-Corasick Automaton",
            ],
        },
    },
    {
        "category": "Science Fiction & Space Exploration",
        "tag": "scifi-space",
        "templates": [
            (
                "Exploration Log: Mission to {destination} and Anomalous Signal Analysis",
                "Deep space probe Voyager Sentinel telemetry from {destination} detected rhythmic gravitational variations. "
                "Spectroscopic analysis confirmed trace atmospheric argon and subterranean silicate structures. "
                "Automated rover units deployed seismic sensors to map crustal tectonic stability before crew rendezvous.",
            ),
            (
                "Relativistic Kinematics and Wormhole Topology near {destination}",
                "Einstein-Rosen bridges require negative energy densities to sustain traversable throat geometries. "
                "Observing frame dragging effects in the vicinity of {destination} validates predictions of general relativity. "
                "Hawking radiation sensors registered thermal micro-signatures consistent with quantum event horizon thermodynamics.",
            ),
        ],
        "variables": {
            "destination": [
                "Proxima Centauri b",
                "Titan Kraken Mare",
                "Enceladus Geysers",
                "Kepler-186f",
                "Oumuamua Trajectory",
                "Betelgeuse Nebula",
            ],
        },
    },
]

AUTHORS = [
    "Dr. Elena Vance",
    "Marcus Reynolds",
    "Siddharth Nair",
    "Anya Petrova",
    "Dr. Arthur Vance",
    "Sarah Connor",
    "Kenji Sato",
    "Claire Delacroix",
    "David Bowman",
    "Dr. H. Brand",
    "Murph Cooper",
    "Alex Chen",
]


def generate_demo_documents(count: int = 5000, seed: int = 42) -> list[Document]:
    """Generate deterministic, high-quality full-text documents for benchmarking and demo."""
    rng = random.Random(seed)
    documents: list[Document] = []

    for i in range(count):
        topic = rng.choice(TOPICS)
        title_tmpl, content_tmpl = rng.choice(topic["templates"])
        vars_dict = {k: rng.choice(v) for k, v in topic["variables"].items()}

        title = title_tmpl.format(**vars_dict)
        content_para1 = content_tmpl.format(**vars_dict)

        # Add supplementary contextual paragraph to enrich document length & vocabulary
        second_topic = rng.choice(TOPICS)
        _, sec_content_tmpl = rng.choice(second_topic["templates"])
        sec_vars = {k: rng.choice(v) for k, v in second_topic["variables"].items()}
        content_para2 = sec_content_tmpl.format(**sec_vars)

        full_content = f"{content_para1}\n\n{content_para2}"

        tags = [topic["tag"], second_topic["tag"], topic["category"].lower().replace(" ", "-")]
        tags = list(set(tags))

        author = rng.choice(AUTHORS)
        views = rng.randint(150, 45000)
        rating = round(rng.uniform(3.5, 5.0), 1)

        documents.append(
            Document(
                id=f"aero-doc-{i + 1:05d}",
                title=title,
                content=full_content,
                tags=tags,
                metadata={
                    "author": author,
                    "category": topic["category"],
                    "views": views,
                    "rating": rating,
                    "year": rng.randint(2018, 2026),
                },
            )
        )

    return documents
