import pandas as pd
import matplotlib.pyplot as plt
import requests
import os
import argparse

# File paths
DATA_URL = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.txt"
DATA_FILE = "data/global_temp_anomalies.csv"
PLOT_DIR = "plots"
os.makedirs(PLOT_DIR, exist_ok=True)

def download_data():
    print("Downloading latest NASA global temperature anomaly data...")
    response = requests.get(DATA_URL)
    if response.status_code != 200:
        raise Exception("Failed to download data from NASA")

    lines = response.text.splitlines()
    # Skip header lines until we find the data (starts with "Year")
    data_start = next(i for i, line in enumerate(lines) if line.strip().startswith("Year"))
    data_lines = lines[data_start:]

    # Write to CSV, replacing multiple spaces with commas
    with open(DATA_FILE, 'w') as f:
        f.write("Year,Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec,J-D,D-N,DJF,MAM,JJA,SON,Year\n")  # Correct full columns
        for line in data_lines[1:]:  # Skip header
            if not line.strip() or line.startswith("----"):
                continue
            # Clean and split: replace multiple spaces with comma
            cleaned = ','.join(line.split())
            f.write(cleaned + '\n')
    print(f"Data saved to {DATA_FILE}")

def load_and_clean_data():
    df = pd.read_csv(DATA_FILE)
    # Convert to numeric, coerce errors (some years have **** for missing)
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    # Drop rows with NaN in Year or J-D (annual mean)
    df = df.dropna(subset=['Year', 'J-D'])
    df['Year'] = df['Year'].astype(int)
    return df

def plot_anomalies(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Year'], df['J-D'], marker='o', linestyle='-', color='red', linewidth=2)
    plt.axhline(0, color='gray', linestyle='--', alpha=0.7)
    plt.title('Global Temperature Anomalies (1951-1980 Baseline)\nNASA GISS Data', fontsize=16)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Temperature Anomaly (°C)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, 'global_temp_anomalies.png'), dpi=300)
    print("Plot saved to plots/global_temp_anomalies.png")

    # Bonus: Bar chart of last 20 years
    recent = df[df['Year'] >= df['Year'].max() - 20]
    plt.figure(figsize=(12, 6))
    plt.bar(recent['Year'], recent['J-D'], color='orange')
    plt.axhline(0, color='gray', linestyle='--')
    plt.title('Recent Global Warming: Last 20 Years', fontsize=16)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Temperature Anomaly (°C)', fontsize=12)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, 'recent_warming.png'), dpi=300)
    print("Recent warming bar chart saved to plots/recent_warming.png")

def main():
    parser = argparse.ArgumentParser(description="Global Temperature Anomaly Visualizer")
    parser.add_argument('--download', action='store_true', help="Download fresh data")
    args = parser.parse_args()

    if args.download or not os.path.exists(DATA_FILE):
        download_data()

    if not os.path.exists(DATA_FILE):
        print("No data file found. Run with --download first.")
        return

    df = load_and_clean_data()
    plot_anomalies(df)
    print("\nDone! Check the 'plots/' folder for visualizations.")
    print("Feel free to share these plots to spread awareness about climate change!")

if __name__ == "__main__":
    main()
