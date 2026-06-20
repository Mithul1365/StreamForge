import torch
import torch.nn as nn
import numpy as np
import json
import random

# ============================================
# STEP 1: Generate training data (NORMAL patients)
# ============================================
def generate_normal_training_data(num_samples=500):
    data = []
    for _ in range(num_samples):
        sample = [
            random.uniform(60, 100),    # heart_rate
            random.uniform(95, 100),    # spo2
            random.uniform(110, 130),   # bp_systolic
            random.uniform(97.0, 99.0)  # temperature
        ]
        data.append(sample)
    return np.array(data, dtype=np.float32)

# ============================================
# STEP 2: Build the LSTM Autoencoder model
# ============================================
class LSTMAutoencoder(nn.Module):
    def __init__(self, input_size=4, hidden_size=8):
        super(LSTMAutoencoder, self).__init__()
        # Encoder - compresses the data
        self.encoder = nn.LSTM(input_size, hidden_size, batch_first=True)
        # Decoder - reconstructs back to original size
        self.decoder = nn.LSTM(hidden_size, input_size, batch_first=True)

    def forward(self, x):
        encoded, _ = self.encoder(x)
        decoded, _ = self.decoder(encoded)
        return decoded

# ============================================
# STEP 3: Train the model
# ============================================
def train_model():
    print("Generating training data...")
    training_data = generate_normal_training_data(500)

    # Normalize the data
    mean = training_data.mean(axis=0)
    std = training_data.std(axis=0)
    normalized_data = (training_data - mean) / std

    # LSTM expects shape: (batch, sequence_length, features)
    tensor_data = torch.tensor(normalized_data).unsqueeze(1)

    model = LSTMAutoencoder(input_size=4, hidden_size=8)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    print("Training the model...")
    epochs = 100
    for epoch in range(epochs):
        optimizer.zero_grad()
        output = model(tensor_data)
        loss = criterion(output, tensor_data)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 20 == 0:
            print(f"   Epoch {epoch+1}/{epochs} - Loss: {loss.item():.4f}")

    print("Model training complete!\n")
    return model, mean, std

# ============================================
# STEP 4: Check for anomaly
# ============================================
def check_anomaly(model, mean, std, patient_data, threshold=1.5):
    sample = np.array([
        patient_data['heart_rate'],
        patient_data['spo2'],
        patient_data['bp_systolic'],
        patient_data['temperature']
    ], dtype=np.float32)

    normalized = (sample - mean) / std
    tensor_input = torch.tensor(normalized).unsqueeze(0).unsqueeze(1)

    model.eval()
    with torch.no_grad():
        reconstructed = model(tensor_input)
        error = torch.mean((tensor_input - reconstructed) ** 2).item()

    is_anomaly = error > threshold
    return is_anomaly, error

# ============================================
# MAIN - Test the model
# ============================================
if __name__ == "__main__":
    model, mean, std = train_model()

    test_patients = [
        {"patient_id": "P001", "heart_rate": 75, "spo2": 98, "bp_systolic": 120, "temperature": 98.2},
        {"patient_id": "P002", "heart_rate": 145, "spo2": 82, "bp_systolic": 180, "temperature": 103.5},
        {"patient_id": "P003", "heart_rate": 80, "spo2": 97, "bp_systolic": 125, "temperature": 98.6},
    ]

    print("Checking test patients:\n")
    for patient in test_patients:
        is_anomaly, error = check_anomaly(model, mean, std, patient)
        status = "ANOMALY" if is_anomaly else "NORMAL"
        print(f"{status} - {patient['patient_id']}: HR={patient['heart_rate']}, SpO2={patient['spo2']}, Error={error:.4f}")