import itertools
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx


def _min_edge_weight(G, u, v, weight='weight'):
    """回傳節點 u, v 之間最小權重的邊權值（支援 Graph 與 MultiGraph）。"""
    if isinstance(G, nx.MultiGraph):
        return min(attrs[weight] for attrs in G[u][v].values())
    return G[u][v][weight]


def solve_open_cpp(G: nx.Graph, source, target, weight='weight'):
    """
    求解指定起點 source 與終點 target 的 Open Chinese Postman Problem。
    
    參數:
        G: 原圖 (需為連通的無向圖 nx.Graph 或 nx.MultiGraph，每條邊需包含權重屬性)
           若為 MultiGraph，同一對節點可有多條平行邊。
        source: 起點節點
        target: 終點節點
        weight: 權重屬性名稱 (預設為 'weight')
    
    回傳:
        path_edges:   依行走順序排列的邊列表 [(u, v, key), ...]
                      key 為 MultiGraph 中的邊索引
        total_cost:   走法總成本
        added_edges:  重複/補充添加的邊列表 [(u, v, key), ...]
        augmented_G:  增強後的 MultiGraph（含新增邊）
    """
    if not nx.is_connected(G):
        raise ValueError("圖必須是連通圖！")

    # 1. 找出原圖的所有奇數度數節點
    odd_nodes = {node for node, degree in G.degree() if degree % 2 == 1}

    # 2. 計算需要調整奇偶性的節點集合 T = O ⊕ {source, target}
    target_endpoints = {source, target}
    T = odd_nodes.symmetric_difference(target_endpoints)

    # 3. 建立多重圖 MultiGraph（準備容納重複邊）
    augmented_G = nx.MultiGraph(G)
    added_edges = []

    # 4. 如果 T 非空，進行最小權重完美匹配 (MWPM)
    if T:
        # 計算 T 中所有點對的最短路徑與長度
        shortest_paths = dict(nx.all_pairs_dijkstra_path(G, weight=weight))
        shortest_lengths = dict(nx.all_pairs_dijkstra_path_length(G, weight=weight))

        # 建立完全輔助圖以進行匹配
        complete_G = nx.Graph()
        for u, v in itertools.combinations(T, 2):
            complete_G.add_edge(u, v, weight=shortest_lengths[u][v])

        # 計算最小權重完美匹配
        matching = nx.algorithms.matching.min_weight_matching(
            complete_G, 
            weight='weight'
        )

        # 5. 將匹配路徑中的邊重複加進 augmented_G
        for u, v in matching:
            path = shortest_paths[u][v]
            for i in range(len(path) - 1):
                p_u, p_v = path[i], path[i + 1]
                edge_weight = _min_edge_weight(G, p_u, p_v, weight)
                key = augmented_G.add_edge(p_u, p_v, **{weight: edge_weight})
                added_edges.append((p_u, p_v, key))

    # 6. 使用 Hierholzer 演算法獲取從 source 到 target 的歐拉路徑
    # nx.eulerian_path 回傳生成器；keys=True 時為 [(u, v, k), ...]
    path_edges = list(nx.eulerian_path(augmented_G, source=source, keys=True))
    
    # 計算總成本
    total_cost = sum(augmented_G[u][v][k][weight] for u, v, k in augmented_G.edges(keys=True))

    return path_edges, total_cost, added_edges, augmented_G


def gshow(G, source, target, weight='weight', title='Open CPP'):
    """
    Draw a single graph with weighted edges in a matplotlib window.
    Supports both Graph and MultiGraph (parallel edges shown as curved arcs).

    Args:
        G:       Graph or MultiGraph to draw
        source:  Source node (highlighted green)
        target:  Target node (highlighted red)
        weight:  Edge weight attribute name
        title:   Window / figure title
    """
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_title(title, fontsize=13)

    pos = nx.spring_layout(G, seed=42)

    # Ensure we iterate with keys even for plain Graph
    mg = G if isinstance(G, nx.MultiGraph) else nx.MultiGraph(G)

    # --- Nodes ---
    node_colors = []
    for n in mg.nodes():
        if n == source:
            node_colors.append("#FF0000")   # source
        elif n == target:
            node_colors.append("#0000FF")   # end
        else:
            node_colors.append("#000000")   # black
    nx.draw_networkx_nodes(mg, pos, ax=ax, node_color=node_colors,
                           node_size=600, edgecolors='black', linewidths=1.2)
    nx.draw_networkx_labels(mg, pos, ax=ax, font_size=12, font_weight='bold')

    # --- Group parallel edges by node pair ---
    pair_edges = defaultdict(list)
    for u, v, k, d in mg.edges(keys=True, data=True):
        canonical = (min(u, v), max(u, v))
        pair_edges[canonical].append((u, v, k, d))

    # --- Draw edges with curvature for parallel edges ---
    for (_nu, _nv), group in pair_edges.items():
        n = len(group)
        for idx, (u, v, k, d) in enumerate(group):
            rad = 0.0 if n == 1 else 0.2 * (idx - (n - 1) / 2)

            nx.draw_networkx_edges(
                mg, pos, ax=ax,
                edgelist=[(u, v)],
                width=1.5,
                edge_color="#000000",
                connectionstyle=f'arc3,rad={rad}',
                arrows=True,
                arrowstyle='-',
            )

            # Edge weight label offset along the normal of the edge
            w = d.get(weight, '')
            mid_x = (pos[u][0] + pos[v][0]) / 2
            mid_y = (pos[u][1] + pos[v][1]) / 2
            dx = pos[v][0] - pos[u][0]
            dy = pos[v][1] - pos[u][1]
            length = (dx**2 + dy**2) ** 0.5 or 1
            offset = rad * 0.5
            label_x = mid_x + (-dy / length) * offset
            label_y = mid_y + (dx / length) * offset
            ax.text(label_x, label_y, str(w),
                    fontsize=9, ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.2', fc='white',
                              ec='gray', alpha=0.8))

    # --- Legend ---
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#4CAF50',
               markersize=10, label=f'Source ({source})'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#F44336',
               markersize=10, label=f'Target ({target})'),
    ]
    ax.legend(handles=legend_elements, loc='best', fontsize=10, frameon=True)
    ax.axis('off')
    plt.tight_layout()
    plt.show()


# ================= Test Examples =================
if __name__ == "__main__":
    # --- Example 1: Simple Graph ---
    print("=== Example 1: Simple Graph ===")
    # A          B
    #    \   /(1)|
    #      X     | (67)
    #    /   \(1)|
    # C          D
    G = nx.Graph()
    G.add_edge('A', 'D', weight=1)
    G.add_edge('C', 'B', weight=1)
    G.add_edge('B', 'D', weight=67)

    start_node = 'B'
    end_node = 'A'

    edges, cost, added_edges, aug_G = solve_open_cpp(G, source=start_node, target=end_node)

    print(f"Total cost: {cost}")
    print(f"Added edges: {added_edges}")
    visit_sequence = [edges[0][0]] + [v for _, v, _k in edges]
    print("Walk order:", " -> ".join(visit_sequence))

    gshow(G, source=start_node, target=end_node, title='Example 1: Input Graph')
    gshow(aug_G, source=start_node, target=end_node, title='Example 1: Augmented Graph')

    # --- Example 2: MultiGraph ---
    print("\n=== Example 2: MultiGraph ===")
    # A --(2)-- B
    # A --(5)-- B   (parallel edge)
    # B --(3)-- C
    # A --(4)-- C
    MG = nx.MultiGraph()
    MG.add_edge('A', 'B', weight=2)
    MG.add_edge('A', 'B', weight=5)  # parallel edge
    MG.add_edge('B', 'C', weight=3)
    MG.add_edge('A', 'C', weight=4)

    start_node = 'A'
    end_node = 'C'

    edges, cost, added_edges, aug_G = solve_open_cpp(MG, source=start_node, target=end_node)

    print(f"Total cost: {cost}")
    print(f"Added edges: {added_edges}")
    visit_sequence = [edges[0][0]] + [v for _, v, _k in edges]
    print("Walk order:", " -> ".join(visit_sequence))

    gshow(MG, source=start_node, target=end_node, title='Example 2: Input MultiGraph')
    gshow(aug_G, source=start_node, target=end_node, title='Example 2: Augmented MultiGraph')