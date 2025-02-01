import numpy as np
from typing import List, Tuple
import logging

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

    @staticmethod
    def recommend_bankroll(std_dev: float, bb_per_100: float = 0, confidence_level: float = 0.95) -> tuple[int, str]:
        """
        Calculate recommended bankroll in buyins (100bb) based on standard deviation and win rate
        
        Args:
            std_dev: Standard deviation of BB/100
            bb_per_100: Win rate in BB/100
            confidence_level: Desired confidence level (default 95%)
            
        Returns:
            Tuple of (recommended_buyins, message)
            For negative win rates, returns (None, warning_message)
        """
        if bb_per_100 < 0:
            return None, "Warning: Negative win rate detected. Consider moving down in stakes or studying to improve your game."
        
        if std_dev <= 0:
            return None, "Warning: Not enough data to calculate bankroll requirement."
        
        # Z-scores for common confidence levels
        z_scores = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576
        }
        
        z_score = z_scores.get(confidence_level, 1.96)
        
        # Calculate required bankroll in big blinds
        # For a BB/100 std dev of 178.4, we want roughly 30 buyins
        # So: (178.4 * 1.96) / 100 * 16.67 ≈ 30
        required_bb = (std_dev * z_score) / 100 * 16.67
        
        # Convert BB to buyins (1 buyin = 100BB) and round up
        recommended_buyins = int(np.ceil(required_bb))
        
        # For debugging
        logger = logging.getLogger(__name__)
        logger.info(f"""
        Bankroll calculation:
        - Input std_dev (BB/100): {std_dev}
        - Input bb_per_100: {bb_per_100}
        - z_score: {z_score}
        - required_bb: {required_bb}
        - recommended_buyins: {recommended_buyins}
        """)
        
        return max(recommended_buyins, 20), ""  # Minimum 20 buyins 