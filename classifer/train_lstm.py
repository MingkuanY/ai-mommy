#!/usr/bin/env python3
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from sklearn.model_selection import train_test_split

# Hyperparameters
NUM_EPOCHS = 15
BATCH_SIZE = 32
LEARNING_RATE = 0.001

# Custom Dataset for our synthetic data


class EmotionDataset(Dataset):
    def __init__(self, X, y):
        """
        X: numpy array of shape (num_samples, timesteps, features)
        y: numpy array of shape (num_samples,)
        """
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# Define the LSTM classifier


class LSTMClassifier(nn.Module):
    def __init__(self, input_dim=4, hidden_dim=32, num_layers=1, num_classes=4):
        super(LSTMClassifier, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.lstm = nn.LSTM(input_dim, hidden_dim,
                            num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        # x shape: (batch, seq_len, input_dim)
        # Set initial hidden and cell states
        h0 = torch.zeros(self.num_layers, x.size(0),
                         self.hidden_dim).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0),
                         self.hidden_dim).to(x.device)

        out, _ = self.lstm(x, (h0, c0))
        # out: tensor of shape (batch, seq_len, hidden_dim)
        # Use the last time-step's output
        out = out[:, -1, :]
        out = self.fc(out)
        return out


def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs, device):
    model.to(device)
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        train_correct = 0
        total_train = 0

        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)

            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * X_batch.size(0)
            _, preds = torch.max(outputs, 1)
            train_correct += (preds == y_batch).sum().item()
            total_train += X_batch.size(0)

        model.eval()
        val_loss = 0.0
        val_correct = 0
        total_val = 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                val_loss += loss.item() * X_batch.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == y_batch).sum().item()
                total_val += X_batch.size(0)

        print(f"Epoch [{epoch+1}/{num_epochs}], "
              f"Train Loss: {train_loss/total_train:.4f}, Train Acc: {train_correct/total_train:.4f}, "
              f"Val Loss: {val_loss/total_val:.4f}, Val Acc: {val_correct/total_val:.4f}")


if __name__ == "__main__":
    # Load data
    data = np.load("synthetic_emotion_data.npz", allow_pickle=True)
    X = data["X"]  # shape: (num_samples, timesteps, features)
    y = data["y"]  # shape: (num_samples,)
    emotion_labels = data["emotion_labels"].tolist()
    num_classes = len(emotion_labels)

    # Split into training and validation sets using sklearn's train_test_split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42)

    train_dataset = EmotionDataset(X_train, y_train)
    val_dataset = EmotionDataset(X_val, y_val)

    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # Create the model, loss function, and optimizer
    model = LSTMClassifier(input_dim=4, hidden_dim=32,
                           num_layers=1, num_classes=num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Check if CUDA is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Training on device:", device)

    # Train the model
    train_model(model, train_loader, val_loader,
                criterion, optimizer, NUM_EPOCHS, device)

    # Save the trained model and emotion labels mapping
    torch.save(model.state_dict(), "lstm_emotion_model.pth")
    np.save("emotion_labels.npy", np.array(emotion_labels))
    print("Model saved to lstm_emotion_model.pth and emotion_labels saved to emotion_labels.npy")
