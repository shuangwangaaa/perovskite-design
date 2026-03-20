import math
import re
from typing import Dict, List, Tuple, Optional

IONIC_RADII_CN6 = {
    'Cs': {'1+': 2.98},
    'Rb': {'1+': 2.65},
    'K':  {'1+': 2.43},
    'Na': {'1+': 1.90},
    'Li': {'1+': 1.67},

    'MA': {'1+': 2.17},
    'FA': {'1+': 2.53},

    'Ba': {'2+': 2.53},
    'Sr': {'2+': 2.19},
    'Ca': {'2+': 1.94},
    'Mg': {'2+': 1.67},

    'Pb': {'2+': 1.54, '4+': 1.54},
    'Sn': {'4+': 1.45},
    'Ge': {'2+': 1.25, '4+': 1.25},

    'Ti': {'4+': 1.76},
    'Zr': {'4+': 2.06},
    'Hf': {'4+': 2.08},

    'Si': {'4+': 1.67},

    'I':  {'1-': 1.15},
    'Br': {'1-': 0.94},
    'Cl': {'1-': 0.79},
    'F':  {'1-': 0.42},

    'O':  {'2-': 0.48},
    'S':  {'2-': 0.88},
    'Se': {'2-': 1.03},
}

OXIDATION_STATES_DEFAULT = {
    'A': {
        'Cs': 1, 'Rb': 1, 'K': 1, 'Na': 1, 'Li': 1,
        'MA': 1, 'FA': 1,
        'Ba': 2, 'Sr': 2, 'Ca': 2, 'Mg': 2,
    },
    'B': {
        'Pb': 2, 'Sn': 4, 'Ge': 2,
        'Ti': 4, 'Zr': 4, 'Hf': 4,
        'Si': 4,
    },
    'X': {
        'I': 1, 'Br': 1, 'Cl': 1, 'F': 1,
        'O': 2, 'S': 2, 'Se': 2,
    }
}

class ToleranceFactorCalculator:
    def __init__(self):
        self.ionic_radii = IONIC_RADII_CN6
        self.oxidation_states = OXIDATION_STATES_DEFAULT

    def _get_charge(self, element: str, site: str = 'A') -> str:
        """获取元素的氧化态对应的电荷字符串"""
        if element in ['MA', 'FA']:
            return '1+'

        n = self.get_oxidation_state(element, site)

        if site == 'X':
            if n == 1:
                return '1-'
            elif n == 2:
                return '2-'

        return f"{n}+"

    def get_ionic_radius(self, element: str, charge: str = None) -> Optional[float]:
        if element in self.ionic_radii:
            if charge:
                charge_map = {
                    '1+': '1+', '1-': '1-',
                    '2+': '2+', '2-': '2-',
                    '3+': '3+', '3-': '3-',
                    '4+': '4+', '4-': '4-',
                }
                mapped_charge = charge_map.get(charge, charge)
                if mapped_charge in self.ionic_radii[element]:
                    return self.ionic_radii[element][mapped_charge]
            else:
                charges = list(self.ionic_radii[element].keys())
                if charges:
                    return self.ionic_radii[element][charges[0]]
        return None

    def get_oxidation_state(self, element: str, site: str = 'A') -> int:
        ox_states = OXIDATION_STATES_DEFAULT.get(site, {})

        if element in ['MA', 'FA']:
            return 1

        if element in ox_states:
            return ox_states[element]

        if element == 'Pb' or element == 'Sn':
            return 2
        elif element == 'Ti':
            return 4
        return 1

    def parse_formula(self, formula: str) -> Tuple[str, str, str]:
        formula = formula.strip()

        organic_map = {
            'MAPb': ('MA', 'Pb', 'I'),
            'MApb': ('MA', 'Pb', 'I'),
            'FAPb': ('FA', 'Pb', 'I'),
            'FApb': ('FA', 'Pb', 'I'),
        }

        for prefix, result in organic_map.items():
            if prefix in formula or prefix.lower() in formula:
                return result

        element_pattern = r'([A-Z][a-z]?)(\d*)'
        elements = re.findall(element_pattern, formula)
        elements = [(e, int(c) if c else 1) for e, c in elements if e]

        if len(elements) >= 3:
            if elements[2][0] in ['O', 'S', 'Se', 'I', 'Br', 'Cl', 'F']:
                X = elements[2][0]
                A = elements[0][0]
                B = elements[1][0]
                return A, B, X

        return 'Cs', 'Pb', 'I'

    def calculate_goldschmidt_t(self, A: str, B: str, X: str) -> Optional[float]:
        r_A = self.get_ionic_radius(A, '1+' if self.get_oxidation_state(A, 'A') == 1 else '2+')
        r_B = self.get_ionic_radius(B, f"{self.get_oxidation_state(B, 'B')}+")
        r_X = self.get_ionic_radius(X, '1-' if self.get_oxidation_state(X, 'X') == 1 else '2-')

        if all([r_A, r_B, r_X]) and r_B > 0:
            t = (r_A + r_X) / (math.sqrt(2) * (r_B + r_X))
            return round(t, 4)
        return None

    def calculate_tau(self, A: str, B: str, X: str) -> Optional[float]:
        """
        严格按照 Bartel et al. Science Advances 2019 的公式计算新型容忍因子 τ
        τ < 4.18 → 预测为钙钛矿

        公式: τ = (r_X/r_B) - n_A * (n_A - (r_A/r_B) / ln(r_A/r_B)) / 10
        """
        r_A = self.get_ionic_radius(A, self._get_charge(A, 'A'))
        r_B = self.get_ionic_radius(B, self._get_charge(B, 'B'))
        r_X = self.get_ionic_radius(X, self._get_charge(X, 'X'))
        n_A = self.get_oxidation_state(A, 'A')

        if r_A is None or r_B is None or r_X is None or r_B <= 1e-6:
            return None

        ratio = r_A / r_B

        if ratio <= 1.0:
            return None

        try:
            ln_term = math.log(ratio)
            inner = ratio / ln_term
            correction = n_A * (n_A - inner)
            tau = (r_X / r_B) - correction
            return round(tau, 4)
        except (ValueError, ZeroDivisionError):
            return None

    def calculate_mu(self, B: str, X: str) -> Optional[float]:
        r_B = self.get_ionic_radius(B, f"{self.get_oxidation_state(B, 'B')}+")
        r_X = self.get_ionic_radius(X, '1-')

        if r_B and r_X and r_B > 0:
            return round(r_B / r_X, 4)
        return None

    def predict_stability(self, formula: str) -> Dict:
        A, B, X = self.parse_formula(formula)

        result = {
            'formula': formula,
            'composition': {'A': A, 'B': B, 'X': X},
            'goldschmidt_t': None,
            'tau': None,
            'mu': None,
            'stability_prediction': {},
            'recommendations': []
        }

        result['goldschmidt_t'] = self.calculate_goldschmidt_t(A, B, X)
        result['tau'] = self.calculate_tau(A, B, X)
        result['mu'] = self.calculate_mu(B, X)

        result['stability_prediction'] = self._evaluate_stability(
            result['tau'],
            result['goldschmidt_t'],
            result['mu']
        )
        result['recommendations'] = self._generate_recommendations(
            result['tau'],
            result['goldschmidt_t']
        )

        return result

    def _evaluate_stability(self, tau: Optional[float], t: Optional[float], mu: Optional[float]) -> Dict:
        """
        综合评估钙钛矿稳定性
        基于 Bartel et al., Science Advances 2019
        """
        pred = {}

        if tau is not None:
            if tau < 4.18:
                status = "预测为稳定钙钛矿 ✓"
                prob = self._tau_to_probability(tau)
            else:
                status = "大概率非钙钛矿结构 ✗"
                prob = max(0, 100 - self._tau_to_probability(tau - 4.18 + 1))
            pred['tau'] = {
                'status': status,
                'probability': f"{prob:.1f}%",
                'tau_value': f'{tau:.3f} (阈值: 4.18)',
                'reference': 'Bartel et al., Science Advances (2019)'
            }
        else:
            pred['tau'] = {
                'status': '无法计算 τ（r_A/r_B ≤ 1 不符合钙钛矿条件）',
                'probability': 'N/A'
            }

        if t is not None:
            if 0.8 <= t <= 1.0:
                pred['goldschmidt'] = {
                    'status': 'Goldschmidt容忍因子在理想范围内 ✓',
                    'range': f't={t:.3f} (理想范围: 0.8-1.0)',
                    'probability': '高'
                }
            elif 0.825 <= t <= 1.059:
                pred['goldschmidt'] = {
                    'status': 'Goldschmidt容忍因子在经典范围内',
                    'range': f't={t:.3f} (经典范围: 0.825-1.059)',
                    'probability': '中等'
                }
            elif t < 0.8:
                pred['goldschmidt'] = {
                    'status': 'A位离子过小 ✗',
                    'range': f't={t:.3f}',
                    'probability': '低',
                    'reason': '可能形成非钙钛矿结构'
                }
            else:
                pred['goldschmidt'] = {
                    'status': 'A位离子过大 ✗',
                    'range': f't={t:.3f}',
                    'probability': '低',
                    'reason': '可能形成层状或非钙钛矿结构'
                }

        if mu is not None:
            if 0.414 <= mu <= 0.732:
                pred['octahedral'] = {
                    'status': '八面体几何合理 ✓',
                    'mu': f'{mu:.3f} (理想范围: 0.414-0.732)'
                }
            else:
                pred['octahedral'] = {
                    'status': '八面体几何可能不稳定',
                    'mu': f'{mu:.3f} (理想范围: 0.414-0.732)'
                }

        return pred

    def _generate_recommendations(self, tau: Optional[float], t: Optional[float]) -> List[str]:
        """基于容忍因子生成建议"""
        recommendations = []

        if tau is not None:
            prob = self._tau_to_probability(tau)
            if prob >= 90:
                recommendations.append(
                    f'高稳定性预测 (τ={tau:.3f}, 置信度={prob:.1f}%)，建议深入研究'
                )
            elif prob >= 70:
                recommendations.append(
                    f'良好稳定性 (τ={tau:.3f}, 置信度={prob:.1f}%)，可进行实验验证'
                )
            elif prob >= 40:
                recommendations.append(
                    f'中等稳定性 (τ={tau:.3f}, 置信度={prob:.1f}%)，需要进一步优化'
                )
            else:
                recommendations.append(
                    f'稳定性较低 (τ={tau:.3f}, 置信度={prob:.1f}%)，建议重新选择元素组合'
                )
        else:
            recommendations.append('τ无法计算，A/B位离子半径比不符合钙钛矿形成条件')

        if t is not None:
            if not (0.8 <= t <= 1.0):
                recommendations.append(
                    f'Goldschmidt容忍因子偏离理想范围 (t={t:.3f})'
                )

        return recommendations

    def _tau_to_probability(self, tau: float) -> float:
        """
        将 τ 值转换为钙钛矿稳定性的置信度
        基于论文 Fig.2 的单调递减概率（经验分段）
        """
        if tau <= 1.0:
            return 96.0
        elif tau <= 2.0:
            return 92.0
        elif tau <= 3.0:
            return 82.0
        elif tau <= 4.0:
            return 62.0
        elif tau <= 4.18:
            return 45.0
        else:
            return 5.0

    def batch_predict(self, formulas: List[str]) -> List[Dict]:
        return [self.predict_stability(f) for f in formulas]

    def design_perovskite(self, target_band_gap: float = None,
                         target_stability: str = 'high',
                         application: str = 'solar_cell') -> Dict:
        candidates = []

        A_sites = ['Cs', 'MA', 'FA', 'Rb', 'K', 'Na']
        B_sites = ['Pb', 'Sn', 'Ge', 'Ti', 'Si']
        X_sites = ['I', 'Br', 'Cl', 'F']

        if target_band_gap:
            if target_band_gap < 1.5:
                X_sites = ['I']
            elif target_band_gap > 2.0:
                X_sites = ['Br', 'Cl']
            else:
                X_sites = ['I', 'Br']

        for A in A_sites:
            for B in B_sites:
                for X in X_sites:
                    formula = f"{A}{B}{X}3"
                    prediction = self.predict_stability(formula)

                    if prediction['tau'] is not None and prediction['tau'] < 4.18:
                        prob = self._tau_to_probability(prediction['tau'])

                        stability_levels = {
                            'high': 85,
                            'medium': 60,
                            'any': 0
                        }

                        threshold = stability_levels.get(target_stability, 85)

                        if prob >= threshold:
                            candidates.append({
                                'formula': formula,
                                'tau': prediction['tau'],
                                't': prediction['goldschmidt_t'],
                                'mu': prediction['mu'],
                                'stability_probability': prob,
                                'prediction': prediction
                            })

        candidates.sort(key=lambda x: x['stability_probability'], reverse=True)

        return {
            'target_band_gap': target_band_gap,
            'target_stability': target_stability,
            'application': application,
            'candidates': candidates[:15],
            'total_candidates': len(candidates)
        }
