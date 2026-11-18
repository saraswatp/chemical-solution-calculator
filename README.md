# Chemical Solution Preparation Calculator

A free, open-source, Python-based calculator for preparing single-element and multielement aqueous solutions.

## Features

- Calculate the mass of chemical salts required to prepare solutions.
- Select multiple elements, including Fe, Ni, Co, Gd, Nd, and others.
- Specify different target concentrations for each element in ppm (mg/L).
- Choose the final solution volume in mL.
- Select chemical salts or enter custom chemical formulas.
- Account for molecular weights and hydration.
- Generate solution preparation calculations for laboratory use.

## Example

Prepare 250 mL of an aqueous solution containing:

| Element | Target Concentration |
|---|---|
| Fe | 100 ppm |
| Ni | 100 ppm |
| Co | 100 ppm |
| Gd | 100 ppm |

The calculator determines the mass of each selected salt required to achieve the target elemental concentrations.

## Technology

- Python
- Streamlit
- Pandas

## How to Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python -m streamlit run solution_preparation_simulator.py
```

## Scientific Note

Concentrations are expressed as mg of elemental metal per liter of final solution. Calculations assume the selected salt composition is correct. Actual solution preparation must also consider reagent purity, solubility, chemical compatibility, and solution stability.

## License

MIT License.
