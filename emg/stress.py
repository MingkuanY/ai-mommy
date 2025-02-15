import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, welch

def butter_bandpass(data, lowcut, highcut, fs, order=4):
    """Apply a bandpass Butterworth filter."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

def compute_median_frequency(signal, fs):
    """
    Compute the median frequency (MDF) for a given signal.
    Uses Welch’s method to estimate the power spectral density.
    """
    freqs, psd = welch(signal, fs=fs)
    cumulative_power = np.cumsum(psd)
    total_power = cumulative_power[-1]
    mdf_index = np.where(cumulative_power >= total_power / 2)[0][0]
    return freqs[mdf_index]

def compute_stress_level(mdf, mdf_min, mdf_max):
    """
    Map the median frequency to a stress level between 0 and 10.
    Lower MDF (linked to fatigue/stress) gives a higher stress score.
    """
    if mdf_max == mdf_min:
        return 0
    normalized = (mdf - mdf_min) / (mdf_max - mdf_min)
    stress = 10 * (1 - normalized)
    return stress

def process_segment(segment, fs):
    """
    Process a segment of data:
      - Filter channel 1 using a bandpass filter (0.5 - 20 Hz)
      - Compute the median frequency of the filtered signal
    """
    raw_signal = segment['ch1'].values
    filtered_signal = butter_bandpass(raw_signal, 0.5, 20, fs, order=4)
    mdf = compute_median_frequency(filtered_signal, fs)
    return mdf
def main():
    # File path for the EMG data file
    filename = "1_raw_data_13-12_22.03.16.txt"
    
    # Read the file assuming whitespace as the delimiter, skipping the header line.
    df = pd.read_csv(filename, delim_whitespace=True, skiprows=1, header=None)
    df.columns = ['time', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'class']
    
    # Convert time from milliseconds to seconds
    df['time'] = df['time'] / 1000.0

    # Use only the first fifth of the data
    df = df.iloc[:len(df) // 5].reset_index(drop=True)

    # STEP 1: Rectify the EMG signal from channel 1
    df['ch1_rect'] = df['ch1'].abs()

    # STEP 2: Smooth via a rolling mean
    # Adjust the window size to control smoothing. Larger = more smoothing.
    window_size = 800  
    df['ch1_smooth'] = df['ch1_rect'].rolling(window=window_size, center=True).mean()

    # Because of the rolling window, the first/last few points will be NaN.
    # You can fill or drop them:
    df['ch1_smooth'].fillna(method='bfill', inplace=True)
    df['ch1_smooth'].fillna(method='ffill', inplace=True)

    # STEP 3: Rescale from 0 to 10 (optional)
    # This ensures the stress level is in a 0–10 range
    min_val = df['ch1_smooth'].min()
    max_val = df['ch1_smooth'].max()
    df['stress'] = 10 * (df['ch1_smooth'] - min_val) / (max_val - min_val + 1e-9)  # +1e-9 to avoid /0

    # Plot the raw EMG (Channel 1) vs. the smoothed stress level
    fig, axs = plt.subplots(2, 1, figsize=(10,6), sharex=True)

    # Top: Downsampled/Raw EMG signal
    axs[0].plot(df['time'], df['ch1'], label='EMG (Channel 1)', color='gray')
    axs[0].set_title('Downsampled Raw EMG Signal (First 1/5 of Data)')
    axs[0].set_ylabel('EMG (a.u.)')
    axs[0].legend()

    # Bottom: Smoothed Stress Level
    axs[1].plot(df['time'], df['stress'], label='Stress Level (0–10)', color='blue')
    axs[1].set_title('Stress Level Over Time')
    axs[1].set_xlabel('Time (s)')
    axs[1].set_ylabel('Stress Level (0–10)')
    axs[1].legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()