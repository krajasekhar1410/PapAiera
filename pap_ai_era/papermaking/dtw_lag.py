"""
Dynamic Time Warping (DTW) Lag Calculation Module
=================================================

Computes the optimal time-delay (lag) between cause and effect process signals
using the Dynamic Time Warping algorithm.

In pulp and paper manufacturing, key process variables (e.g., stock consistency,
machine chest level, steam pressure) propagate through the system with variable
transport and reaction delays before impacting sheet quality KPIs (basis weight,
moisture, caliper). Accurate lag identification is critical for:

  - QCS/DCS control loop tuning
  - Correct alarm prioritisation
  - Root-cause analysis of variability
  - Feedforward controller design

This module provides DTW-based lag estimation which is superior to simple
cross-correlation when signals are non-stationary, noisy, or exhibit nonlinear
time-stretching — all common conditions on a running paper machine.

References:
    - Sakoe, H. and Chiba, S. (1978) "Dynamic Programming Algorithm Optimization
      for Spoken Word Recognition", IEEE Trans. Acoustics, Speech, Signal Processing.
    - BREF (2015) Best Available Techniques for the Production of Pulp, Paper
      and Board, European Commission.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional, Union, Dict, List, Tuple, Any


# =============================================================================
# Result Data Classes
# =============================================================================

@dataclass
class DTWLagResult:
    """
    Result object from a single DTW lag estimation between two signals.

    Attributes:
        optimal_lag_samples: Optimal lag in sample units (integer offset).
        optimal_lag_seconds: Optimal lag in seconds (None if sample_rate_hz not provided).
        dtw_distance: Normalised DTW distance at the optimal lag.
        xcorr_lag_samples: Cross-correlation based lag for comparison.
        xcorr_coefficient: Peak normalised cross-correlation coefficient.
        lag_scan_distances: Dict mapping each tested lag (samples) to its DTW distance.
        warping_path: The optimal DTW warping path as list of (i, j) index pairs.
        confidence: Qualitative confidence level ('HIGH', 'MEDIUM', 'LOW').
        method_agreement: True if DTW and cross-correlation agree on lag direction.
    """
    optimal_lag_samples: int
    optimal_lag_seconds: Optional[float]
    dtw_distance: float
    xcorr_lag_samples: int
    xcorr_coefficient: float
    lag_scan_distances: Dict[int, float]
    warping_path: List[Tuple[int, int]]
    confidence: str
    method_agreement: bool


@dataclass
class MultiLagReport:
    """
    Aggregated report for lag analysis across multiple cause-effect variable pairs.

    Attributes:
        pair_results: Dict mapping (cause_name, effect_name) to DTWLagResult.
        summary_table: Pandas DataFrame summarising all lag estimates.
        dominant_lag: The most frequently occurring lag across all pairs.
        recommendations: List of actionable process recommendations.
    """
    pair_results: Dict[Tuple[str, str], DTWLagResult]
    summary_table: pd.DataFrame
    dominant_lag: int
    recommendations: List[str] = field(default_factory=list)


# =============================================================================
# Core DTW Engine
# =============================================================================

def _compute_dtw_matrix(
    x: np.ndarray,
    y: np.ndarray,
    window: Optional[int] = None
) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
    """
    Computes the full DTW cost matrix and optimal warping path.

    Uses the Sakoe-Chiba band constraint when `window` is provided to
    limit the warping bandwidth and improve computational performance
    from O(N*M) to O(N*W) where W is the window size.

    Args:
        x: Reference signal (1D array, length N).
        y: Query signal (1D array, length M).
        window: Sakoe-Chiba band half-width in samples.
                If None, no constraint is applied (full matrix).

    Returns:
        Tuple of (cost_matrix, warping_path).
    """
    n = len(x)
    m = len(y)

    # Initialise cost matrix with infinity
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0.0

    # If no window constraint, set window to max possible
    if window is None:
        w = max(n, m)
    else:
        # Ensure window is at least |n - m| to guarantee a valid path
        w = max(window, abs(n - m))

    # Fill cost matrix with Sakoe-Chiba band constraint
    for i in range(1, n + 1):
        j_start = max(1, i - w)
        j_end = min(m, i + w)
        for j in range(j_start, j_end + 1):
            cost = (x[i - 1] - y[j - 1]) ** 2
            D[i, j] = cost + min(
                D[i - 1, j],      # insertion
                D[i, j - 1],      # deletion
                D[i - 1, j - 1]   # match
            )

    # Trace back the optimal warping path
    path = []
    i, j = n, m
    path.append((i - 1, j - 1))

    while i > 1 or j > 1:
        if i == 1:
            j -= 1
        elif j == 1:
            i -= 1
        else:
            candidates = [
                (D[i - 1, j - 1], i - 1, j - 1),
                (D[i - 1, j],     i - 1, j),
                (D[i, j - 1],     i,     j - 1)
            ]
            _, i, j = min(candidates, key=lambda c: c[0])
        path.append((i - 1, j - 1))

    path.reverse()
    return D, path


def _normalised_dtw_distance(D: np.ndarray, n: int, m: int) -> float:
    """
    Returns the DTW distance normalised by the path length.
    """
    raw = D[n, m]
    return np.sqrt(raw) / (n + m)


def _normalised_cross_correlation(
    x: np.ndarray,
    y: np.ndarray,
    max_lag: int
) -> Tuple[int, float]:
    """
    Computes normalised cross-correlation between x and y.

    Uses absolute correlation to handle both direct and inverse
    relationships (e.g., temperature up -> kappa down).

    Returns the lag (in samples) and the peak correlation coefficient.
    Positive lag means y lags x (effect follows cause).

    Args:
        x: Cause signal.
        y: Effect signal.
        max_lag: Maximum lag to scan (in samples).

    Returns:
        Tuple of (best_lag, best_abs_coefficient).
    """
    x_norm = (x - np.mean(x)) / (np.std(x) + 1e-12)
    y_norm = (y - np.mean(y)) / (np.std(y) + 1e-12)

    n = len(x_norm)
    best_lag = 0
    best_abs_coeff = -1.0
    best_raw_coeff = 0.0

    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            xi = x_norm[:n - lag]
            yi = y_norm[lag:]
        else:
            xi = x_norm[-lag:]
            yi = y_norm[:n + lag]

        if len(xi) < 10:
            continue

        coeff = np.dot(xi, yi) / len(xi)
        if abs(coeff) > best_abs_coeff:
            best_abs_coeff = abs(coeff)
            best_raw_coeff = coeff
            best_lag = lag

    return best_lag, float(best_abs_coeff)


# =============================================================================
# Universal API — Works for ANY Process, ANY Parameters
# =============================================================================

def find_lag(
    input_signal: Union[np.ndarray, pd.Series, list],
    output_signal: Union[np.ndarray, pd.Series, list],
    time_interval: Optional[float] = None,
    time_unit: str = 'seconds',
    max_lag: Optional[int] = None,
    input_name: str = 'Input',
    output_name: str = 'Output',
) -> Dict[str, Any]:
    """
    Find the time lag between ANY input parameter and ANY output parameter.

    This is the simplest entry point in PapAiEra for lag detection.
    Works for any process — pulp mill, chemical plant, power plant,
    food processing, pharma, or any system where an input affects
    an output with a delay.

    Just pass two arrays of equal-length time-series data and the tool
    figures out the rest automatically.

    Args:
        input_signal:  Array of the INPUT (cause / upstream) variable.
        output_signal: Array of the OUTPUT (effect / downstream) variable.
        time_interval: Time between consecutive samples (e.g., 1.0 for 1-second
                       sampling, 60.0 for 1-minute sampling). If None, results
                       are reported in sample units only.
        time_unit:     Unit string for display ('seconds', 'minutes', 'hours').
        max_lag:       Maximum lag to search, in number of samples.
                       Default: auto-calculated as 1/4 of signal length.
        input_name:    Name of the input variable (for display).
        output_name:   Name of the output variable (for display).

    Returns:
        Dictionary with keys:
            - 'lag_samples': Optimal lag in sample units
            - 'lag_time': Optimal lag in time units (None if time_interval not given)
            - 'lag_unit': The time unit string
            - 'confidence': 'HIGH', 'MEDIUM', or 'LOW'
            - 'xcorr_lag_samples': Cross-correlation lag for comparison
            - 'xcorr_coefficient': Correlation strength (0 to 1)
            - 'methods_agree': Whether DTW and cross-correlation agree
            - 'input_name': Name of input variable
            - 'output_name': Name of output variable
            - 'full_result': The complete DTWLagResult object for advanced use

    Example — Any process, any parameters:

        >>> from pap_ai_era.papermaking.dtw_lag import find_lag
        >>>
        >>> # Example 1: Temperature input -> Viscosity output
        >>> result = find_lag(temperature, viscosity, time_interval=1.0, time_unit='minutes')
        >>> print(f"Lag: {result['lag_time']} {result['lag_unit']}")
        >>>
        >>> # Example 2: Feed rate -> Product quality
        >>> result = find_lag(feed_rate, quality, time_interval=5.0, time_unit='seconds')
        >>>
        >>> # Example 3: No time info — just raw sample lag
        >>> result = find_lag(signal_a, signal_b)
    """
    # Convert to numpy
    x = np.asarray(input_signal, dtype=np.float64).ravel()
    y = np.asarray(output_signal, dtype=np.float64).ravel()

    if len(x) != len(y):
        raise ValueError(
            f"Input ({len(x)} samples) and output ({len(y)} samples) must be same length."
        )

    # Auto-configure max_lag: default to 1/4 of signal length
    if max_lag is None:
        max_lag = max(10, len(x) // 4)

    # Ensure signals are long enough
    min_len = 2 * max_lag + 20
    if len(x) < min_len:
        # Reduce max_lag to fit
        max_lag = max(5, (len(x) - 20) // 2)

    # Compute sample rate in Hz from time_interval
    sample_rate_hz = None
    if time_interval is not None and time_interval > 0:
        sample_rate_hz = 1.0 / time_interval

    # Run DTW lag calculation
    dtw_result = compute_dtw_lag(
        cause=x,
        effect=y,
        max_lag_samples=max_lag,
        sample_rate_hz=sample_rate_hz,
        normalise_signals=True,
    )

    # Compute lag in user's time unit
    lag_time = None
    if time_interval is not None:
        lag_time = dtw_result.optimal_lag_samples * time_interval

    return {
        'lag_samples': dtw_result.optimal_lag_samples,
        'lag_time': lag_time,
        'lag_unit': time_unit if time_interval is not None else 'samples',
        'confidence': dtw_result.confidence,
        'xcorr_lag_samples': dtw_result.xcorr_lag_samples,
        'xcorr_coefficient': dtw_result.xcorr_coefficient,
        'methods_agree': dtw_result.method_agreement,
        'input_name': input_name,
        'output_name': output_name,
        'full_result': dtw_result,
    }


def find_multi_lag(
    data: pd.DataFrame,
    input_columns: List[str],
    output_columns: List[str],
    time_interval: Optional[float] = None,
    time_unit: str = 'seconds',
    max_lag: Optional[int] = None,
) -> pd.DataFrame:
    """
    Find time lags between ALL combinations of input and output parameters.

    Pass a DataFrame with your process data — any number of input columns
    and output columns. The tool tests every input-output pair and returns
    a clean summary table.

    Args:
        data: DataFrame with time-series columns.
        input_columns: List of column names for INPUT (cause) variables.
        output_columns: List of column names for OUTPUT (effect) variables.
        time_interval: Time between samples.
        time_unit: Unit string for display.
        max_lag: Maximum lag to search (samples). Auto-configured if None.

    Returns:
        DataFrame with lag results for every input-output pair.

    Example:
        >>> import pandas as pd
        >>> from pap_ai_era.papermaking.dtw_lag import find_multi_lag
        >>>
        >>> df = pd.read_csv('my_process_data.csv')
        >>> results = find_multi_lag(
        ...     data=df,
        ...     input_columns=['temperature', 'pressure', 'flow_rate'],
        ...     output_columns=['product_quality', 'yield'],
        ...     time_interval=1.0,
        ...     time_unit='minutes'
        ... )
        >>> print(results)
    """
    rows = []
    for inp in input_columns:
        for out in output_columns:
            try:
                r = find_lag(
                    input_signal=data[inp].values,
                    output_signal=data[out].values,
                    time_interval=time_interval,
                    time_unit=time_unit,
                    max_lag=max_lag,
                    input_name=inp,
                    output_name=out,
                )
                rows.append({
                    'Input': inp,
                    'Output': out,
                    f'Lag ({time_unit})': r['lag_time'],
                    'Lag (samples)': r['lag_samples'],
                    'Confidence': r['confidence'],
                    'Correlation': round(r['xcorr_coefficient'], 4),
                    'Methods Agree': r['methods_agree'],
                })
            except Exception as e:
                rows.append({
                    'Input': inp,
                    'Output': out,
                    f'Lag ({time_unit})': None,
                    'Lag (samples)': None,
                    'Confidence': 'ERROR',
                    'Correlation': None,
                    'Methods Agree': None,
                })
    return pd.DataFrame(rows)


# =============================================================================
# Advanced API — Single Pair Lag Estimation
# =============================================================================

def compute_dtw_lag(
    cause: Union[np.ndarray, pd.Series],
    effect: Union[np.ndarray, pd.Series],
    max_lag_samples: int = 100,
    lag_step: int = 1,
    sample_rate_hz: Optional[float] = None,
    sakoe_chiba_window: Optional[int] = None,
    normalise_signals: bool = True
) -> DTWLagResult:
    """
    Estimates the optimal time-lag between a cause signal and an effect signal
    using Dynamic Time Warping.

    The function slides the effect signal across a range of lags and computes
    the DTW distance at each offset. The lag producing the minimum DTW distance
    is reported as the optimal lag.

    In addition, a standard cross-correlation lag is computed for comparison.
    Agreement between the two methods increases confidence.

    Example — Finding the lag between stock consistency and basis weight:

        >>> import numpy as np
        >>> from pap_ai_era.papermaking.dtw_lag import compute_dtw_lag
        >>>
        >>> # Simulated 1 Hz process data
        >>> t = np.arange(0, 600)  # 10 minutes
        >>> consistency = np.sin(0.02 * t) + 0.1 * np.random.randn(len(t))
        >>> # Basis weight follows consistency with a 45-second lag
        >>> bw = np.sin(0.02 * (t - 45)) + 0.1 * np.random.randn(len(t))
        >>>
        >>> result = compute_dtw_lag(consistency, bw, max_lag_samples=100, sample_rate_hz=1.0)
        >>> print(f"Optimal lag: {result.optimal_lag_seconds:.1f} seconds")
        >>> print(f"Confidence: {result.confidence}")

    Args:
        cause: 1D array of the cause (upstream) process variable.
        effect: 1D array of the effect (downstream) quality variable.
        max_lag_samples: Maximum lag offset to scan, in sample units.
        lag_step: Step size between lag offsets to test.
                  Use >1 for coarse initial scan on very long signals.
        sample_rate_hz: Sample rate in Hz.  If provided, lag is also reported
                        in seconds.
        sakoe_chiba_window: Sakoe-Chiba band half-width for DTW constraint.
                            If None, defaults to min(50, len(signal)//4).
        normalise_signals: If True, z-score normalise both signals before
                           DTW computation. Strongly recommended for process
                           variables with different engineering units.

    Returns:
        DTWLagResult: Comprehensive lag estimation results.

    Raises:
        ValueError: If signals are too short or max_lag_samples is invalid.
    """
    # Convert to numpy arrays
    x = np.asarray(cause, dtype=np.float64).ravel()
    y = np.asarray(effect, dtype=np.float64).ravel()

    # Validate inputs
    min_length = 2 * max_lag_samples + 20
    if len(x) < min_length or len(y) < min_length:
        raise ValueError(
            f"Signals too short (length {len(x)}, {len(y)}). "
            f"Need at least {min_length} samples for max_lag_samples={max_lag_samples}."
        )
    if max_lag_samples < 1:
        raise ValueError("max_lag_samples must be >= 1.")

    # Handle NaN by linear interpolation
    for arr in [x, y]:
        nans = np.isnan(arr)
        if nans.any():
            idx = np.arange(len(arr))
            arr[nans] = np.interp(idx[nans], idx[~nans], arr[~nans])

    # Z-score normalisation
    if normalise_signals:
        x = (x - np.mean(x)) / (np.std(x) + 1e-12)
        y = (y - np.mean(y)) / (np.std(y) + 1e-12)

    # Default Sakoe-Chiba window
    if sakoe_chiba_window is None:
        sakoe_chiba_window = min(50, len(x) // 4)

    # --- Performance: downsample if signals are very long ---
    # For signals > 500 points after trimming, downsample to keep DTW fast.
    max_dtw_window = 300
    analysis_len = len(x) - 2 * max_lag_samples
    downsample_factor = 1

    if analysis_len > max_dtw_window:
        downsample_factor = max(1, analysis_len // max_dtw_window)

    def _downsample(arr):
        if downsample_factor <= 1:
            return arr
        # Average pooling for downsampling
        trim = len(arr) - (len(arr) % downsample_factor)
        return arr[:trim].reshape(-1, downsample_factor).mean(axis=1)

    # --- Two-Phase Lag Scan ---
    # Phase 1: Fast cross-correlation to find candidate lag regions
    xcorr_lag, xcorr_coeff = _normalised_cross_correlation(x, y, max_lag_samples)

    # Also compute xcorr with inverted signal to catch inverse relationships
    xcorr_lag_inv, xcorr_coeff_inv = _normalised_cross_correlation(x, -y, max_lag_samples)

    # Phase 2: DTW fine scan around xcorr peak(s) and nearby regions
    dtw_scan_radius = max(20, max_lag_samples // 5)

    # Scan around xcorr peak, inverted-xcorr peak, and lag=0
    scan_centers = list(set([xcorr_lag, xcorr_lag_inv, 0]))
    all_lags_to_test = set()

    for center in scan_centers:
        s = max(-max_lag_samples, center - dtw_scan_radius)
        e = min(max_lag_samples, center + dtw_scan_radius)
        for lag in range(s, e + 1, lag_step):
            all_lags_to_test.add(lag)

    x_window_full = x[max_lag_samples: max_lag_samples + analysis_len]
    x_window = _downsample(x_window_full)
    ds_scw = max(5, sakoe_chiba_window // downsample_factor)

    lag_distances: Dict[int, float] = {}
    for lag in sorted(all_lags_to_test):
        offset = max_lag_samples + lag
        y_window_full = y[offset: offset + analysis_len]
        if len(y_window_full) != len(x_window_full):
            continue
        y_window = _downsample(y_window_full)
        if len(y_window) != len(x_window):
            continue

        D, _ = _compute_dtw_matrix(x_window, y_window, window=ds_scw)
        dist = _normalised_dtw_distance(D, len(x_window), len(y_window))
        lag_distances[lag] = dist

    if not lag_distances:
        raise ValueError("No valid lag offsets were computed. Check signal lengths.")

    # Find optimal lag
    optimal_lag = min(lag_distances, key=lag_distances.get)
    optimal_dist = lag_distances[optimal_lag]

    # Compute the warping path at the optimal lag (on downsampled data)
    offset = max_lag_samples + optimal_lag
    y_opt = _downsample(y[offset: offset + analysis_len])
    D_opt, warping_path = _compute_dtw_matrix(x_window, y_opt, window=ds_scw)

    # Cross-correlation already computed in Phase 1 above

    # --- Confidence estimation ---
    # Uses valley sharpness, cross-correlation strength, and method agreement.
    # Valley sharpness: how much does the optimal DTW distance stand out
    # from the overall distance landscape (median and max)?
    all_dists = np.array(sorted(lag_distances.values()))
    median_dist = np.median(all_dists)
    max_dist = np.max(all_dists)
    min_dist = np.min(all_dists)

    # Valley depth relative to the full range
    dist_range = max_dist - min_dist
    if dist_range > 1e-12:
        valley_sharpness = (median_dist - min_dist) / dist_range
    else:
        valley_sharpness = 0.0

    # Lag agreement: DTW and XCorr lag should be within 10% of max_lag_samples
    lag_tolerance = max(5, int(0.1 * max_lag_samples))
    method_agreement = abs(optimal_lag - xcorr_lag) <= lag_tolerance

    # Composite confidence
    score = 0
    if valley_sharpness > 0.3:
        score += 1
    if valley_sharpness > 0.15:
        score += 1
    if xcorr_coeff > 0.5:
        score += 1
    if xcorr_coeff > 0.3:
        score += 1
    if method_agreement:
        score += 1

    if score >= 4:
        confidence = 'HIGH'
    elif score >= 2:
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'

    # Convert lag to seconds if sample rate provided
    lag_seconds = None
    if sample_rate_hz is not None and sample_rate_hz > 0:
        lag_seconds = optimal_lag / sample_rate_hz

    return DTWLagResult(
        optimal_lag_samples=int(optimal_lag),
        optimal_lag_seconds=lag_seconds,
        dtw_distance=float(optimal_dist),
        xcorr_lag_samples=int(xcorr_lag),
        xcorr_coefficient=float(xcorr_coeff),
        lag_scan_distances=lag_distances,
        warping_path=warping_path,
        confidence=confidence,
        method_agreement=bool(method_agreement)
    )


# =============================================================================
# Public API — Multi-Variable Lag Analysis
# =============================================================================

def compute_multi_lag(
    data: pd.DataFrame,
    cause_columns: List[str],
    effect_columns: List[str],
    max_lag_samples: int = 100,
    lag_step: int = 1,
    sample_rate_hz: Optional[float] = None,
    sakoe_chiba_window: Optional[int] = None
) -> MultiLagReport:
    """
    Performs DTW lag analysis across all combinations of cause and effect variables.

    This is the primary entry point for mill engineers running a full process audit.
    Given a DataFrame of time-synchronised process data, it computes the optimal lag
    between every (cause, effect) pair and generates an actionable summary.

    Example — Wet-end process audit:

        >>> import pandas as pd
        >>> from pap_ai_era.papermaking.dtw_lag import compute_multi_lag
        >>>
        >>> df = pd.read_csv('process_data.csv')
        >>> report = compute_multi_lag(
        ...     data=df,
        ...     cause_columns=['consistency', 'headbox_pressure', 'steam_flow'],
        ...     effect_columns=['basis_weight', 'moisture'],
        ...     max_lag_samples=120,
        ...     sample_rate_hz=1.0
        ... )
        >>> print(report.summary_table)
        >>> for rec in report.recommendations:
        ...     print(rec)

    Args:
        data: Pandas DataFrame with time-series columns. Must not contain
              all-NaN columns for the specified cause/effect variables.
        cause_columns: List of column names for cause (upstream) variables.
        effect_columns: List of column names for effect (downstream) variables.
        max_lag_samples: Maximum lag to scan for each pair.
        lag_step: Step size for lag scanning.
        sample_rate_hz: Sample rate in Hz.
        sakoe_chiba_window: Sakoe-Chiba bandwidth constraint.

    Returns:
        MultiLagReport: Aggregated report with per-pair results and recommendations.
    """
    pair_results: Dict[Tuple[str, str], DTWLagResult] = {}
    summary_rows = []

    for cause_col in cause_columns:
        for effect_col in effect_columns:
            if cause_col not in data.columns:
                raise ValueError(f"Cause column '{cause_col}' not found in DataFrame.")
            if effect_col not in data.columns:
                raise ValueError(f"Effect column '{effect_col}' not found in DataFrame.")

            cause_signal = data[cause_col].values
            effect_signal = data[effect_col].values

            try:
                result = compute_dtw_lag(
                    cause=cause_signal,
                    effect=effect_signal,
                    max_lag_samples=max_lag_samples,
                    lag_step=lag_step,
                    sample_rate_hz=sample_rate_hz,
                    sakoe_chiba_window=sakoe_chiba_window,
                    normalise_signals=True
                )
                pair_results[(cause_col, effect_col)] = result

                summary_rows.append({
                    'Cause Variable': cause_col,
                    'Effect Variable': effect_col,
                    'DTW Lag (samples)': result.optimal_lag_samples,
                    'DTW Lag (seconds)': result.optimal_lag_seconds,
                    'DTW Distance': round(result.dtw_distance, 6),
                    'XCorr Lag (samples)': result.xcorr_lag_samples,
                    'XCorr Coefficient': round(result.xcorr_coefficient, 4),
                    'Confidence': result.confidence,
                    'Methods Agree': result.method_agreement
                })

            except ValueError as e:
                summary_rows.append({
                    'Cause Variable': cause_col,
                    'Effect Variable': effect_col,
                    'DTW Lag (samples)': None,
                    'DTW Lag (seconds)': None,
                    'DTW Distance': None,
                    'XCorr Lag (samples)': None,
                    'XCorr Coefficient': None,
                    'Confidence': 'ERROR',
                    'Methods Agree': None
                })

    summary_table = pd.DataFrame(summary_rows)

    # Determine dominant lag (mode of the optimal lags, excluding errors)
    valid_lags = [r.optimal_lag_samples for r in pair_results.values()]
    if valid_lags:
        lag_counts: Dict[int, int] = {}
        for lag in valid_lags:
            lag_counts[lag] = lag_counts.get(lag, 0) + 1
        dominant_lag = max(lag_counts, key=lag_counts.get)
    else:
        dominant_lag = 0

    # Generate process recommendations
    recommendations = _generate_recommendations(pair_results, sample_rate_hz)

    return MultiLagReport(
        pair_results=pair_results,
        summary_table=summary_table,
        dominant_lag=dominant_lag,
        recommendations=recommendations
    )


# =============================================================================
# Recommendation Engine
# =============================================================================

def _generate_recommendations(
    pair_results: Dict[Tuple[str, str], DTWLagResult],
    sample_rate_hz: Optional[float]
) -> List[str]:
    """
    Generates actionable process recommendations based on lag analysis results.

    Rules are based on pulp & paper process knowledge:
    - Very short lags (<5s): Direct mechanical coupling, check sensors
    - Short lags (5-30s): Hydraulic transport delay (approach system, headbox)
    - Medium lags (30-120s): Stock preparation pipeline delay
    - Long lags (>120s): Chemical reaction or thermal process delay
    """
    recommendations = []

    for (cause, effect), result in pair_results.items():
        lag_s = result.optimal_lag_seconds
        if lag_s is None:
            # Fall back to sample-based heuristic
            lag_s = float(result.optimal_lag_samples)

        abs_lag = abs(lag_s)
        conf = result.confidence

        if conf == 'LOW':
            recommendations.append(
                f"[{cause} → {effect}] LOW confidence (lag={lag_s:.1f}s). "
                f"Possible causes: weak signal coupling, non-stationary process, "
                f"or insufficient data length. Consider collecting more data or "
                f"pre-filtering signals with a band-pass filter."
            )
            continue

        if abs_lag < 5.0:
            recommendations.append(
                f"[{cause} → {effect}] Near-instantaneous coupling (lag={lag_s:.1f}s, {conf}). "
                f"Suggests direct mechanical or hydraulic link. "
                f"Verify sensor placement — could be measuring same physical phenomenon."
            )
        elif abs_lag < 30.0:
            recommendations.append(
                f"[{cause} → {effect}] Short transport delay (lag={lag_s:.1f}s, {conf}). "
                f"Typical of approach flow system or headbox-to-wire transit. "
                f"Use this lag for feedforward controller dead-time compensation."
            )
        elif abs_lag < 120.0:
            recommendations.append(
                f"[{cause} → {effect}] Medium process delay (lag={lag_s:.1f}s, {conf}). "
                f"Consistent with stock preparation pipeline (machine chest → headbox). "
                f"Review DCS scan-average controller dead-time setting — should match this lag."
            )
        else:
            recommendations.append(
                f"[{cause} → {effect}] Long process delay (lag={lag_s:.1f}s, {conf}). "
                f"Indicates chemical reaction kinetics or thermal loop delay "
                f"(e.g., digester retention, bleach tower, dryer hood thermal inertia). "
                f"This variable is not suitable for fast-loop control; "
                f"consider cascade or model-predictive control strategy."
            )

        if not result.method_agreement:
            recommendations.append(
                f"  ⚠ DTW and cross-correlation disagree on [{cause} → {effect}]. "
                f"DTW={result.optimal_lag_samples} samples vs XCorr={result.xcorr_lag_samples} samples. "
                f"Signal may contain nonlinear dynamics — investigate with spectral analysis."
            )

    return recommendations


# =============================================================================
# Utility — Quick Lag Plot Data Generator
# =============================================================================

def get_lag_profile(result: DTWLagResult) -> pd.DataFrame:
    """
    Converts the lag scan distances from a DTWLagResult into a plot-ready DataFrame.

    Useful for visualising the DTW distance as a function of lag offset
    to verify the optimality and sharpness of the lag estimate.

    Args:
        result: A DTWLagResult object from compute_dtw_lag().

    Returns:
        DataFrame with columns: 'lag_samples', 'dtw_distance', 'is_optimal'.
    """
    rows = []
    for lag, dist in sorted(result.lag_scan_distances.items()):
        rows.append({
            'lag_samples': lag,
            'dtw_distance': dist,
            'is_optimal': (lag == result.optimal_lag_samples)
        })
    return pd.DataFrame(rows)
