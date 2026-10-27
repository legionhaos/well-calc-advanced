"""Модуль расчёта показателей работы скважины."""

import sys

if hasattr(sys.stdout, "reconfigure") and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure") and sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from well_calc import config


def calc_q_oil(q_liq: float, w_cut: float) -> float:
    return q_liq * (1.0 - w_cut)


def calc_q_water(q_liq: float, w_cut: float) -> float:
    return q_liq * w_cut


def calc_m_oil(q_oil: float) -> float:
    return q_oil * config.OIL_DENSITY / 1000.0


def calc_rho_mix(w_cut: float) -> float:
    return (1.0 - w_cut) * config.OIL_DENSITY + w_cut * config.WATER_DENSITY


def calc_p_hydro(rho_mix: float, h: float) -> float:
    return (rho_mix * config.G * h) / config.PA_TO_MPA


def calc_drawdown(p_res: float, p_wf: float) -> float:
    return p_res - p_wf
