def calculate_quality_score(dup_info, null_info, mixed_types_count, num_cols):
    """Calculates a rough data quality score from 0 to 100."""
    score = 100
    
    # Penalize for duplicates (up to 20 points)
    dup_penalty = min(20, dup_info['duplicate_percentage'] * 2)
    score -= dup_penalty
    
    # Penalize for nulls (up to 40 points)
    null_penalty = min(40, null_info['null_percentage'] * 3)
    score -= null_penalty
    
    # Penalize for mixed types (up to 40 points)
    if num_cols > 0:
        type_penalty = min(40, (mixed_types_count / num_cols) * 100)
        score -= type_penalty
        
    return max(0, round(score, 1))
