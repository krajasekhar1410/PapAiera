"""
Mill Lag Profiles — Pre-built DTW Lag Scenarios for Pulp & Paper
================================================================

Provides ready-to-use signal pair definitions with industry-calibrated
parameters so mill engineers can run DTW lag analysis without manually
configuring max_lag, sample_rate, or interpretation rules.

Supported Scenarios:
    1. BLEACH_BRIGHTNESS  — Bleach tower inlet brightness -> Board brightness
    2. TOWER_PH_WETEND    — Bleach tower pH -> Wet-end pH
    3. VISCOSITY_STRENGTH  — Stage-wise pulp viscosity -> Strength properties
                            (tensile, burst, tear indices)

Usage:
    >>> from pap_ai_era.papermaking.mill_lag_profiles import run_mill_scenario, MillScenario
    >>> result = run_mill_scenario(MillScenario.BLEACH_BRIGHTNESS, cause_signal, effect_signal)
"""

import numpy as np
import pandas as pd
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Union, Dict, List, Tuple, Any

from .dtw_lag import compute_dtw_lag, compute_multi_lag, DTWLagResult, MultiLagReport


# =============================================================================
# Scenario Definitions
# =============================================================================

class MillScenario(Enum):
    """Pre-defined mill lag analysis scenarios."""
    BLEACH_BRIGHTNESS = "bleach_tower_inlet_brightness_to_board_brightness"
    TOWER_PH_WETEND = "bleach_tower_ph_to_wetend_ph"
    VISCOSITY_STRENGTH = "stagewise_viscosity_to_strength_properties"


@dataclass
class ScenarioConfig:
    """Configuration for a mill lag scenario."""
    name: str
    description: str
    cause_label: str
    effect_label: str
    cause_unit: str
    effect_unit: str
    max_lag_samples: int
    sample_rate_hz: float
    sakoe_chiba_window: int
    expected_lag_range: Tuple[float, float]  # (min_seconds, max_seconds)
    process_area: str
    typical_causes_of_deviation: List[str]


# Registry of all pre-built scenarios
SCENARIO_REGISTRY: Dict[MillScenario, ScenarioConfig] = {

    MillScenario.BLEACH_BRIGHTNESS: ScenarioConfig(
        name="Bleach Tower Inlet Brightness to Board Brightness",
        description=(
            "Tracks how brightness at the bleach tower inlet propagates through "
            "the stock system (HD tower, machine chest, approach flow) to final "
            "board brightness measured by QCS scanner on the paper machine."
        ),
        cause_label="Bleach Tower Inlet Brightness",
        effect_label="Board Brightness (QCS)",
        cause_unit="% ISO",
        effect_unit="% ISO",
        max_lag_samples=300,
        sample_rate_hz=1/60.0,   # 1 sample per minute (typical DCS historian)
        sakoe_chiba_window=60,
        expected_lag_range=(60.0, 240.0),  # 1-4 hours typical
        process_area="Bleach Plant to Paper Machine",
        typical_causes_of_deviation=[
            "ClO2 dosage upset in D0/D1 stage",
            "Bleach tower retention time variation (level changes)",
            "HD storage tower mixing and dilution effects",
            "Machine chest consistency fluctuation",
            "Broke recirculation diluting brightness",
        ]
    ),

    MillScenario.TOWER_PH_WETEND: ScenarioConfig(
        name="Bleach Tower pH to Wet-End pH",
        description=(
            "pH at the bleach tower exit propagates through washing, storage, "
            "and stock preparation to the wet-end of the paper machine. "
            "pH affects retention chemistry, sizing efficiency, and deposit formation."
        ),
        cause_label="Bleach Tower Exit pH",
        effect_label="Wet-End pH (Machine Chest / Headbox)",
        cause_unit="pH",
        effect_unit="pH",
        max_lag_samples=200,
        sample_rate_hz=1/60.0,
        sakoe_chiba_window=50,
        expected_lag_range=(30.0, 180.0),  # 30 min to 3 hours
        process_area="Bleach Plant Washers to Wet-End",
        typical_causes_of_deviation=[
            "NaOH carry-over from EOP extraction stage",
            "Washer dilution factor changes",
            "Acidic broke addition to machine chest",
            "Alum/PAC dosing variation at wet-end",
            "White water pH buffering capacity shift",
        ]
    ),

    MillScenario.VISCOSITY_STRENGTH: ScenarioConfig(
        name="Stage-wise Pulp Viscosity to Strength Properties",
        description=(
            "Pulp viscosity (a proxy for cellulose chain length / degree of "
            "polymerisation) measured at each bleaching stage correlates with "
            "final sheet strength properties (tensile index, burst index, tear index). "
            "Excessive viscosity loss in bleaching degrades fibre strength."
        ),
        cause_label="Pulp Viscosity (post-bleach stage)",
        effect_label="Sheet Strength Property",
        cause_unit="mPa.s (cP)",
        effect_unit="kN.m/kg or kPa.m2/g",
        max_lag_samples=400,
        sample_rate_hz=1/60.0,
        sakoe_chiba_window=80,
        expected_lag_range=(120.0, 480.0),  # 2-8 hours
        process_area="Bleach Plant to Paper Machine Quality Lab",
        typical_causes_of_deviation=[
            "Over-dosing ClO2 in D-stages causing cellulose degradation",
            "High temperature in oxygen delignification stage",
            "Low pH in acidic stages accelerating hydrolysis",
            "Incoming Kappa variability from digester",
            "Retention time variation in bleach towers",
        ]
    ),
}


# =============================================================================
# Public API
# =============================================================================

def get_scenario_config(scenario: MillScenario) -> ScenarioConfig:
    """Returns the configuration for a pre-built mill scenario."""
    return SCENARIO_REGISTRY[scenario]


def list_scenarios() -> pd.DataFrame:
    """Lists all available mill lag scenarios in a summary table."""
    rows = []
    for sc, cfg in SCENARIO_REGISTRY.items():
        rows.append({
            'Scenario': sc.value,
            'Name': cfg.name,
            'Cause': cfg.cause_label,
            'Effect': cfg.effect_label,
            'Expected Lag': f"{cfg.expected_lag_range[0]:.0f}-{cfg.expected_lag_range[1]:.0f} min",
            'Process Area': cfg.process_area,
        })
    return pd.DataFrame(rows)


def run_mill_scenario(
    scenario: MillScenario,
    cause: Union[np.ndarray, pd.Series],
    effect: Union[np.ndarray, pd.Series],
    sample_rate_hz: Optional[float] = None,
    max_lag_samples: Optional[int] = None,
) -> 'MillLagResult':
    """
    Runs a pre-configured DTW lag analysis for a known mill scenario.

    Uses industry-calibrated defaults for max_lag, sample_rate, and Sakoe-Chiba
    window. Generates scenario-specific interpretation and recommendations.

    Args:
        scenario: A MillScenario enum value.
        cause: 1D cause signal array.
        effect: 1D effect signal array.
        sample_rate_hz: Override default sample rate if your data differs.
        max_lag_samples: Override default max lag if needed.

    Returns:
        MillLagResult with DTW results plus mill-specific interpretation.
    """
    cfg = SCENARIO_REGISTRY[scenario]
    sr = sample_rate_hz or cfg.sample_rate_hz
    ml = max_lag_samples or cfg.max_lag_samples

    dtw_result = compute_dtw_lag(
        cause=cause,
        effect=effect,
        max_lag_samples=ml,
        sample_rate_hz=sr,
        sakoe_chiba_window=cfg.sakoe_chiba_window,
        normalise_signals=True,
    )

    interpretation = _interpret_result(dtw_result, cfg)

    return MillLagResult(
        scenario=scenario,
        config=cfg,
        dtw_result=dtw_result,
        interpretation=interpretation,
    )


def run_viscosity_strength_audit(
    viscosity_signals: Dict[str, Union[np.ndarray, pd.Series]],
    strength_signals: Dict[str, Union[np.ndarray, pd.Series]],
    sample_rate_hz: Optional[float] = None,
) -> MultiLagReport:
    """
    Specialised audit: maps multiple bleach-stage viscosity signals to
    multiple strength properties (tensile, burst, tear).

    Args:
        viscosity_signals: Dict like {'D0_viscosity': array, 'EOP_viscosity': array, ...}
        strength_signals: Dict like {'tensile_index': array, 'burst_index': array, ...}
        sample_rate_hz: Override default sample rate.

    Returns:
        MultiLagReport across all viscosity x strength combinations.
    """
    cfg = SCENARIO_REGISTRY[MillScenario.VISCOSITY_STRENGTH]
    sr = sample_rate_hz or cfg.sample_rate_hz

    # Build a combined DataFrame
    all_data = {}
    all_data.update(viscosity_signals)
    all_data.update(strength_signals)
    df = pd.DataFrame(all_data)

    return compute_multi_lag(
        data=df,
        cause_columns=list(viscosity_signals.keys()),
        effect_columns=list(strength_signals.keys()),
        max_lag_samples=cfg.max_lag_samples,
        sample_rate_hz=sr,
        sakoe_chiba_window=cfg.sakoe_chiba_window,
    )


# =============================================================================
# Result & Interpretation
# =============================================================================

@dataclass
class MillLagResult:
    """Result from a mill-specific lag scenario analysis."""
    scenario: MillScenario
    config: ScenarioConfig
    dtw_result: DTWLagResult
    interpretation: Dict[str, Any]

    def summary(self) -> str:
        """Returns a human-readable summary string."""
        r = self.dtw_result
        c = self.config
        i = self.interpretation
        lag_min = r.optimal_lag_seconds / 60.0 if r.optimal_lag_seconds else r.optimal_lag_samples
        unit = "min" if r.optimal_lag_seconds else "samples"

        lines = [
            f"=== {c.name} ===",
            f"Cause:  {c.cause_label} ({c.cause_unit})",
            f"Effect: {c.effect_label} ({c.effect_unit})",
            f"",
            f"DTW Optimal Lag:    {lag_min:.1f} {unit}",
            f"XCorr Lag:          {(r.xcorr_lag_samples / (c.sample_rate_hz * 60)):.1f} {unit}",
            f"XCorr Coefficient:  {r.xcorr_coefficient:.4f}",
            f"Confidence:         {r.confidence}",
            f"Methods Agree:      {r.method_agreement}",
            f"",
            f"Lag in Expected Range: {i['in_expected_range']}",
            f"Status: {i['status']}",
            f"",
            f"Interpretation:",
        ]
        for line in i['recommendations']:
            lines.append(f"  - {line}")
        return "\n".join(lines)


def _interpret_result(result: DTWLagResult, cfg: ScenarioConfig) -> Dict[str, Any]:
    """Generates scenario-specific interpretation of DTW results."""
    lag_s = result.optimal_lag_seconds
    if lag_s is None:
        lag_s = float(result.optimal_lag_samples)

    lag_min = abs(lag_s) / 60.0
    exp_min = cfg.expected_lag_range[0]
    exp_max = cfg.expected_lag_range[1]
    in_range = exp_min <= lag_min <= exp_max

    recommendations = []

    if result.confidence == 'LOW':
        status = "UNRELIABLE"
        recommendations.append(
            "Low confidence result. Increase data collection window or "
            "pre-filter signals to remove high-frequency noise."
        )
    elif in_range:
        status = "NORMAL"
        recommendations.append(
            f"Lag of {lag_min:.1f} min is within expected range "
            f"({exp_min:.0f}-{exp_max:.0f} min) for {cfg.process_area}."
        )
        recommendations.append(
            "Use this lag value for feedforward dead-time compensation in DCS."
        )
    elif lag_min < exp_min:
        status = "SHORT LAG WARNING"
        recommendations.append(
            f"Lag of {lag_min:.1f} min is shorter than expected "
            f"({exp_min:.0f} min minimum). Possible causes:"
        )
        recommendations.append("  * Reduced tower retention (low level in bleach/HD tower)")
        recommendations.append("  * Bypass flow or short-circuiting in stock system")
        recommendations.append("  * Check tower level trends and retention time calculation")
    else:
        status = "LONG LAG WARNING"
        recommendations.append(
            f"Lag of {lag_min:.1f} min is longer than expected "
            f"({exp_max:.0f} min maximum). Possible causes:"
        )
        recommendations.append("  * High tower levels increasing retention time")
        recommendations.append("  * Dead volume or stagnant zones in storage chests")
        recommendations.append("  * Check for plugged lines or low flow rates")

    if not result.method_agreement:
        recommendations.append(
            "DTW and cross-correlation disagree. Signal may contain "
            "nonlinear dynamics. Investigate with spectral analysis."
        )

    # Add scenario-specific deviation causes
    recommendations.append("")
    recommendations.append("Common causes of variability in this loop:")
    for cause in cfg.typical_causes_of_deviation:
        recommendations.append(f"  * {cause}")

    return {
        'in_expected_range': in_range,
        'lag_minutes': lag_min,
        'expected_range_minutes': (exp_min, exp_max),
        'status': status,
        'recommendations': recommendations,
    }


# =============================================================================
# Realistic Mill Data Simulator (for demos and testing)
# =============================================================================

def simulate_mill_scenario(
    scenario: MillScenario,
    duration_hours: float = 24.0,
    noise_level: float = 0.1,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Generates realistic simulated process data for a given mill scenario.

    Useful for testing, demos, and training. Signals include process-typical
    oscillation frequencies, drift, and noise patterns.

    Args:
        scenario: Which mill scenario to simulate.
        duration_hours: Length of simulated data in hours.
        noise_level: Relative noise amplitude (0.0 = clean, 0.3 = noisy).
        seed: Random seed for reproducibility.

    Returns:
        Dict with 'cause', 'effect', 'time_minutes', 'true_lag_minutes',
        and for VISCOSITY_STRENGTH: multi-signal dicts.
    """
    rng = np.random.RandomState(seed)

    if scenario == MillScenario.BLEACH_BRIGHTNESS:
        return _sim_bleach_brightness(duration_hours, noise_level, rng)
    elif scenario == MillScenario.TOWER_PH_WETEND:
        return _sim_tower_ph(duration_hours, noise_level, rng)
    elif scenario == MillScenario.VISCOSITY_STRENGTH:
        return _sim_viscosity_strength(duration_hours, noise_level, rng)
    else:
        raise ValueError(f"Unknown scenario: {scenario}")


def _sim_bleach_brightness(hrs, noise, rng):
    """Bleach tower inlet brightness -> Board brightness."""
    true_lag_min = 120.0  # 2-hour transport delay
    dt = 1.0  # 1-minute sampling
    n = int(hrs * 60 / dt)
    t = np.arange(n) * dt  # minutes
    lag_samples = int(true_lag_min / dt)

    # Cause: brightness oscillates around 82% ISO with slow process drift
    cause = (
        82.0
        + 2.0 * np.sin(2 * np.pi * t / 480)       # 8-hour cycle (digester Kappa)
        + 1.5 * np.sin(2 * np.pi * t / 120)       # 2-hour cycle (ClO2 dosing)
        + 0.5 * np.sin(2 * np.pi * t / 30)        # 30-min process noise
        + noise * 1.5 * rng.randn(n)
    )

    # Effect: board brightness follows with lag + slight attenuation + extra noise
    effect = np.zeros(n)
    for i in range(n):
        src = i - lag_samples
        if src >= 0:
            effect[i] = (
                cause[src] * 0.92  # 8% brightness loss through stock system + machine
                + 3.5              # offset from broke/filler contribution
                + noise * 1.0 * rng.randn()
            )
        else:
            effect[i] = 79.0 + noise * rng.randn()

    return {
        'cause': cause, 'effect': effect, 'time_minutes': t,
        'true_lag_minutes': true_lag_min,
        'cause_label': 'Bleach Tower Inlet Brightness (% ISO)',
        'effect_label': 'Board Brightness (% ISO)',
    }


def _sim_tower_ph(hrs, noise, rng):
    """Bleach tower exit pH -> Wet-end pH."""
    true_lag_min = 90.0  # 1.5-hour delay
    dt = 1.0
    n = int(hrs * 60 / dt)
    t = np.arange(n) * dt
    lag_samples = int(true_lag_min / dt)

    # Cause: tower pH oscillates around 10.5
    cause = (
        10.5
        + 0.8 * np.sin(2 * np.pi * t / 360)     # 6-hour NaOH dosing cycle
        + 0.3 * np.sin(2 * np.pi * t / 60)      # 1-hour wash water variation
        + noise * 0.4 * rng.randn(n)
    )

    # Effect: wet-end pH (much lower due to alum addition, white water buffering)
    effect = np.zeros(n)
    for i in range(n):
        src = i - lag_samples
        if src >= 0:
            effect[i] = (
                7.0 + (cause[src] - 10.5) * 0.4  # attenuated pH propagation
                + 0.2 * np.sin(2 * np.pi * t[i] / 45)  # local wet-end oscillation
                + noise * 0.3 * rng.randn()
            )
        else:
            effect[i] = 7.0 + noise * 0.2 * rng.randn()

    return {
        'cause': cause, 'effect': effect, 'time_minutes': t,
        'true_lag_minutes': true_lag_min,
        'cause_label': 'Bleach Tower Exit pH',
        'effect_label': 'Wet-End pH',
    }


def _sim_viscosity_strength(hrs, noise, rng):
    """Stage-wise viscosity -> strength properties (multi-signal)."""
    true_lags_min = {'D0': 300.0, 'EOP': 240.0, 'D1': 180.0}
    dt = 1.0
    n = int(hrs * 60 / dt)
    t = np.arange(n) * dt

    # Stage viscosities: each stage has progressively lower viscosity
    base_signal = (
        2.0 * np.sin(2 * np.pi * t / 720)
        + 1.0 * np.sin(2 * np.pi * t / 180)
    )

    visc_D0 = 850.0 + 50 * base_signal + noise * 30 * rng.randn(n)
    visc_EOP = 720.0 + 40 * base_signal + noise * 25 * rng.randn(n)
    visc_D1 = 650.0 + 35 * base_signal + noise * 20 * rng.randn(n)

    # Strength properties track viscosity with different lags and sensitivity
    def make_strength(base_visc, lag_min, scale, offset, noise_amp):
        lag_s = int(lag_min / dt)
        s = np.zeros(n)
        for i in range(n):
            src = i - lag_s
            if src >= 0:
                s[i] = offset + (base_visc[src] - 700) * scale + noise_amp * rng.randn()
            else:
                s[i] = offset + noise_amp * rng.randn()
        return s

    # Tensile index most sensitive to D1 viscosity (closest stage)
    tensile = make_strength(visc_D1, true_lags_min['D1'], 0.05, 65.0, noise * 3)
    # Burst index tracks EOP viscosity
    burst = make_strength(visc_EOP, true_lags_min['EOP'], 0.003, 4.5, noise * 0.2)
    # Tear index tracks D0 viscosity (earliest degradation)
    tear = make_strength(visc_D0, true_lags_min['D0'], 0.008, 8.0, noise * 0.5)

    return {
        'viscosity_signals': {
            'D0_viscosity': visc_D0,
            'EOP_viscosity': visc_EOP,
            'D1_viscosity': visc_D1,
        },
        'strength_signals': {
            'tensile_index': tensile,
            'burst_index': burst,
            'tear_index': tear,
        },
        'time_minutes': t,
        'true_lags_minutes': true_lags_min,
        'cause_label': 'Stage Viscosity (mPa.s)',
        'effect_label': 'Strength Properties',
    }
