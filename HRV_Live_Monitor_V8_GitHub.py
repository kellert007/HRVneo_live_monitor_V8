# HRV Live Monitor V8 – GitHub-ready version
# Developed by Titus Keller (2025) – for clinical and research use
# Real-time HRV analysis and visualization from ECG data

import pandas as pd
import numpy as np
import neurokit2 as nk
import matplotlib.pyplot as plt
import time
import os
import sys
import glob
import warnings
from fpdf import FPDF
from datetime import datetime
import matplotlib.dates as mdates

warnings.filterwarnings("ignore", category=RuntimeWarning)

# === START-UP STATUS ===
print("\U0001FA7A Starting HRVneo Live Monitor (V8)...")
print("\U0001F504 Initializing...")

# === Show current working directory ===
current_dir = os.getcwd()
print(f"\U0001F4C2 Working directory: {current_dir}")

# === Search for newest *_fast_Unknown.csv file ===
pattern = "*_fast_Unknown.csv"
print(f"\U0001F50D Searching for files with pattern: {pattern}")

files = sorted(glob.glob(os.path.join(current_dir, pattern)), key=os.path.getmtime, reverse=True)

if not files:
    print("\n❌ No *_fast_Unknown.csv files found in current folder.")
    print("Please make sure at least one valid file is present.")
    print("\U0001F501 Expected pattern: e.g., ID123_fast_Unknown.csv")
    print("\U0001F4C1 Folder checked:", current_dir)
    time.sleep(10)
    sys.exit(1)

# Use most recent file (can be changed manually if needed)
input_file = files[0]
print(f"✅ Input file found: {os.path.basename(input_file)}")

# === Create results folder and define output file name ===
timestamp_now = datetime.now().strftime("%Y%m%d-%H-%M")
results_dir = os.path.join(current_dir, "results_newengine")

# === Request User ID for session labeling ===
while True:
    user_id = input("\n🆔 Please enter an ID (e.g., ID007): ").strip()
    if user_id.startswith("ID") and user_id[2:].isdigit():
        break
    print("⚠️ Invalid format. Use 'ID' followed by 3 digits (e.g., ID007).")

# Create folder for results
results_dir = os.path.join(results_dir, user_id)
os.makedirs(results_dir, exist_ok=True)
print(f"📁 Created results folder: {results_dir}")

# Final output filename
output_file = os.path.join(results_dir, f"HRVneo_live_{timestamp_now}.csv")

# === Analysis settings ===
sampling_rate = 200
chunk_size_sec = 150
chunk_points = chunk_size_sec * sampling_rate

# === Initialize live plotting ===
plt.ion()
plt.style.use('dark_background')
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 7), sharex=True)

# Parameters to track
param_list = ["HR_BPM", "HRV_RMSSD", "HRV_LF", "HRV_DFA_alpha1"]
colors = ["red", "orange", "yellowgreen", "deepskyblue"]

last_chunk_index = -1
hrv_summary = pd.DataFrame()
first_chunk_time = None
raw_time_start, raw_time_end = None, None

# === Cross-platform "press q to quit" ===
if sys.platform == 'darwin':
    import termios, tty, select
    def is_q_pressed():
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        return dr and sys.stdin.read(1) == 'q'
    tty.setcbreak(sys.stdin.fileno())
elif sys.platform.startswith('win'):
    import msvcrt
    def is_q_pressed():
        return msvcrt.kbhit() and msvcrt.getch() == b'q'
else:
    def is_q_pressed():
        return False

# === Create PDF summary report ===
def generate_pdf_report(data, plot_figure, output_file, input_file, raw_time_start, raw_time_end):
    pdf_name = output_file.replace(".csv", "_report.pdf")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    duration_min = data["Start_Time_s"].max() / 60 if "Start_Time_s" in data else 0
    chunks = data["Chunk_Index"].nunique()
    stats = data[param_list].describe().T.round(2)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="HRV Monitoring Report", ln=1, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Input File: {os.path.basename(input_file)}", ln=1)
    pdf.cell(200, 10, txt=f"Output CSV: {os.path.basename(output_file)}", ln=1)
    pdf.cell(200, 10, txt=f"PDF Created: {timestamp}", ln=1)
    pdf.cell(200, 10, txt=f"Start Time (raw): {raw_time_start.strftime('%H:%M:%S') if raw_time_start else 'N/A'}", ln=1)
    pdf.cell(200, 10, txt=f"End Time (raw): {raw_time_end.strftime('%H:%M:%S') if raw_time_end else 'N/A'}", ln=1)
    pdf.cell(200, 10, txt=f"Duration: {round(duration_min, 1)} min", ln=1)
    pdf.cell(200, 10, txt=f"Chunk Size: {chunk_size_sec} s", ln=1)
    pdf.cell(200, 10, txt=f"Total Chunks: {chunks}", ln=1)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=10)
    pdf.cell(0, 10, txt="HRV Parameter Summary:", ln=1)
    pdf.set_font("Arial", size=9)
    for param in stats.index:
        row = stats.loc[param]
        pdf.cell(0, 8, txt=f"{param}: min {row['min']}, max {row['max']}, mean {row['mean']}, median {row['50%']}, SD {row['std']}, Q1 {row['25%']}, Q3 {row['75%']}", ln=1)

    plot_path = output_file.replace(".csv", "_lastplot.png")
    plot_figure.savefig(plot_path, bbox_inches="tight", dpi=150)
    pdf.add_page()
    pdf.image(plot_path, x=10, y=20, w=190)
    pdf.output(pdf_name)
    print(f"\n📄 PDF saved: {pdf_name}")

# === Main loop ===
try:
    while True:
        if is_q_pressed():
            print("'q' pressed – exiting monitor.")
            break

        raw_data = pd.read_csv(input_file)
        ecg_column = [col for col in raw_data.columns if "ECG" in col and "LEAD" in col][0]

        if "Time" in raw_data.columns:
            raw_data["Time"] = pd.to_datetime(raw_data["Time"], format="%H:%M:%S.%f", errors="coerce")
            if not raw_data["Time"].dropna().empty:
                raw_time_start = raw_data["Time"].dropna().iloc[0]
                raw_time_end = raw_data["Time"].dropna().iloc[-1]

        total_points = len(raw_data)
        total_chunks = total_points // chunk_points

        if total_chunks <= last_chunk_index:
            print("⏳ Waiting for new data...")
            time.sleep(30)
            continue

        for chunk_index in range(last_chunk_index + 1, total_chunks):
            start_idx = chunk_index * chunk_points
            end_idx = (chunk_index + 1) * chunk_points
            chunk = raw_data.iloc[start_idx:end_idx].copy()
            chunk[ecg_column] = chunk[ecg_column] / 1000  # Convert µV to mV

            if chunk[ecg_column].isnull().any():
                chunk[ecg_column] = chunk[ecg_column].interpolate(method="linear", limit_direction="both")
                if chunk[ecg_column].isnull().any():
                    continue

            try:
                clean_ecg = nk.ecg_clean(chunk[ecg_column], sampling_rate=sampling_rate)
                peaks, info = nk.ecg_peaks(clean_ecg, sampling_rate=sampling_rate)
                rpeaks = np.where(peaks["ECG_R_Peaks"] == 1)[0]
                if len(rpeaks) < 5:
                    continue
            except Exception:
                continue

            try:
                hrv = nk.hrv(peaks=rpeaks, sampling_rate=sampling_rate)
                if "HRV_MeanNN" in hrv.columns:
                    hrv["HR_BPM"] = 60000 / hrv["HRV_MeanNN"]
                else:
                    hrv["HR_BPM"] = np.nan

                hrv.insert(0, "Chunk_Index", chunk_index)
                hrv["Start_Time_s"] = start_idx / sampling_rate

                if "Time" in raw_data.columns:
                    clock_time = raw_data["Time"].iloc[start_idx]
                    hrv["Clock_Time"] = clock_time.strftime("%H:%M") if pd.notnull(clock_time) else ""
                else:
                    hrv["Clock_Time"] = (datetime.combine(datetime.today(), datetime.min.time()) + pd.to_timedelta(hrv["Start_Time_s"], unit="s")).strftime("%H:%M")

                hrv_summary = pd.concat([hrv_summary, hrv], ignore_index=True)
                hrv_summary.to_csv(output_file, index=False)

                # === Live plot update ===
                x = pd.to_datetime(hrv_summary["Clock_Time"], format="%H:%M", errors="coerce")
                for i, param in enumerate(param_list):
                    ax = axes[i // 2][i % 2]
                    ax.clear()
                    if param in hrv_summary.columns:
                        ax.plot(x, hrv_summary[param], color=colors[i], linewidth=2)
                        ax.set_ylabel(param)
                        ax.grid(True, linestyle='--', alpha=0.3)
                        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                        ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30]))
                        ax.tick_params(axis='x', labelrotation=45)

                axes[1][0].set_xlabel("time (hh:mm)")
                axes[1][1].set_xlabel("time (hh:mm)")

                fig.suptitle("HRVneo live monitor – © 2025 Titus Keller", fontsize=14, color='white')
                display_path = os.path.basename(input_file)
                fig.text(0.5, 0.01, f"Input File: {display_path}", ha='center', fontsize=9, color='gray')

                plt.pause(0.1)
                print(f"✅ Chunk {chunk_index} processed.")

            except Exception as e:
                print(f"⚠️ Error in chunk {chunk_index}: {e}")
                continue

        last_chunk_index = total_chunks - 1
        time.sleep(30)

except KeyboardInterrupt:
    print("❗️Manual interrupt (Ctrl+C).")

finally:
    if not hrv_summary.empty:
        generate_pdf_report(hrv_summary, fig, output_file, input_file, raw_time_start, raw_time_end)
        print("✅ Final report created.")
    else:
        print("⚠️ No HRV data processed – PDF not generated.")
