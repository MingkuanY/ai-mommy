import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

def butter_bandpass(data, lowcut, highcut, fs, order=4):
    """
    Apply a Butterworth bandpass filter with zero-phase filtering.
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

def read_emg_data(filename):
    """
    Reads EMG data from a file and returns a DataFrame with columns 'time' and 'ch1'.
    
    Assumes the file uses whitespace as the delimiter, has a header row to skip, 
    and that the time column is in milliseconds.
    """
    df = pd.read_csv(filename, sep='\s+', skiprows=1, header=None)
    df.columns = ['time', 'ch1']
    # Convert time from milliseconds to seconds
    df['time'] = df['time'] / 1000.0
    return df

def preprocess_data(df, fraction=0.2):
    """
    Preprocess the DataFrame by selecting only the first fraction of the data.
    
    Parameters:
      df: DataFrame containing the EMG data.
      fraction: Fraction of the data to retain (e.g., 0.2 for the first 20%).
      
    Returns:
      Preprocessed DataFrame.
    """
    num_samples = len(df)
    df = df.iloc[: int(num_samples * fraction)].reset_index(drop=True)
    return df

def compute_sampling_frequency(df):
    """
    Compute the sampling frequency from the DataFrame's 'time' column.
    
    Returns:
      fs: Sampling frequency in Hz.
    """
    return 1 / (df['time'].iloc[1] - df['time'].iloc[0])

def compute_stress_data(df, fs, downsample_factor=100, smoothing_span=3000):
    """
    Compute low-frequency stress data from an EMG signal.
    
    Processing steps:
      1. Bandpass filter the raw EMG (0.5 - 4 Hz) to isolate slow components.
      2. Rectify the filtered signal to obtain its absolute value.
      3. Smooth the rectified signal using an exponential weighted moving average.
      4. Rescale the smoothed signal to a 0- 10 stress level.
      5. Downsample the resulting time and stress data.
    
    Parameters:
      df: DataFrame containing at least 'time' and 'ch1'.
      fs: Sampling frequency (Hz).
      downsample_factor: Factor by which to downsample the data for plotting.
      smoothing_span: Span for the exponential moving average smoother.
      
    Returns:
      List of (time, stress) tuples.
    """
    # 1. Bandpass filter (0.5 - 4 Hz)
    ch1_low = butter_bandpass(df['ch1'].values, lowcut=0.5, highcut=4, fs=fs, order=4)
    
    # 2. Rectify the signal
    ch1_low_rect = np.abs(ch1_low)
    
    # 3. Smooth the rectified signal using an exponential weighted moving average
    ch1_low_smooth = pd.Series(ch1_low_rect).ewm(span=smoothing_span, adjust=False).mean()
    ch1_low_smooth.ffill(inplace=True)
    ch1_low_smooth.bfill(inplace=True)
    
    # 4. Rescale the signal to a 0 - 10 range
    min_val = ch1_low_smooth.min()
    max_val = ch1_low_smooth.max()
    stress_low = 10 * (ch1_low_smooth - min_val) / (max_val - min_val + 1e-9)
    
    # 5. Downsample the time and stress data for smoother plotting
    time_down = df['time'].values[::downsample_factor]
    stress_down = stress_low.values[::downsample_factor]
    
    return list(zip(time_down, stress_down))

def compute_stress_data_from_file(filename):
    df = read_emg_data(filename)
    df = preprocess_data(df, fraction=0.2)
    fs = compute_sampling_frequency(df)
    np_data = compute_stress_data(df, fs, downsample_factor=100, smoothing_span=3000)
    # turn into python list
    data = list(np_data)
    return data

def main():
    filename = "sample_history.txt"
    stress_data = compute_stress_data_from_file(filename)
    
    # Unzip the list of (time, stress) tuples for plotting
    times, stresses = zip(*stress_data)
    
    # Plot the computed low-frequency stress data
    plt.figure(figsize=(10, 6))
    plt.plot(times, stresses, label="Low-Frequency Stress", color="green")
    plt.xlabel("Time (s)")
    plt.ylabel("Stress Level (0 - 10)")
    plt.title("Low-Frequency Stress Data")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
