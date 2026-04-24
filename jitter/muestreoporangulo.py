import serial
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

PORT = 'COM3'   # Cambiar
BAUD = 115200

ANGLES = [0, 30, 60, 90, 120, 150]
#ANGLES = [90, 90, 90, 90,90,90 ]
#ANGLES = [60,60,60,60,60,60 ]
#ANGLES = [120, 120, 120, 120, 120, 120 ]
#ANGLES = [45, 45, 45, 45, 45, 45]
SAMPLES = 1000

FREQ = 60
HALF_CYCLE_US = (1/(2*FREQ)) * 1e6

ser = serial.Serial(PORT, BAUD, timeout=1)

all_data = []

for ang in ANGLES:
    print(f"\nSetting angle: {ang}°")
    
    # Enviar ángulo
    ser.write(f"{ang}\n".encode())
    
    time.sleep(2)
    ser.reset_input_buffer()  # limpiar basura
    
    count = 0
    start = time.time()
    
    while count < SAMPLES:
        
        # seguridad anti-bloqueo
        if time.time() - start > 10:
            print("Timeout reached")
            break
        
        line = ser.readline().decode(errors='ignore').strip()
        
        # DEBUG (puedes comentarlo después)
        # print("RAW:", line)
        
        if "," not in line:
            continue

        try:
            t0, tf, a = map(int, line.split(","))
            delay_real = tf - t0
            delay_ideal = (a / 180) * HALF_CYCLE_US
            jitter = delay_real - delay_ideal
            
            all_data.append([a, delay_real, delay_ideal, jitter])
            
            count += 1
            
        except:
            continue

ser.close()

# =========================
# DATAFRAME
# =========================
df = pd.DataFrame(all_data, columns=[
    "angle", "delay_real", "delay_ideal", "jitter"
])

# =========================
# SUBPLOTS: SINE PER ANGLE
# =========================

angles = sorted(df["angle"].unique())
n = len(angles)

# Definir grid automático (2 columnas)
cols = 2
rows = int(np.ceil(n / cols))

fig, axes = plt.subplots(rows, cols, figsize=(10, 4*rows))
axes = axes.flatten()

FREQ = 60
t = np.linspace(0, 1/(2*FREQ), 1000)

Vp = 12 * np.sqrt(2)
sine = Vp * np.sin(2 * np.pi * FREQ * t)

for i, ang in enumerate(angles):
    
    ax = axes[i]
    subset = df[df["angle"] == ang]
    
    # Cálculos
    delay_ideal_s = (ang / 180) * (1/(2*FREQ))
    delay_real_s = subset["delay_real"].mean() / 1e6
    std_real_s = subset["delay_real"].std() / 1e6
    
    # Senoide
    ax.plot(t, sine, label="Sine wave")
    
    # Disparo ideal (VERDE)
    ax.axvline(delay_ideal_s,
               linestyle='--',
               linewidth=2,
               color='green',
               label="Ideal firing")
    
    # Disparo real (ROJO)
    ax.axvline(delay_real_s,
               linestyle='--',
               linewidth=2,
               color='red',
               label="Measured firing")
    
    # Banda de jitter
    ax.axvspan(delay_real_s - std_real_s,
               delay_real_s + std_real_s,
               alpha=0.3,
               color='red',
               label="±1σ jitter")
    
    ax.set_title(f"Angle {ang}°")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    
    # Leyenda en esquina superior derecha
    ax.legend(loc="upper right")
    
    ax.grid()

# Eliminar subplots vacíos
for j in range(i+1, len(axes)):
    fig.delaxes(axes[j])

plt.suptitle("TRIAC Firing: Ideal vs Measured with Jitter", fontsize=14)

plt.tight_layout()
plt.show()

# =========================
# STATISTICS
# =========================
stats = df.groupby("angle")["jitter"].agg(['mean', 'std', 'min', 'max'])

print("\n=== STATISTICS BY ANGLE ===")
print(stats)

# =========================
# COLOR MAP
# =========================
angles = sorted(df["angle"].unique())
colors = plt.cm.viridis(np.linspace(0, 1, len(angles)))

# =========================
# 1. HISTOGRAM
# =========================
plt.figure()

for i, ang in enumerate(angles):
    subset = df[df["angle"] == ang]
    plt.hist(subset["jitter"], bins=40, alpha=0.5,
             label=f"{ang}°", color=colors[i])

plt.title("Jitter Distribution per Angle")
plt.xlabel("Jitter (µs)")
plt.ylabel("Frequency")
plt.legend()
plt.grid()

# =========================
# 2. JITTER VS SAMPLE
# =========================
plt.figure()

for i, ang in enumerate(angles):
    subset = df[df["angle"] == ang]
    plt.plot(subset["jitter"].values,
             label=f"{ang}°",
             color=colors[i])

plt.title("Jitter vs Sample Index")
plt.xlabel("Sample")
plt.ylabel("Jitter (µs)")
plt.legend()
plt.grid()

# =========================
# 3. SINE + IDEAL vs REAL
# =========================
example_angle = angles[len(angles)//2]
subset = df[df["angle"] == example_angle]

t = np.linspace(0, 1/(2*FREQ), 1000)
Vp = 12 * np.sqrt(2)
sine = Vp * np.sin(2 * np.pi * FREQ * t)

delay_ideal_s = (example_angle / 180) * (1/(2*FREQ))
delay_real_s = subset["delay_real"].mean() / 1e6
std_real_s = subset["delay_real"].std() / 1e6

plt.figure()
plt.plot(t, sine, label="Ideal sine wave")

plt.axvline(delay_ideal_s,
            linestyle='--',
            linewidth=2,
            label="Ideal firing")

plt.axvline(delay_real_s,
            linestyle='--',
            linewidth=2,
            label="Measured firing (mean)")

plt.axvspan(delay_real_s - std_real_s,
            delay_real_s + std_real_s,
            alpha=0.3,
            label="±1σ jitter")

plt.title(f"Firing Comparison at {example_angle}°")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.legend()
plt.grid()

# =========================
# 4. JITTER VS ANGLE (MAIN)
# =========================
stats_reset = stats.reset_index()

plt.figure()
plt.errorbar(stats_reset["angle"],
             stats_reset["mean"],
             yerr=stats_reset["std"],
             capsize=5)

plt.title("Jitter vs Firing Angle")
plt.xlabel("Angle (degrees)")
plt.ylabel("Jitter (µs)")
plt.grid()

# =========================
# SHOW ALL FIGURES
# =========================
plt.show()