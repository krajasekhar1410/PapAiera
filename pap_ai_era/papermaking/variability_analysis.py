import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Union, Dict, List, Any

@dataclass
class VPAResult:
    """
    Result object containing the Variance Partition Analysis (VPA) metrics and inferences.
    """
    sigma_raw: Dict[str, float]
    sigma_2s: Dict[str, float]
    normalised: Dict[str, float]
    pct_distribution: Dict[str, float]
    process_average: float
    threshold_status: Dict[str, str]
    primary_problem: Optional[str]
    inference: List[Dict[str, Any]]
    kpi_trend_flag: Optional[bool] = None

def compute_vpa(
    data: Union[pd.DataFrame, np.ndarray],
    scan_col: Optional[str] = None,
    box_col: Optional[str] = None,
    value_col: str = 'value',
    process_average: Optional[float] = None,
    goals: Optional[Dict[str, float]] = None,
    thresholds: Optional[Dict[str, float]] = None,
    sigma_convention: int = 2,
    trend_window_reels: Optional[int] = None
) -> VPAResult:
    """
    Computes Variance Partition Analysis (VPA) from scanner profiles.
    
    Decomposes total variability into Machine Direction Long-term (MDL),
    Cross Direction (CD), and Machine Direction Short-term (MDS) components.
    
    Args:
        data: 2D array of [scans x boxes] or pandas DataFrame in long format.
        scan_col: Column name for scan index if data is a DataFrame.
        box_col: Column name for data box index if data is a DataFrame.
        value_col: Measurement column if data is a DataFrame.
        process_average: Baseline process average (e.g., target gsm or moisture %). 
                        If None, it is computed from the data grand mean. This value is used 
                        to calculate the Normalized % of Process variability.
        goals: Target distribution of variability percentages. Default: {'MDS': 70, 'CD': 20, 'MDL': 10}.
        thresholds: Alert thresholds for variability percentages. Default: {'MDS': 75, 'CD': 25, 'MDL': 15}.
        sigma_convention: Multiplier for reporting (default 2 for 2-sigma).
        trend_window_reels: Optional window size for multi-reel KPI trending.
        
    Returns:
        VPAResult: Object containing calculated variances, normalizations, alert statuses, and root cause inference.
    """
    if goals is None:
        goals = {'MDS': 70.0, 'CD': 20.0, 'MDL': 10.0}
    if thresholds is None:
        thresholds = {'MDS': 75.0, 'CD': 25.0, 'MDL': 15.0}

    # Step 1: Build the 2D array X[m × n]
    if isinstance(data, pd.DataFrame) and scan_col and box_col:
        # Pivot long format to wide matrix
        pivot_df = data.pivot(index=scan_col, columns=box_col, values=value_col)
        # Handle missing boxes by interpolation or forward/backward filling
        pivot_df = pivot_df.interpolate(axis=1).bfill(axis=1).ffill(axis=1)
        X = pivot_df.to_numpy()
    else:
        X = np.asarray(data)

    # Step 2: Compute grand mean and process average
    X_grand = np.nanmean(X)
    if process_average is None:
        process_average = X_grand

    # Step 3: Compute scan averages (MD trend signal)
    X_scan = np.nanmean(X, axis=1)

    # Step 4: Compute data box averages (CD profile signal)
    X_db = np.nanmean(X, axis=0)

    # Step 5: Compute MDL sigma (population std of scan averages)
    MDL_sigma = np.nanstd(X_scan, ddof=0)

    # Step 6: Compute CD sigma (population std of data-box averages)
    CD_sigma = np.nanstd(X_db, ddof=0)

    # Step 7: Compute TOT sigma (population std of all data points)
    TOT_sigma = np.nanstd(X, ddof=0)

    # Step 8: Compute MDS sigma (residual, from variance subtraction)
    Var_TOT = TOT_sigma ** 2
    Var_MDL = MDL_sigma ** 2
    Var_CD  = CD_sigma ** 2
    Var_MDS = Var_TOT - Var_MDL - Var_CD
    
    # Clamp negative values due to floating point inaccuracies
    MDS_sigma = np.sqrt(max(Var_MDS, 0.0))

    # Step 9: Apply sigma convention multiplier
    TOT_mult = sigma_convention * TOT_sigma
    MDL_mult = sigma_convention * MDL_sigma
    CD_mult  = sigma_convention * CD_sigma
    MDS_mult = sigma_convention * MDS_sigma

    # Step 10: Normalise to % of Process
    TOT_norm = (100.0 * TOT_mult / process_average) if process_average else 0.0
    MDL_norm = (100.0 * MDL_mult / process_average) if process_average else 0.0
    CD_norm  = (100.0 * CD_mult / process_average) if process_average else 0.0
    MDS_norm = (100.0 * MDS_mult / process_average) if process_average else 0.0

    # Step 11: Compute % distribution within TOT
    if Var_TOT > 0:
        pct_MDL = 100.0 * (Var_MDL / Var_TOT)
        pct_CD  = 100.0 * (Var_CD  / Var_TOT)
        pct_MDS = 100.0 * (max(Var_MDS, 0.0) / Var_TOT)
    else:
        pct_MDL = pct_CD = pct_MDS = 0.0

    # Verify distributions sum to approximately 100%
    total_pct = pct_MDL + pct_CD + pct_MDS
    if total_pct > 0:
        pct_MDL = (pct_MDL / total_pct) * 100.0
        pct_CD = (pct_CD / total_pct) * 100.0
        pct_MDS = (pct_MDS / total_pct) * 100.0

    # Step 12: Apply threshold logic and generate inference
    # Assume an overall TOT threshold of 10% of process (as a standard placeholder constraint)
    tot_alert = 'ALERT' if TOT_norm > 10.0 else 'OK'
    
    threshold_status = {
        'MDL': 'ALERT' if pct_MDL > thresholds.get('MDL', 15.0) else 'OK',
        'CD': 'ALERT' if pct_CD > thresholds.get('CD', 25.0) else 'OK',
        'MDS': 'ALERT' if pct_MDS > thresholds.get('MDS', 75.0) else 'OK',
        'TOT': tot_alert
    }

    # Identify primary problem based on maximum deviation from expected distribution goal
    deviations = {
        'MDL': pct_MDL - goals.get('MDL', 10.0),
        'CD': pct_CD - goals.get('CD', 20.0),
        'MDS': pct_MDS - goals.get('MDS', 70.0)
    }
    
    primary_problem = None
    max_dev = -float('inf')
    for comp, dev in deviations.items():
        if dev > 0 and dev > max_dev:
            max_dev = dev
            primary_problem = comp

    # Clear primary problem if all alerts are OK and we're not breaching TOT
    if all(status == 'OK' for status in threshold_status.values()):
        primary_problem = None

    # Inference mapping rules
    inference = []
    
    # MDL Inferences
    if threshold_status['MDL'] == 'ALERT':
        if pct_MDS <= thresholds.get('MDS', 75.0) and pct_CD <= thresholds.get('CD', 25.0):
            inference.append({
                'cause_area': 'Scan-level weight/moisture control loop instability',
                'equipment': 'QCS scan-average control loop; DCS process variable',
                'frequency_band': 'Slow: 2m-20m',
                'recommended_action': 'Open-loop bump test of scan-level control; review QCS controller tuning; check transmitter calibration',
                'confidence': 'HIGH'
            })
        if pct_MDS > thresholds.get('MDS', 75.0):
            inference.append({
                'cause_area': 'Stock preparation — chest upset or consistency disturbance',
                'equipment': 'Machine chest, proportional valve, broke system',
                'frequency_band': 'Very slow: 20m to 3hrs',
                'recommended_action': 'DCS historian review of machine chest level and consistency; check proportional valve stroke',
                'confidence': 'HIGH'
            })
            
    # CD Inferences
    if threshold_status['CD'] == 'ALERT':
        inference.append({
            'cause_area': 'Cross Direction Control / Profile non-uniformity',
            'equipment': 'Headbox dilution manifold; CD actuator array; slice lip; Press roll crown',
            'frequency_band': 'Spatial: Broad to medium wavelength',
            'recommended_action': 'Evaluate single-scan profiles; contour plot (scan × box); check actuator range vs. required correction; nip impression measurement',
            'confidence': 'HIGH'
        })

    # MDS Inferences
    if threshold_status['MDS'] == 'ALERT':
        inference.append({
            'cause_area': 'Mechanical vibration, Dilute stock circuit pulsation, or Fast loops',
            'equipment': 'Press rolls, suction rolls, fan pump, pressure screen, fast consistency regulators',
            'frequency_band': 'Fast to Medium: 1s – 60s (0.01 Hz – 1.0 Hz)',
            'recommended_action': 'High-speed single-point data; vibration spectrum analysis; fan pump pressure trend; actuator step response test',
            'confidence': 'HIGH'
        })

    return VPAResult(
        sigma_raw={'TOT': TOT_sigma, 'MDL': MDL_sigma, 'CD': CD_sigma, 'MDS': MDS_sigma},
        sigma_2s={'TOT': TOT_mult, 'MDL': MDL_mult, 'CD': CD_mult, 'MDS': MDS_mult},
        normalised={'TOT': TOT_norm, 'MDL': MDL_norm, 'CD': CD_norm, 'MDS': MDS_norm},
        pct_distribution={'MDL': pct_MDL, 'CD': pct_CD, 'MDS': pct_MDS},
        process_average=process_average,
        threshold_status=threshold_status,
        primary_problem=primary_problem,
        inference=inference,
        kpi_trend_flag=None
    )
