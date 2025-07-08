# HRVneo Live Monitor 🫀📊

A real-time heart rate variability (HRV) monitor for neonatal ECG data – developed for clinical and research use in extremely preterm infants.

This tool was created and used in the study:

> **From Standard ECG to Digital Insight: Decoding Autonomic Balance and Transitions During Kangaroo Care in Extremely Preterm Infants**  
> Keller, T. et al. (2025) – under submission

---

## 🌟 What this tool does

- 📡 **Processes raw ECG data** (e.g., from standard NICU monitors)
- 🧠 **Calculates HRV parameters** in real time, including:
  - Time-domain: HR, RMSSD  
  - Frequency-domain: LF power  
  - Nonlinear: DFA α1 (fractal), SD1/SD2
- 🔥 **Live visualizations** of HRV trends (4 panels)
- 📁 **Generates output files**:
  - Chunk-wise HRV CSV summary  
  - Final PDF report including plots and parameter statistics

---

## 📂 File overview

| File | Description |
|------|-------------|
| `live_HRV_monitor_V8_GitHub.py` | Main script – real-time HRV monitor |
| `example_data.csv` | Sample RR-interval recording (for simulation/testing) |
| `requirements.txt` | Python dependencies |
| `README.md` | This file – documentation and usage instructions |

---

## ▶️ How to use

### 1. **Install dependencies**
This project uses Python ≥ 3.8.

Install required packages:
```bash
pip install -r requirements.txt
```

### 2. **Run the monitor**
Use your own ECG `.csv` file (e.g., `ID123_fast_Unknown.csv`) or the provided example:
```bash
python live_HRV_monitor_V8_GitHub.py
```

You will be asked to enter an ID (e.g., `ID007`) to label the session.  
Results will be saved in `/results_newengine/ID007/` as `.csv` and `.pdf`.

---

## 💡 Features

- Works with standard NICU ECG recordings (no special hardware needed)
- Compatible with Polar H10–derived RR recordings (with conversion)
- Outputs clean, intuitive plots and a summary PDF
- Fully written in Python using open-source libraries (e.g., NeuroKit2, matplotlib)

---

## 🧠 A note on HRV calculations and NeuroKit2

This tool builds upon the powerful open-source library [**NeuroKit2**](https://neurokit2.readthedocs.io/), which provides robust and validated implementations of HRV analysis functions. All core HRV metrics—time-domain, frequency-domain, and nonlinear—are computed using `neurokit2.hrv()` based on detected R-peaks from cleaned ECG signals.

We gratefully acknowledge the developers of NeuroKit2 for enabling advanced physiological signal processing in Python.

> Makowski, D., Pham, T., Lau, Z. J., Brammer, J. C., Lespinasse, F., Pham, H., Schölzel, C., & Chen, S. A. (2021). NeuroKit2: A Python toolbox for neurophysiological signal processing. *Behavior Research Methods*, 53(4), 1689–1696. https://doi.org/10.3758/s13428-020-01516-y

---

## 📊 Example output

<p align="center">
  <img src="example_output.png" width="600" alt="Live HRV Plot Example"/>
</p>


---

## 📄 Citation

If you use this tool in your research or clinical setting, please cite:
```bibtex
@article{keller2025hrv,
  title={Decoding Autonomic Balance in ELGANs: HRV Signatures Before, During, and After Kangaroo Care},
  author={Keller, Titus et al.},
  journal={npj Digital Medicine},
  year={2025},
  note={submitted}
}
```

---

## 🙌 Acknowledgements

This tool was developed as part of a neonatal HRV research initiative led by Dr. Titus Keller.  
We welcome clinical collaborators and data-driven minds to improve and extend this work.

---

## 📬 Contact

For questions or collaborations, please contact:

**Titus Keller, MD**  
Neonatal Intensive Care Unit  
University Hospital Cologne, Germany  
📧 titus.keller@uk-koeln.de

---

> 🛠️ _Making the invisible visible – real-time HRV for the smallest patients._
