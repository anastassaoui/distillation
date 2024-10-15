import streamlit as st
import numpy as np
import scipy.optimize as opt
import pandas as pd

st.set_page_config(page_title="UNIT OPERATIONS ARE COOL", layout="wide")

tailwind_cdn = """
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
        <style>
            /* Center the table header and cell content */
            .css-1q8dd3e.e1ewe7hr3 th, .css-1q8dd3e.e1ewe7hr3 td {
                text-align: center !important;
            }
        </style>
    """
st.markdown(tailwind_cdn, unsafe_allow_html=True)
    
st.markdown("""

<h1 class="text-3xl  text-center font-extrabold mt-10 md:text-7xl
            cursor-pointer md:text-7xl md:font-extrabold
            mb-10 hover:text-red-400 duration-1000 md:mt-20
            ">
             Pressure 
            <span class="bg-red-100 text-red-600 md:text-6xl mt-2 text-3xl font-extrabold me-2 px-2.5 py-0.5 rounded dark:bg-red-400 dark:text-red-800 ms-2
            hover:scale-125">
                Estimation!
            </span>
</h1
""", unsafe_allow_html=True)








# Inputs
t_v = st.slider("Température de vaporisation (°C)", 0.0, 100.0, 50.0)
x1 = st.slider("Fraction molaire du composant 1 (x1)", 0.0, 1.0, 0.5)
x2 = 1.0 - x1  

# Antoine equation function
def antoine_p_sat(A, B, C, T):
    """Returns the saturation pressure (in bar) using Antoine equation parameters (in mmHg) and converts to bar."""
    return (10 ** (A - (B / (T + C)))) / 760 

# Ki and yi functions
def calc_ki(p_sat, p):
    """Calculates the Ki ratio for component i (ki = p_sat / p)."""
    return p_sat / p

def calc_yi(ki, xi):
    """Calculates the vapor-phase mole fraction yi for component i."""
    return ki * xi


def vaporization_pressure(t_v, x1, x2):

    def objective(p):

        A1, B1, C1 = 8.07131, 1730.63, 233.426  # water
        A2, B2, C2 = 7.24677, 1590.84, 219.16   # ethanol

        p_sat1 = antoine_p_sat(A1, B1, C1, t_v)
        p_sat2 = antoine_p_sat(A2, B2, C2, t_v)

        ki1 = calc_ki(p_sat1, p)
        ki2 = calc_ki(p_sat2, p)

        y1 = calc_yi(ki1, x1)
        y2 = calc_yi(ki2, x2)

        return (y1 + y2) - 1
    

    A1, B1, C1 = 8.07131, 1730.63, 233.426  # water
    A2, B2, C2 = 7.24677, 1590.84, 219.16   # ethanol

    p_sat1 = antoine_p_sat(A1, B1, C1, t_v)
    p_sat2 = antoine_p_sat(A2, B2, C2, t_v)

    # Physically meaningful bounds
    p_min = min(p_sat1, p_sat2)  # Lower saturation pressure
    p_max = p_sat1 * x1 + p_sat2 * x2  # Raoult'supper bound
    
    p_sol = opt.root_scalar(objective, bracket=[p_min, p_max], method='bisect')
    

    return {
        'p_vap': p_sol.root,
        'p_min': p_min,
        'p_max': p_max,
        'p_sat1': p_sat1,
        'p_sat2': p_sat2,
        'x1': x1,
        'x2': x2,
        't_v': t_v
    }

# Call the function and store the results
results = vaporization_pressure(t_v, x1, x2)

# Create a DataFrame with the results
df_results = pd.DataFrame({
    'Température de vaporisation (°C)': [f"{results['t_v']:.2f}"],
    'Fraction molaire du composant 1 (x1)': [f"{results['x1']:.2f}"],
    'Fraction molaire du composant 2 (x2)': [f"{results['x2']:.2f}"],
    'Pression de saturation du composant 1 (eau) (bar)': [f"{results['p_sat1']:.4f}"],
    'Pression de saturation du composant 2 (éthanol) (bar)': [f"{results['p_sat2']:.4f}"],
    'Limite inférieure de la pression (p_min) (bar)': [f"{results['p_min']:.4f}"],
    'Limite supérieure de la pression (p_max) (bar)': [f"{results['p_max']:.4f}"],
    'Pression de vaporisation estimée (bar)': [f"{results['p_vap']:.4f}"]
})

# Transpose the DataFrame so the variables are displayed as columns
df_results_transposed = df_results.T

# Display the transposed DataFrame
st.subheader("Tableau des résultats")
st.dataframe(df_results_transposed)
