#!/usr/bin/env python3
import numpy as np


def generate_sequence(emotion, timesteps=10):
    """
    Generate a single sample time series (timesteps x 4 features) based on emotion.

    Features order: [stress, bpm, blood_pressure, body_temperature]
    """
    sequence = np.zeros((timesteps, 4))

    if emotion == "fear":
        # High stress and high bpm; other features are in normal range.
        # Stress: 300-500, BPM: 120-150, Blood pressure: 110-130, Temperature: 36.5-37.5
        stress = np.random.uniform(300, 500, timesteps)
        bpm = np.random.uniform(120, 150, timesteps)
        bp = np.random.uniform(110, 130, timesteps)
        temp = np.random.uniform(36.5, 37.5, timesteps)

    elif emotion == "anger":
        # High blood pressure; others in normal range.
        # Stress: 0-300, BPM: 60-100, BP: 140-180, Temperature: 36.5-37.5
        stress = np.random.uniform(0, 300, timesteps)
        bpm = np.random.uniform(60, 100, timesteps)
        bp = np.random.uniform(140, 180, timesteps)
        temp = np.random.uniform(36.5, 37.5, timesteps)

    elif emotion == "sadness":
        # High stress, low bpm; others in normal range.
        # Stress: 300-500, BPM: 40-60, BP: 110-130, Temperature: 36.5-37.5
        stress = np.random.uniform(300, 500, timesteps)
        bpm = np.random.uniform(40, 60, timesteps)
        bp = np.random.uniform(110, 130, timesteps)
        temp = np.random.uniform(36.5, 37.5, timesteps)

    elif emotion in ["normal", "chill"]:
        # All features in normal ranges.
        # Stress: 0-300, BPM: 60-100, BP: 110-130, Temperature: 36.5-37.5
        stress = np.random.uniform(0, 300, timesteps)
        bpm = np.random.uniform(60, 100, timesteps)
        bp = np.random.uniform(110, 130, timesteps)
        temp = np.random.uniform(36.5, 37.5, timesteps)

    else:
        raise ValueError("Unknown emotion")

    # Optionally add some random noise to each signal
    stress += np.random.normal(0, 5, timesteps)
    bpm += np.random.normal(0, 2, timesteps)
    bp += np.random.normal(0, 2, timesteps)
    temp += np.random.normal(0, 0.1, timesteps)

    sequence[:, 0] = stress
    sequence[:, 1] = bpm
    sequence[:, 2] = bp
    sequence[:, 3] = temp

    return sequence


def generate_dataset(num_samples_per_class=250, timesteps=10):
    # treat "chill" same as "normal"
    emotions = ["fear", "anger", "sadness", "normal"]
    X = []
    y = []
    for idx, emotion in enumerate(emotions):
        for _ in range(num_samples_per_class):
            seq = generate_sequence(emotion, timesteps)
            X.append(seq)
            y.append(idx)  # numeric label
    X = np.array(X)  # shape: (num_samples, timesteps, features)
    y = np.array(y)  # shape: (num_samples,)

    # Shuffle the dataset
    indices = np.arange(len(X))
    np.random.shuffle(indices)
    X = X[indices]
    y = y[indices]

    return X, y, emotions


if __name__ == "__main__":
    # Generate dataset (e.g., 250 samples per emotion -> 1000 samples total)
    X, y, emotion_labels = generate_dataset(
        num_samples_per_class=250, timesteps=10)
    print(f"Generated dataset with shape: {X.shape}, labels shape: {y.shape}")

    # Save the dataset and label mapping (emotion_labels) into a file
    np.savez("synthetic_emotion_data.npz", X=X, y=y,
             emotion_labels=np.array(emotion_labels))
    print("Data saved to synthetic_emotion_data.npz")
