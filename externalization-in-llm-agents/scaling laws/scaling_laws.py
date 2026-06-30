"""
Scaling Laws for Neural Language Models - Implementation Library
Based on Kaplan et al., 2020 (https://arxiv.org/abs/2001.08361)

This module provides tools for:
- Predicting model performance from scaling laws
- Finding optimal model configurations
- Analyzing scaling relationships
- Comparing different allocation strategies
"""

import numpy as np
from scipy.optimize import curve_fit
import pandas as pd
from typing import Tuple, Dict, Optional


# ============================================================================
# EMPIRICAL CONSTANTS FROM KAPLAN ET AL. (2020)
# ============================================================================

KAPLAN_ALPHA = 0.07           # Model size exponent
KAPLAN_ALPHA_D = 0.095        # Data size exponent
KAPLAN_ALPHA_C = 0.077        # Compute exponent

KAPLAN_A_N = 0.34             # Model size coefficient
KAPLAN_A_D = 2.56             # Data size coefficient
KAPLAN_A_C = 0.37             # Compute coefficient

# Chinchilla optimal ratio (Hoffmann et al., 2022)
CHINCHILLA_RATIO = 20         # D_optimal ≈ 20 * N


# ============================================================================
# BASIC POWER-LAW FUNCTIONS
# ============================================================================

def loss_from_model_size(N: float,
                         a_N: float = KAPLAN_A_N,
                         alpha_N: float = KAPLAN_ALPHA) -> float:
    """
    Estimate loss from model size.

    L(N) = a_N * N^(-alpha_N)

    Args:
        N: Model size (number of parameters)
        a_N: Coefficient (default from Kaplan et al.)
        alpha_N: Exponent (default from Kaplan et al.)

    Returns:
        Predicted loss value
    """
    return a_N * (N ** (-alpha_N))


def loss_from_data_size(D: float,
                        a_D: float = KAPLAN_A_D,
                        alpha_D: float = KAPLAN_ALPHA_D) -> float:
    """
    Estimate loss from dataset size.

    L(D) = a_D * D^(-alpha_D)

    Args:
        D: Dataset size (number of tokens)
        a_D: Coefficient (default from Kaplan et al.)
        alpha_D: Exponent (default from Kaplan et al.)

    Returns:
        Predicted loss value
    """
    return a_D * (D ** (-alpha_D))


def loss_from_compute(C: float,
                      a_C: float = KAPLAN_A_C,
                      alpha_C: float = KAPLAN_ALPHA_C) -> float:
    """
    Estimate loss from compute budget.

    L(C) = a_C * C^(-alpha_C)

    Args:
        C: Compute budget (FLOPs)
        a_C: Coefficient (default from Kaplan et al.)
        alpha_C: Exponent (default from Kaplan et al.)

    Returns:
        Predicted loss value
    """
    return a_C * (C ** (-alpha_C))


def combined_loss(N: float, D: float,
                  a_N: float = KAPLAN_A_N,
                  a_D: float = KAPLAN_A_D,
                  alpha_N: float = KAPLAN_ALPHA,
                  alpha_D: float = KAPLAN_ALPHA_D) -> float:
    """
    Estimate combined loss from both model and data size.
    Assumes additive relationship.

    Args:
        N: Model size (parameters)
        D: Dataset size (tokens)

    Returns:
        Combined loss prediction
    """
    return loss_from_model_size(N, a_N, alpha_N) + \
           loss_from_data_size(D, a_D, alpha_D)


# ============================================================================
# CHINCHILLA OPTIMIZATION
# ============================================================================

def compute_optimal_allocation(C: float) -> Tuple[float, float]:
    """
    Find compute-optimal allocation for a given compute budget.

    For fixed compute C, optimal allocation satisfies:
    - C = 6 * N * D
    - D_optimal ≈ 20 * N

    Solving: N_optimal = sqrt(C / 120)
             D_optimal = 20 * N_optimal

    Args:
        C: Total compute budget (FLOPs)

    Returns:
        Tuple of (optimal_N, optimal_D)
    """
    N_optimal = np.sqrt(C / 120)
    D_optimal = CHINCHILLA_RATIO * N_optimal
    return N_optimal, D_optimal


def tokens_from_compute(C: float, N: float) -> float:
    """
    Calculate tokens needed given compute budget and model size.

    From C = 6 * N * D:
    D = C / (6 * N)

    Args:
        C: Compute budget (FLOPs)
        N: Model size (parameters)

    Returns:
        Required dataset size (tokens)
    """
    return C / (6 * N)


def compute_required(N: float, D: float) -> float:
    """
    Calculate compute required for training.

    C = 6 * N * D
    (Rough approximation; actual may vary by implementation)

    Args:
        N: Model size (parameters)
        D: Dataset size (tokens)

    Returns:
        Approximate FLOPs required
    """
    return 6 * N * D


# ============================================================================
# POWER-LAW FITTING
# ============================================================================

def fit_power_law(x_data: np.ndarray, y_data: np.ndarray,
                  initial_guess: Tuple[float, float] = (1.0, 0.07)) \
    -> Tuple[Tuple[float, float], np.ndarray]:
    """
    Fit power-law function y = a * x^(-alpha) to data.

    Args:
        x_data: Independent variable values
        y_data: Dependent variable (loss) values
        initial_guess: (a, alpha) starting values

    Returns:
        Tuple of ((a_fitted, alpha_fitted), covariance_matrix)
    """
    def power_law(x, a, alpha):
        return a * x ** (-alpha)

    popt, pcov = curve_fit(power_law, x_data, y_data,
                           p0=initial_guess, maxfev=10000)
    return popt, pcov


# ============================================================================
# SCALING LAW PREDICTOR CLASS
# ============================================================================

class ScalingLawPredictor:
    """
    High-level predictor for model performance based on scaling laws.

    Example:
        predictor = ScalingLawPredictor()
        loss = predictor.predict_loss(N=7e9, D=140e9)
        improvement = predictor.improvement_when_scaling(7e9, 13e9, 'N')
    """

    def __init__(self,
                 a_N: float = KAPLAN_A_N,
                 a_D: float = KAPLAN_A_D,
                 a_C: float = KAPLAN_A_C,
                 alpha: float = KAPLAN_ALPHA,
                 alpha_D: float = KAPLAN_ALPHA_D,
                 alpha_C: float = KAPLAN_ALPHA_C):
        """
        Initialize predictor with scaling law parameters.

        Args:
            a_N, a_D, a_C: Coefficients
            alpha, alpha_D, alpha_C: Exponents
        """
        self.a_N = a_N
        self.a_D = a_D
        self.a_C = a_C
        self.alpha = alpha
        self.alpha_D = alpha_D
        self.alpha_C = alpha_C

    def predict_loss(self, N: Optional[float] = None,
                     D: Optional[float] = None,
                     C: Optional[float] = None) -> Dict[str, float]:
        """
        Predict loss from any combination of N, D, or C.

        Args:
            N: Model size (parameters)
            D: Dataset size (tokens)
            C: Compute budget (FLOPs)

        Returns:
            Dictionary with loss predictions from each specified dimension
        """
        results = {}

        if N is not None:
            results['from_N'] = loss_from_model_size(
                N, self.a_N, self.alpha)

        if D is not None:
            results['from_D'] = loss_from_data_size(
                D, self.a_D, self.alpha_D)

        if C is not None:
            results['from_C'] = loss_from_compute(
                C, self.a_C, self.alpha_C)

        return results

    def combined_prediction(self, N: Optional[float] = None,
                           D: Optional[float] = None) -> Optional[float]:
        """
        Get combined loss prediction from N and D.

        Args:
            N: Model size (parameters)
            D: Dataset size (tokens)

        Returns:
            Combined loss (or None if not enough data)
        """
        if N is not None and D is not None:
            return combined_loss(N, D, self.a_N, self.a_D,
                               self.alpha, self.alpha_D)
        return None

    def improvement_when_scaling(self, old_size: float, new_size: float,
                                dimension: str = 'N') -> Dict[str, float]:
        """
        Estimate improvement when scaling up a dimension.

        Args:
            old_size: Original size
            new_size: New size
            dimension: 'N' for model size or 'D' for data size

        Returns:
            Dictionary with improvement metrics
        """
        if dimension == 'N':
            loss_old = loss_from_model_size(old_size, self.a_N, self.alpha)
            loss_new = loss_from_model_size(new_size, self.a_N, self.alpha)
        elif dimension == 'D':
            loss_old = loss_from_data_size(old_size, self.a_D, self.alpha_D)
            loss_new = loss_from_data_size(new_size, self.a_D, self.alpha_D)
        else:
            raise ValueError("dimension must be 'N' or 'D'")

        improvement_pct = (loss_old - loss_new) / loss_old * 100
        scale_factor = new_size / old_size

        return {
            'improvement_%': improvement_pct,
            'scale_factor': scale_factor,
            'loss_old': loss_old,
            'loss_new': loss_new,
            'absolute_improvement': loss_old - loss_new
        }

    def comparison_table(self, N_values, D_values=None) -> pd.DataFrame:
        """
        Generate comparison table for different model/data sizes.

        Args:
            N_values: List of model sizes to compare
            D_values: Optional list of data sizes (defaults to optimal)

        Returns:
            DataFrame with predictions
        """
        rows = []

        if D_values is None:
            D_values = [CHINCHILLA_RATIO * N for N in N_values]

        for N, D in zip(N_values, D_values):
            loss_N = loss_from_model_size(N, self.a_N, self.alpha)
            loss_D = loss_from_data_size(D, self.a_D, self.alpha_D)
            loss_combined = loss_N + loss_D

            rows.append({
                'Model Size (B)': f'{N/1e9:.0f}',
                'Tokens (B)': f'{D/1e9:.0f}',
                'D/N Ratio': f'{D/N:.0f}x',
                'Loss from N': f'{loss_N:.4f}',
                'Loss from D': f'{loss_D:.4f}',
                'Combined Loss': f'{loss_combined:.4f}'
            })

        return pd.DataFrame(rows)


# ============================================================================
# ANALYSIS UTILITIES
# ============================================================================

def pareto_frontier(compute_budget: float) -> pd.DataFrame:
    """
    Generate Pareto frontier of different allocation strategies
    for a given compute budget.

    Shows how loss varies with different N/D allocations while
    keeping total compute fixed.

    Args:
        compute_budget: Total compute (FLOPs)

    Returns:
        DataFrame with different allocations and their losses
    """
    N_range = np.logspace(6, 12, 50)  # 1M to 1T parameters
    rows = []

    for N in N_range:
        D = compute_required_for_compute(compute_budget, N)

        loss_N = loss_from_model_size(N)
        loss_D = loss_from_data_size(D)
        loss_total = loss_N + loss_D

        rows.append({
            'N (params)': N,
            'D (tokens)': D,
            'D/N ratio': D/N,
            'Loss from N': loss_N,
            'Loss from D': loss_D,
            'Total Loss': loss_total
        })

    return pd.DataFrame(rows)


def compute_required_for_compute(C: float, N: float) -> float:
    """Alias for tokens_from_compute for clarity in some contexts."""
    return tokens_from_compute(C, N)


# ============================================================================
# BENCHMARK COMPARISONS
# ============================================================================

REAL_MODELS = {
    'BERT': {'params': 340e6, 'tokens': 3.4e9, 'year': 2018},
    'GPT-3': {'params': 175e9, 'tokens': 300e9, 'year': 2020},
    'Chinchilla': {'params': 70e9, 'tokens': 1.4e12, 'year': 2022},
    'LLaMA-7B': {'params': 7e9, 'tokens': 1e12, 'year': 2023},
    'LLaMA-65B': {'params': 65e9, 'tokens': 1.4e12, 'year': 2023},
}


def model_comparison(models: list = None) -> pd.DataFrame:
    """
    Compare real models against scaling law predictions.

    Args:
        models: List of model names to compare (defaults to all)

    Returns:
        DataFrame with actual vs predicted metrics
    """
    if models is None:
        models = list(REAL_MODELS.keys())

    rows = []
    predictor = ScalingLawPredictor()

    for name in models:
        if name not in REAL_MODELS:
            continue

        config = REAL_MODELS[name]
        N = config['params']
        D = config['tokens']

        predictions = predictor.predict_loss(N=N, D=D)
        loss_N = predictions.get('from_N', 0)
        loss_D = predictions.get('from_D', 0)
        loss_combined = loss_N + loss_D

        rows.append({
            'Model': name,
            'Year': config['year'],
            'Params (B)': f'{N/1e9:.0f}',
            'Tokens (B)': f'{D/1e9:.0f}',
            'D/N Ratio': f'{D/N:.1f}x',
            'Predicted Loss': f'{loss_combined:.4f}'
        })

    return pd.DataFrame(rows)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    print("Scaling Laws for Neural Language Models")
    print("=" * 60)

    # Example 1: Basic prediction
    print("\n1. BASIC LOSS PREDICTION")
    print("-" * 60)
    N = 7e9  # 7B parameters
    D = 140e9  # 140B tokens
    loss_N = loss_from_model_size(N)
    loss_D = loss_from_data_size(D)
    total = loss_N + loss_D
    print(f"Model: 7B params, 140B tokens")
    print(f"  Loss from N: {loss_N:.4f}")
    print(f"  Loss from D: {loss_D:.4f}")
    print(f"  Combined:    {total:.4f}")

    # Example 2: Optimal allocation
    print("\n2. COMPUTE-OPTIMAL ALLOCATION")
    print("-" * 60)
    C = 1e17  # 10^17 FLOPs
    N_opt, D_opt = compute_optimal_allocation(C)
    print(f"Compute budget: {C:.1e} FLOPs")
    print(f"Optimal N: {N_opt/1e9:.1f}B parameters")
    print(f"Optimal D: {D_opt/1e12:.1f}T tokens")
    print(f"Ratio: D/{N_opt/1e9:.1f}B = {D_opt/N_opt:.0f}x")

    # Example 3: Scaling comparison
    print("\n3. SCALING COMPARISON")
    print("-" * 60)
    predictor = ScalingLawPredictor()
    improvement = predictor.improvement_when_scaling(7e9, 13e9, 'N')
    print(f"Scaling from 7B to 13B parameters:")
    print(f"  Improvement: {improvement['improvement_%']:.2f}%")
    print(f"  Scale factor: {improvement['scale_factor']:.2f}x")

    # Example 4: Model comparison
    print("\n4. REAL MODEL COMPARISON")
    print("-" * 60)
    print(model_comparison().to_string(index=False))

    print("\n" + "=" * 60)
    print("See scaling_laws_deepdive.ipynb for detailed analysis!")
