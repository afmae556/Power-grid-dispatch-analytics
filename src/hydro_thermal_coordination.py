import os
import pandas as pd
import matplotlib.pyplot as plt

def analyze_reservoir_and_inflows(
    inflows_path: str,
    reserves_path: str,
    spills_path: str,
    output_plot: str = None
):
    """
    Evaluates historical inflows, Punchina reservoir storage volume (%),
    and spillway discharges to analyze hydro-firm energy security.
    """
    print("Loading daily hydrological and storage data...")
    df_inf = pd.read_excel(inflows_path, header=3)
    df_res = pd.read_excel(reserves_path, header=3)
    df_spl = pd.read_excel(spills_path, header=3)
    
    df_inf['Fecha'] = pd.to_datetime(df_inf['Fecha'])
    df_res['Fecha'] = pd.to_datetime(df_res['Fecha'])
    df_spl['Fecha'] = pd.to_datetime(df_spl['Fecha'])
    
    # Inflows: San Carlos & Guatape rivers
    col_inf = [c for c in df_inf.columns if 'Aportes' in str(c) and 'm3' in str(c)][0]
    sub_inf = df_inf[df_inf['Nombre Río'].str.contains('SAN CARLOS|GUATAPE', case=False, na=False)]
    daily_inf = sub_inf.groupby('Fecha')[col_inf].sum().reset_index()
    
    # Reservoir: Embalse Punchina
    col_vol = [c for c in df_res.columns if 'olumen' in str(c) and '%' in str(c)][0]
    sub_res = df_res[df_res['Nombre Embalse'].str.contains('PUNCHINA', case=False, na=False)].copy()
    sub_res = sub_res[sub_res[col_vol] > 0]
    daily_res = sub_res.groupby('Fecha')[col_vol].mean().reset_index()
    
    print("Hydrological and reservoir storage metrics successfully aggregated.")
    return daily_inf, daily_res

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    inf_p = os.path.join(base_dir, "data", "Aportes_Diario_2025.xlsx")
    res_p = os.path.join(base_dir, "data", "Reservas_Diario_2025.xlsx")
    spl_p = os.path.join(base_dir, "data", "Vertimentos_Diario_2025.xlsx")
    analyze_reservoir_and_inflows(inf_p, res_p, spl_p)
