import re
from typing import Dict, List, Optional

class StructureConverter:
    @staticmethod
    def parse_chemical_formula(formula: str) -> Dict:
        formula = formula.strip()
        elements = re.findall(r'([A-Z][a-z]?)(\d*\.?\d*)', formula)
        parsed = {}
        for element, count in elements:
            if element:
                count = int(count) if count else 1
                parsed[element] = count
        return parsed

    @staticmethod
    def extract_lattice_parameters(text: str) -> Optional[Dict]:
        patterns = {
            'a': r'a\s*=\s*(\d+\.?\d*)\s*Å',
            'b': r'b\s*=\s*(\d+\.?\d*)\s*Å',
            'c': r'c\s*=\s*(\d+\.?\d*)\s*Å',
            'alpha': r'α\s*=\s*(\d+\.?\d*)\s*°',
            'beta': r'β\s*=\s*(\d+\.?\d*)\s*°',
            'gamma': r'γ\s*=\s*(\d+\.?\d*)\s*°'
        }

        params = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                params[key] = float(match.group(1))

        return params if params else None

    @staticmethod
    def extract_band_gap(text: str) -> Optional[float]:
        pattern = r'能隙[为是]?\s*(\d+\.?\d*)\s*eV|band\s*gap\s*[=:]\s*(\d+\.?\d*)\s*eV'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1) or match.group(2))
        return None

    @staticmethod
    def generate_poscar(formula: str, lattice_params: Dict = None) -> str:
        parsed = StructureConverter.parse_chemical_formula(formula)

        if not lattice_params:
            lattice_params = {'a': 4.2, 'b': 4.2, 'c': 4.2, 'alpha': 90, 'beta': 90, 'gamma': 90}

        poscar = f"""钙钛矿 {formula}
1.0
{lattice_params.get('a', 4.2):.6f} 0.0 0.0
0.0 {lattice_params.get('b', 4.2):.6f} 0.0
0.0 0.0 {lattice_params.get('c', 4.2):.6f}
"""

        elements = list(parsed.keys())
        counts = list(parsed.values())

        poscar += " ".join(elements) + "\n"
        poscar += " ".join(map(str, counts)) + "\n"
        poscar += "Cartesian\n"

        total_atoms = sum(counts)
        positions = StructureConverter._generate_positions(parsed, lattice_params)
        for pos in positions:
            poscar += f"{pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f}\n"

        return poscar

    @staticmethod
    def _generate_positions(composition: Dict, lattice: Dict) -> List:
        positions = []
        a, b, c = lattice.get('a', 4.2), lattice.get('b', 4.2), lattice.get('c', 4.2)

        base_positions = [
            (0.0, 0.0, 0.0),
            (0.5, 0.5, 0.0),
            (0.5, 0.0, 0.5),
            (0.0, 0.5, 0.5)
        ]

        for i, (element, count) in enumerate(composition.items()):
            for j in range(count % 4):
                if i < len(base_positions):
                    pos = base_positions[i]
                    positions.append((
                        pos[0] * a,
                        pos[1] * b,
                        pos[2] * c
                    ))

        return positions

    @staticmethod
    def extract_formula(text: str) -> Optional[str]:
        perovskite_patterns = [
            r'([A-Z][a-z]?\d*[A-Z][a-z]?\d*[A-Z][a-z]?\d*)',
            r'(Cs|Rb|K|Na|Li|MA|FA)\s*([A-Z][a-z]?)\s*([A-Z][a-z]?)\s*3',
            r'([A-Z][a-z]?[0-9]?)\s*([A-Z][a-z]?[0-9]?)\s*([IOBrClFS])\s*3',
        ]

        organic_map = {
            'MA': 'MA',
            'CH3NH3': 'MA',
            'FA': 'FA',
            'HC(NH2)2': 'FA',
        }

        for pattern in perovskite_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                formula = match.group(0)

                for organic, abbr in organic_map.items():
                    if organic in formula.upper():
                        formula = formula.upper().replace(organic.upper(), abbr)
                        break

                formula = re.sub(r'\s+', '', formula)

                if re.match(r'^[A-Z][a-z]?\d*[A-Z][a-z]?\d*[IOBrClFS]\d*$', formula):
                    return formula

        return None

    @staticmethod
    def create_structure_summary(design_text: str) -> Dict:
        summary = {
            'formula': None,
            'lattice_parameters': None,
            'predicted_band_gap': None,
            'stability': None,
            'applications': []
        }

        formula_pattern = r'([A-Z][a-z]?\d*[A-Z]?[a-z]?\d*(?:\d)*)|(?:化学式|分子式)[:：]\s*([A-Za-z0-9]+)'
        formula_match = re.search(formula_pattern, design_text)
        if formula_match:
            summary['formula'] = formula_match.group(1) or formula_match.group(2)

        summary['lattice_parameters'] = StructureConverter.extract_lattice_parameters(design_text)
        summary['predicted_band_gap'] = StructureConverter.extract_band_gap(design_text)

        if '稳定' in design_text or 'stability' in design_text.lower():
            summary['stability'] = '高'
        elif '中等' in design_text:
            summary['stability'] = '中'

        app_keywords = ['太阳能电池', '光伏', 'LED', '光电探测器', '催化']
        summary['applications'] = [kw for kw in app_keywords if kw in design_text]

        return summary
