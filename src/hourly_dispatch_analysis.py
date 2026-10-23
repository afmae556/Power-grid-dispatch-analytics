import os
import pandas as pd
import matplotlib.pyplot as plt

def analyze_generation_dispatch(
    data_path: str,
    installed_capacity_mw: float = 1240.0,
    export_plots: bool = False,
    plots_dir: str = None
):
    """
    Analyzes hourly generation dispatch, converts kWh to MW,
    and computes annual energy yield (MWh) and Plant Capacity Factor (%).
    """
    print(f"Loading dispatch data from '{data_path}'...")
    df_raw = pd.read_excel(data_path)
    
    # Identify hour columns (0..23 or 1..24)
    hour_cols = [c for c in df_raw.columns if str(c).isdigit()]
    
    df_melt = pd.melt(
        df_raw,
        id_vars=['Fecha'],
        value_vars=hour_cols,
        var_name='Hora',
        value_name='Generacion_kWh'
    )
    
    df_melt['Fecha'] = pd.to_datetime(df_melt['Fecha']).dt.normalize()
    df_melt['Hora'] = df_melt['Hora'].astype(int) + 1
    df_melt['Generacion_MW'] = df_melt['Generacion_kWh'] / 1000.0
    
    df_hourly = df_melt.groupby(['Fecha', 'Hora'])['Generacion_MW'].sum().reset_index()
    
    total_energy_mwh = df_hourly['Generacion_MW'].sum()
    theoretical_max_mwh = installed_capacity_mw * 24 * 365
    capacity_factor_pct = (total_energy_mwh / theoretical_max_mwh) * 100.0
    
    print("\n" + "=" * 60)
    print(" CENTRAL SAN CARLOS (1,240 MW) - DISPATCH PERFORMANCE")
    print("=" * 60)
    print(f"Total Annual Generation : {total_energy_mwh:,.2f} MWh")
    print(f"Theoretical Max Energy  : {theoretical_max_mwh:,.2f} MWh")
    print(f"Plant Capacity Factor   : {capacity_factor_pct:.2f}%")
    print("=" * 60)
    
    if export_plots and plots_dir:
        os.makedirs(plots_dir, exist_ok=True)
        unique_dates = df_hourly['Fecha'].unique()[:5]  # Sample 5 days for showcase
        print(f"Generating sample dispatch plots in '{plots_dir}'...")
        for dt in unique_dates:
            sub = df_hourly[df_hourly['Fecha'] == dt].sort_values('Hora')
            dt_str = pd.to_datetime(dt).strftime('%Y-%m-%d')
            plt.figure(figsize=(8, 4))
            plt.plot(sub['Hora'], sub['Generacion_MW'], color='teal', lw=2)
            plt.title(f'San Carlos Hydro Dispatch - {dt_str}')
            plt.xlabel('Hour of Day')
            plt.ylabel('Power Output [MW]')
            plt.ylim(0, installed_capacity_mw + 100)
            plt.xticks(range(1, 25))
            plt.grid(True, alpha=0.4)
            plt.tight_layout()
            plt.savefig(os.path.join(plots_dir, f"Dispatch_{dt_str}.png"))
            plt.close()
            
    return df_hourly, total_energy_mwh, capacity_factor_pct

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "Generacion_San_Carlos_2025.xlsx")
    analyze_generation_dispatch(file_path, installed_capacity_mw=1240.0)
