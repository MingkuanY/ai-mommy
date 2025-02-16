#!/usr/bin/env python3
import numpy as np
import torch
import torch.nn as nn

# Define the same model architecture as used during training


class LSTMClassifier(nn.Module):
    def __init__(self, input_dim=4, hidden_dim=32, num_layers=1, num_classes=4):
        super(LSTMClassifier, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.lstm = nn.LSTM(input_dim, hidden_dim,
                            num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0),
                         self.hidden_dim).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0),
                         self.hidden_dim).to(x.device)

        out, _ = self.lstm(x, (h0, c0))
        out = out[:, -1, :]
        out = self.fc(out)
        return out


# Load emotion labels mapping
try:
    emotion_labels = np.load("emotion_labels.npy", allow_pickle=True).tolist()
except Exception:
    emotion_labels = ["fear", "anger", "sadness", "normal"]

# Load the trained model
num_classes = len(emotion_labels)
model = LSTMClassifier(input_dim=4, hidden_dim=32,
                       num_layers=1, num_classes=num_classes)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.load_state_dict(torch.load(
    "lstm_emotion_model.pth", map_location=device))
model.to(device)
model.eval()


def predict_emotion(stress, bpm, blood_pressure, temperature):
    """
    Accepts 4 lists (each of length 10) representing:
    - stress
    - bpm
    - blood_pressure
    - temperature

    Returns the predicted emotion as a string.
    """
    # Validate input lengths
    if not (len(stress) == len(bpm) == len(blood_pressure) == len(temperature) == 10):
        raise ValueError("Each input list must be of length 10.")

    # Construct the feature matrix of shape (10, 4)
    sequence = np.column_stack((stress, bpm, blood_pressure, temperature))
    # Add batch dimension -> (1, 10, 4)
    sequence = np.expand_dims(sequence, axis=0)

    # Convert to torch tensor
    sequence_tensor = torch.tensor(sequence, dtype=torch.float32).to(device)

    # Make prediction
    with torch.no_grad():
        outputs = model(sequence_tensor)
        _, predicted_class = torch.max(outputs, 1)

    return emotion_labels[predicted_class.item()]


# # Example usage:
# if __name__ == "__main__":
#     # Example dummy input: (you can replace these with real data)
#     example_stress = [320 + i for i in range(10)]
#     example_bpm = [130 + i for i in range(10)]
#     example_bp = [115 + i * 0.5 for i in range(10)]
#     example_temp = [37.0 for _ in range(10)]

#     emotion = predict_emotion(
#         example_stress, example_bpm, example_bp, example_temp)
#     print("Predicted emotion:", emotion)
