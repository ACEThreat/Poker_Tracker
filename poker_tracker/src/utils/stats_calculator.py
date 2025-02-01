import numpy as np
from typing import List, Tuple

class StatsCalculator:
    @staticmethod
    def calculate_variance_stats(results_bb: List[float], n_hands: int) -> Tuple[float, float, float]:
        """
        Calculate variance statistics for poker results
        
        Args:
            results_bb: List of results in big blinds
            n_hands: Number of hands played
            
        Returns:
            Tuple of (mean_bb_per_hand, variance, std_dev)
        """
        if not results_bb or n_hands == 0:
            return 0.0, 0.0, 0.0
            
        mean = sum(results_bb) / n_hands
        
        # Calculate variance
        squared_diff_sum = sum((x - mean) ** 2 for x in results_bb)
        variance = squared_diff_sum / n_hands
        
        # Calculate standard deviation
        std_dev = np.sqrt(variance)
        
        return mean, variance, std_dev
    
    @staticmethod
    def bb_per_100(mean: float) -> float:
        """Convert mean BB per hand to BB per 100 hands"""
        return mean * 100 