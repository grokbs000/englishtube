#!/usr/bin/env python3
"""
Dynamic Time Warping (DTW) Sequence Alignment for Karaoke Vocals & Subtitles
Aligns transcribed vocal timing frames with canonical target lyrics.
"""

import math
from difflib import SequenceMatcher

def clean_token(text: str) -> str:
    return "".join(c.lower() for c in text if c.isalnum())

def token_distance(t1: str, t2: str) -> float:
    c1, c2 = clean_token(t1), clean_token(t2)
    if not c1 and not c2:
        return 0.0
    if not c1 or not c2:
        return 1.0
    ratio = SequenceMatcher(None, c1, c2).ratio()
    return 1.0 - ratio

def dtw_alignment(reference_sequence, target_sequence, dist_fn=token_distance):
    """
    Computes optimal monotonic alignment path between reference and target sequences.
    Returns:
        cost: float
        path: List of (ref_idx, tgt_idx) pairs
    """
    n, m = len(reference_sequence), len(target_sequence)
    if n == 0 or m == 0:
        return 0.0, []

    # DP Matrix initialization
    dp = [[math.inf] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = dist_fn(reference_sequence[i - 1], target_sequence[j - 1])
            dp[i][j] = cost + min(
                dp[i - 1][j],       # insertion
                dp[i][j - 1],       # deletion
                dp[i - 1][j - 1]    # match/substitution
            )

    # Backtracking path
    i, j = n, m
    path = []
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        scores = [
            (dp[i - 1][j - 1], i - 1, j - 1),
            (dp[i - 1][j], i - 1, j),
            (dp[i][j - 1], i, j - 1),
        ]
        _, i, j = min(scores, key=lambda x: x[0])

    path.reverse()
    return dp[n][m], path

def align_vocal_cues(vocal_words, target_cues):
    """
    Aligns raw Whisper word segments to target lyric cues using DTW.
    """
    ref_tokens = [w['word'] for w in vocal_words]
    
    aligned_cues = []
    w_idx = 0
    for cue in target_cues:
        cue_tokens = cue['en'].split()
        if not cue_tokens:
            aligned_cues.append(cue)
            continue
            
        win = vocal_words[max(0, w_idx - 5) : min(len(vocal_words), w_idx + 40)]
        if not win:
            aligned_cues.append(cue)
            continue
            
        win_tokens = [w['word'] for w in win]
        _, path = dtw_alignment(cue_tokens, win_tokens)
        
        if path:
            matched_win_indices = [p[1] for p in path]
            first_idx = min(matched_win_indices)
            last_idx = max(matched_win_indices)
            
            start_t = win[first_idx]['start']
            end_t = win[last_idx]['end']
            w_idx = max(0, w_idx - 5) + last_idx + 1
            
            aligned_cues.append({
                'start': round(start_t, 2),
                'duration': round(max(1.2, end_t - start_t), 2),
                'en': cue['en'],
                'zh': cue.get('zh', ''),
                'text': cue['en']
            })
        else:
            aligned_cues.append(cue)
            
    return aligned_cues

if __name__ == '__main__':
    ref = ["hello", "world", "this", "is", "a", "test"]
    tgt = ["hello", "word", "this", "is", "test"]
    cost, path = dtw_alignment(ref, tgt)
    print(f"Alignment Cost: {cost:.4f}")
    print(f"Optimal Path: {path}")
