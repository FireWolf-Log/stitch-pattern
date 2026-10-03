import itertools
import networkx as nx

def solve_open_cpp(G: nx.Graph, source, target, weight='weight'):
    """
    求解指定起點 source 與終點 target 的 Open Chinese Postman Problem。
    
    參數:
        G: 原圖 (需為連通的無向圖 nx.Graph，每條邊需包含權重屬性)
        source: 起點節點
        target: 終點節點
        weight: 權重屬性名稱 (預設為 'weight')
    
    回傳:
        path_edges: 依行走順序排列的邊列表 [(u, v), ...]
        total_cost: 走法總成本
        added_edges: 重複/補充添加的邊列表 [(u, v), ...]
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
        # 注意：nx.min_weight_matching 預設尋求最大權重，需透過 max_weight=False 進行最小匹配
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
                edge_weight = G[p_u][p_v][weight]
                augmented_G.add_edge(p_u, p_v, **{weight: edge_weight})
                added_edges.append((p_u, p_v))

    # 6. 使用 Hierholzer 演算法獲取從 source 到 target 的歐拉路徑
    # nx.eulerian_path 回傳生成器 [(u, v), (v, w), ...]
    path_edges = list(nx.eulerian_path(augmented_G, source=source))
    
    # 計算總成本
    total_cost = sum(augmented_G[u][v][k][weight] for u, v, k in augmented_G.edges(keys=True))

    return path_edges, total_cost, added_edges


# ================= 測試範例 =================
if __name__ == "__main__":
    # A          B
    #    \   /(1)|
    #      X     | (67)
    #    /   \(1)|
    # C          D
    G = nx.Graph()
    G.add_edge('A', 'D', weight=1)
    G.add_edge('C', 'B', weight=1)
    G.add_edge('B', 'D', weight=67)

    # 指定起點 A，終點 B
    start_node = 'B'
    end_node = 'A'

    edges, cost, added_edges = solve_open_cpp(G, source=start_node, target=end_node)

    print(f"最小總路徑成本: {cost} (weight)")
    print(f"新增重複邊 (added edges): {added_edges}")
    
    # 將邊列表轉換成直觀的節點訪問順序
    visit_sequence = [edges[0][0]] + [v for _, v in edges]
    print("具體行走節點順序:", " -> ".join(visit_sequence))