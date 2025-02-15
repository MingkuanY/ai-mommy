import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, welch

def butter_bandpass(data, lowcut, highcut, fs, order=4):
    """Apply a Butterworth bandpass filter."""
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
    filename = "history.txt"
    
    # Read the file assuming whitespace as the delimiter, skipping the header line.
    df = pd.read_csv(filename, delim_whitespace=True, skiprows=1, header=None)
    df.columns = ['time', 'ch1']
    
    # Convert time from milliseconds to seconds
    df['time'] = df['time'] / 1000.0

    # Use only the first fifth of the data
    df = df.iloc[:len(df) // 5].reset_index(drop=True)
    
    # Calculate the sampling frequency from the time vector
    fs = 1 / (df['time'].iloc[1] - df['time'].iloc[0])
    
    ###############################
    # Original Stress Computation #
    ###############################
    # Step 1: Rectify the raw EMG signal (Channel 1)
    df['ch1_rect'] = df['ch1'].abs()

    # Step 2: Smooth the rectified signal with a rolling average
    window_size = 800  # Adjust the window size as needed
    df['ch1_smooth'] = df['ch1_rect'].rolling(window=window_size, center=True).mean()
    df['ch1_smooth'].fillna(method='bfill', inplace=True)
    df['ch1_smooth'].fillna(method='ffill', inplace=True)

    # Step 3: Rescale the smoothed signal to a stress level between 0 and 10
    min_val = df['ch1_smooth'].min()
    max_val = df['ch1_smooth'].max()
    df['stress'] = 10 * (df['ch1_smooth'] - min_val) / (max_val - min_val + 1e-9)

    ###########################################
    # Low-Frequency Filtering Integration     #
    # (Based on study findings on EMG stress) #
    ###########################################
    # Apply a bandpass filter for the low-frequency range (0.5–4 Hz)
    # which has been shown to improve stress detection.
    df['ch1_low'] = butter_bandpass(df['ch1'].values, 0.5, 4, fs, order=4)
    
    # Rectify the low-frequency filtered signal
    df['ch1_low_rect'] = np.abs(df['ch1_low'])
    
    # Smooth the rectified low-frequency signal using the same rolling average
    df['ch1_low_smooth'] = pd.Series(df['ch1_low_rect']).rolling(window=window_size, center=True).mean()
    df['ch1_low_smooth'].fillna(method='bfill', inplace=True)
    df['ch1_low_smooth'].fillna(method='ffill', inplace=True)
    
    # Rescale the low-frequency smoothed signal to a stress level between 0 and 10
    min_val_low = df['ch1_low_smooth'].min()
    max_val_low = df['ch1_low_smooth'].max()
    df['stress_low'] = 10 * (df['ch1_low_smooth'] - min_val_low) / (max_val_low - min_val_low + 1e-9)

    ####################
    # Plotting Results #
    ####################
    fig, axs = plt.subplots(3, 1, figsize=(10,8), sharex=True)

    # Plot 1: Raw EMG signal (Channel 1)
    axs[0].plot(df['time'], df['ch1'], label='EMG (Channel 1)', color='gray')
    axs[0].set_title('Downsampled Raw EMG Signal (First 1/5 of Data)')
    axs[0].set_ylabel('EMG (a.u.)')
    axs[0].legend()

    # Plot 2: Stress level computed from the original method (rectification + smoothing)
    axs[1].plot(df['time'], df['stress'], label='Stress Level (Original)', color='blue')
    axs[1].set_title('Stress Level (Original Computation)')
    axs[1].set_ylabel('Stress Level (0–10)')
    axs[1].legend()

    # Plot 3: Stress level computed from the low-frequency (0.5–4 Hz) filtered signal
    axs[2].plot(df['time'], df['stress_low'], label='Stress Level (Low-Frequency)', color='green')
    axs[2].set_title('Stress Level (Low-Frequency Filtered: 0.5–4 Hz)')
    axs[2].set_xlabel('Time (s)')
    axs[2].set_ylabel('Stress Level (0–10)')
    axs[2].legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
