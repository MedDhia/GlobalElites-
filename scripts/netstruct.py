"""Positional analysis helpers shared by the network-structure script and its figures.

Sectors that combine with the same partners occupy the same position, whether or
not they combine with each other. These functions turn an association matrix into
profile correlations, blocks, a blockmodel image, core-periphery scores and
whole-network indices.
"""

import itertools

import networkx as nx
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import squareform


def to_matrix(frame, order, a_col, b_col, value="assoc_log2"):
    mat = pd.DataFrame(np.nan, index=order, columns=order, dtype=float)
    for _, r in frame.iterrows():
        if r[a_col] in mat.index and r[b_col] in mat.columns:
            mat.loc[r[a_col], r[b_col]] = r[value]
            mat.loc[r[b_col], r[a_col]] = r[value]
    return mat


def profile_correlations(mat: pd.DataFrame) -> pd.DataFrame:
    """Correlation between the association profiles of every pair of nodes.

    The cells (i, j) and (j, i) are excluded from each comparison, so two nodes
    can be similar in position without combining with one another.
    """
    m = mat.to_numpy(dtype=float)
    k = len(mat)
    out = np.eye(k)
    for i, j in itertools.combinations(range(k), 2):
        keep = np.ones(k, dtype=bool)
        keep[[i, j]] = False
        a, b = m[i, keep], m[j, keep]
        ok = np.isfinite(a) & np.isfinite(b)
        out[i, j] = out[j, i] = (np.corrcoef(a[ok], b[ok])[0, 1] if ok.sum() > 2 else np.nan)
    return pd.DataFrame(out, index=mat.index, columns=mat.columns)


def silhouette(dist: np.ndarray, labels: np.ndarray) -> float:
    n = len(labels)
    scores = []
    for i in range(n):
        same = (labels == labels[i]) & (np.arange(n) != i)
        if not same.any():
            continue
        a = dist[i, same].mean()
        others = [dist[i, labels == g].mean() for g in np.unique(labels) if g != labels[i]]
        if not others:
            continue
        scores.append((min(others) - a) / max(a, min(others)))
    return float(np.mean(scores)) if scores else np.nan


def choose_k(dist: np.ndarray, link, kmax: int = 6):
    rows = []
    for k in range(2, kmax + 1):
        labels = fcluster(link, k, criterion="maxclust")
        rows.append({"k": k, "silhouette": silhouette(dist, labels)})
    return pd.DataFrame(rows)


def blocks_from(corr: pd.DataFrame, k: int, order, reference: pd.Series | None = None):
    """Average-linkage blocks over the profile-distance matrix.

    Without a reference, each block is named after the member that comes first in
    the canonical order. With one, blocks are matched to the reference partition
    by best overlap and inherit its names, so membership can be read across
    periods without the labels drifting.
    """
    dist = 1.0 - corr.to_numpy(dtype=float)
    dist = np.nan_to_num(dist, nan=1.0)
    np.fill_diagonal(dist, 0.0)
    dist = (dist + dist.T) / 2
    link = linkage(squareform(dist, checks=False), method="average")
    labels = fcluster(link, k, criterion="maxclust")
    groups = {g: [order[i] for i in range(len(order)) if labels[i] == g]
              for g in np.unique(labels)}

    if reference is None:
        names = {g: f"{members[0]} block" for g, members in groups.items()}
    else:
        ref_names = sorted(reference.unique())
        ref_sets = {name: set(reference[reference == name].index) for name in ref_names}
        gs = sorted(groups)
        overlap = np.zeros((len(gs), len(ref_names)))
        for a, g in enumerate(gs):
            for b, name in enumerate(ref_names):
                members = set(groups[g])
                union = members | ref_sets[name]
                overlap[a, b] = len(members & ref_sets[name]) / len(union) if union else 0.0
        rows, cols = linear_sum_assignment(-overlap)
        names = {}
        for a, b in zip(rows, cols):
            names[gs[a]] = ref_names[b] if overlap[a, b] > 0 else f"{groups[gs[a]][0]} block"
        for g in gs:                       # more blocks than the reference has
            names.setdefault(g, f"{groups[g][0]} block")
    return pd.Series([names[g] for g in labels], index=order), link, dist


def coreness(mat: pd.DataFrame):
    """Continuous core-periphery scores: the leading eigenvector of the positive
    part of the association matrix, which is its best rank-one approximation."""
    a = np.nan_to_num(mat.to_numpy(dtype=float), nan=0.0)
    a = np.clip(a, 0, None)
    np.fill_diagonal(a, 0.0)
    if not np.any(a):
        return pd.Series(np.nan, index=mat.index), np.nan
    vals, vecs = np.linalg.eigh(a)
    c = np.abs(vecs[:, -1])
    c = c / c.max() if c.max() > 0 else c
    off = ~np.eye(len(a), dtype=bool)
    fit = float(np.corrcoef(a[off], np.outer(c, c)[off])[0, 1])
    return pd.Series(c, index=mat.index), fit


def network_indices(frame, mat: pd.DataFrame, layer, period):
    sig = frame[frame["q_value"] < 0.05]
    n_pairs = len(frame)
    pos = sig[sig["assoc_log2"] > 0]
    neg = sig[sig["assoc_log2"] < 0]

    graph = nx.Graph()
    graph.add_nodes_from(mat.index)
    a_col = "sector_a" if "sector_a" in frame.columns else "domain_a"
    b_col = "sector_b" if "sector_b" in frame.columns else "domain_b"
    for _, r in pos.iterrows():
        graph.add_edge(r[a_col], r[b_col], weight=float(r["assoc_log2"]))

    degrees = np.array([d for _, d in graph.degree()])
    n = graph.number_of_nodes()
    max_sum = (n - 1) * (n - 2) if n > 2 else np.nan
    centralization = ((degrees.max() - degrees).sum() / max_sum) if n > 2 else np.nan

    if graph.number_of_edges() > 0:
        communities = nx.community.greedy_modularity_communities(graph, weight="weight")
        modularity = nx.community.modularity(graph, communities, weight="weight")
        n_comm = len(communities)
    else:
        modularity, n_comm = np.nan, np.nan

    _, cp_fit = coreness(mat)
    vals = frame["assoc_log2"].to_numpy(dtype=float)
    return {
        "layer": layer,
        "period": period,
        "n_nodes": n,
        "n_pairs": n_pairs,
        "n_crossings": int(frame["n_diversified_period"].iloc[0]),
        "share_associated": len(pos) / n_pairs,
        "share_dissociated": len(neg) / n_pairs,
        "share_indistinguishable": (n_pairs - len(sig)) / n_pairs,
        "mean_abs_assoc": float(np.nanmean(np.abs(vals))),
        "sd_assoc": float(np.nanstd(vals, ddof=1)),
        "degree_centralization": centralization,
        "transitivity": nx.transitivity(graph),
        "modularity": modularity,
        "n_communities": n_comm,
        "core_periphery_fit": cp_fit,
    }
