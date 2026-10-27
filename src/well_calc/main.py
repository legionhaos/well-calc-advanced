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


def input_number(prompt: str, lo: float, hi: float) -> float:
    """Запрос и валидация вещественного числа."""
    while True:
        try:
            raw = input(prompt).strip()
        except EOFError:
            print("\nВвод прерван (EOF).")
            raise
        raw = raw.replace(",", ".")
        if raw == "":
            print("Пустая строка — введите число.")
            continue
        try:
            value = float(raw)
        except ValueError:
            print(f"'{raw}' не число. Повторите.")
            continue
        if not (lo <= value <= hi):
            print(f"Значение должно быть в диапазоне [{lo}; {hi}].")
            continue
        return value


def print_summary_table(
    q_liq: float,
    w_pct: float,
    q_oil: float,
    m_oil: float,
    q_water: float,
    rho_mix: float,
    p_hydro: float,
    drawdown: float,
    productivity: float | None,
) -> None:
    print("\n" + "=" * 52)
    print("                    СВОДКА РАСЧЁТА")
    print("=" * 52)
    print(f"{'Параметр':<28}{'Значение':>12}  {'Ед. изм.'}")
    print("-" * 52)
    print(f"{'Дебит жидкости':<28}{q_liq:>12.2f}  м³/сут")
    print(f"{'Обводнённость':<28}{w_pct:>12.2f}  %")
    print(f"{'Дебит нефти':<28}{q_oil:>12.2f}  м³/сут")
    print(f"{'Массовый дебит нефти':<28}{m_oil:>12.2f}  т/сут")
    print(f"{'Дебит воды':<28}{q_water:>12.2f}  м³/сут")
    print(f"{'Плотность смеси':<28}{rho_mix:>12.1f}  кг/м³")
    print(f"{'Гидростатическое давление':<28}{p_hydro:>12.2f}  МПа")
    print(f"{'Забойная депрессия':<28}{drawdown:>12.2f}  МПа")
    if productivity is not None:
        print(f"{'Коэф. продуктивности (J)':<28}{productivity:>12.3f}  м³/(сут·МПа)")
    else:
        print(f"{'Коэф. продуктивности (J)':<28}{'Н/Д':>12}  м³/(сут·МПа)")
    print("=" * 52)


def print_fluid_structure(w_cut: float) -> None:
    oil_bars = round((1.0 - w_cut) * 20)
    water_bars = round(w_cut * 20)
    print("\nСТРУКТУРА ПОТОКА:")
    print(f"Нефть: {'#' * oil_bars:<20} {(1.0 - w_cut) * 100:5.1f}%")
    print(f"Вода:  {'#' * water_bars:<20} {w_cut * 100:5.1f}%")


def analyze_special_cases(w_cut: float, drawdown: float, q_liq: float) -> float | None:
    productivity = None
    if w_cut == 1.0:
        print("(!) Обводнённость 100% — нефти нет.")
    if drawdown < 0:
        print("(!) Забойное давление выше пластового — вероятно фонтанирование.")
    elif drawdown == 0:
        print("(!) Депрессия нулевая, J не определён.")
    else:
        productivity = q_liq / drawdown
        print(f"Коэффициент продуктивности скважины J = {productivity:.3f} м³/(сут·МПа)")
    return productivity


def main() -> None:
    print("Расчёт технологических параметров скважины (Вариант Б)")
    print("-" * 52)

    q_liq = input_number("Введите дебит жидкости Qж [0.0; 1000.0] (м³/сут): ", 0.0, 1000.0)
    w_pct = input_number("Введите обводнённость [0.0; 100.0] (%): ", 0.0, 100.0)
    h = input_number("Введите глубину скважины H [0.0; 5000.0] (м): ", 0.0, 5000.0)
    p_res = input_number("Введите пластовое давление Pпл [0.0; 100.0] (МПа): ", 0.0, 100.0)
    p_wf = input_number("Введите забойное давление Pзаб [0.0; 100.0] (МПа): ", 0.0, 100.0)

    w_cut = w_pct / 100.0
    q_oil = calc_q_oil(q_liq, w_cut)
    q_water = calc_q_water(q_liq, w_cut)
    m_oil = calc_m_oil(q_oil)
    rho_mix = calc_rho_mix(w_cut)
    p_hydro = calc_p_hydro(rho_mix, h)
    drawdown = calc_drawdown(p_res, p_wf)

    productivity = q_liq / drawdown if drawdown > 0 else None

    print_summary_table(
        q_liq=q_liq,
        w_pct=w_pct,
        q_oil=q_oil,
        m_oil=m_oil,
        q_water=q_water,
        rho_mix=rho_mix,
        p_hydro=p_hydro,
        drawdown=drawdown,
        productivity=productivity,
    )
    print_fluid_structure(w_cut)

    print("\nАНАЛИЗ РЕЖИМА РАБОТЫ СКВАЖИНЫ:")
    analyze_special_cases(w_cut, drawdown, q_liq)


if __name__ == "__main__":
    main()
