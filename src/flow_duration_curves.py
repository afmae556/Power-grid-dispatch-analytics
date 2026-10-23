import os
import pandas as pd
import numpy as np

def calculate_flow_duration_curve(
    filepath: str,
    start_year: int = 1991,
    end_year: int = 1998,
    output_excel: str = None
) -> pd.DataFrame:
    """
    Computes characteristic flow exceedance percentiles (Qmax, Q10..Q95)
    for historical river inflow time-series.
    """
    print(f"Loading historical hydrological inflows from '{filepath}'...")
    df = pd.read_excel(filepath)
    df.columns = df.columns.astype(str).str.strip()

    col_date = [c for c in df.columns if 'FECHA' in c.upper()][0]
    col_flow = [c for c in df.columns if 'CAUDAL' in c.upper() or 'VALOR' in c.upper()][0]

    df[col_date] = pd.to_datetime(df[col_date])
    df_period = df[(df[col_date].dt.year >= start_year) & (df[col_date].dt.year <= end_year)].copy()

    exceedance_levels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95]
    years = list(range(start_year, end_year + 1))

    results = {
        'Exceedance': [f'Q{p}' if p != 0 else 'Qmax' for p in exceedance_levels]
    }

    def get_percentiles(series):
        if series.empty:
            return [np.nan] * len(exceedance_levels)
        # Exceedance: Q10 is 90th percentile
        return [np.percentile(series.dropna(), 100 - p) for p in exceedance_levels]

    for y in years:
        sub = df_period[df_period[col_date].dt.year == y][col_flow]
        results[str(y)] = get_percentiles(sub)

    results[f'{start_year}-{end_year}'] = get_percentiles(df_period[col_flow])
    fdc_table = pd.DataFrame(results)

    if output_excel:
        fdc_table.to_excel(output_excel, index=False)
        print(f"Exceedance table successfully saved to '{output_excel}'.")

    return fdc_table

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "Aportes_Historicos.xlsx")
    out_path = os.path.join(base_dir, "data", "Tabla_Caudales_Guatape.xlsx")
    table = calculate_flow_duration_curve(data_path, 1991, 1998, out_path)
    print("\n=== CHARACTERISTIC INFLOW EXCEEDANCE TABLE (m3/s) ===")
    print(table.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))
