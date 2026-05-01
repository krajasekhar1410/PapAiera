import numpy as np
import pandas as pd
try:
    from sklearn.ensemble import RandomForestRegressor
except ImportError:
    RandomForestRegressor = None

class BulkModel:
    """
    ML-based model to predict Paper/Board Bulk (cm3/g) based on 
    multi-layer furnish and process conditions.
    """
    def __init__(self, n_layers=3):
        self.n_layers = n_layers
        self.model = RandomForestRegressor(n_estimators=100, random_state=42) if RandomForestRegressor else None
        self._is_trained = False

    def flatten_layer_data(self, layers_info, process_info):
        """
        Converts nested layer dictionaries into a flat feature vector.
        """
        features = {}
        for i in range(self.n_layers):
            prefix = f"L{i+1}_"
            info = layers_info[i] if i < len(layers_info) else {}
            features[prefix + "gsm"] = info.get("gsm", 0)
            features[prefix + "sw_ratio"] = info.get("sw_ratio", 0)
            features[prefix + "hw_ratio"] = info.get("hw_ratio", 0)
            features[prefix + "csf"] = info.get("csf", 500)
            features[prefix + "fines"] = info.get("fines", 10)
            features[prefix + "ash"] = info.get("ash", 0)

        features["nip_load"] = process_info.get("nip_load", 50)
        features["n_nips"] = process_info.get("n_nips", 2)
        features["moisture"] = process_info.get("moisture", 7)
        
        return features

    def train(self, df_data):
        """
        Trains the model on historical mill/lab data.
        df_data: Pandas DataFrame with flattened features and a 'bulk' column.
        """
        if self.model is None:
            raise ImportError("scikit-learn is required for training.")
        
        X = df_data.drop(columns=["bulk"])
        y = df_data["bulk"]
        self.model.fit(X, y)
        self._is_trained = True

    def predict(self, layers_info, process_info):
        """
        Predicts bulk using the trained model or a heuristic fallback.
        """
        flat_features = self.flatten_layer_data(layers_info, process_info)
        
        if self._is_trained:
            X_input = pd.DataFrame([flat_features])
            return self.model.predict(X_input)[0]
        
        return self._heuristic_predict(layers_info, process_info)

    def _heuristic_predict(self, layers_info, process_info):
        """
        Physics-aware heuristic for bulk prediction.
        Bulk decreases with: Refining (CSF low), Pressing (Nip high), Ash.
        Bulk increases with: SW fiber, low pressing.
        """
        total_gsm = sum(l.get("gsm", 0) for l in layers_info)
        if total_gsm == 0: return 0.0
        
        weighted_bulk_sum = 0
        for l in layers_info:
            # Base bulk for pulp types (approximate)
            # SW: 1.8, HW: 1.4, Recycled: 1.3
            base = (l.get("sw_ratio", 0) * 1.8 + l.get("hw_ratio", 0) * 1.4 + 
                    (1 - l.get("sw_ratio", 0) - l.get("hw_ratio", 0)) * 1.3)
            
            # CSF effect (Refining reduces bulk)
            csf_factor = 0.8 + (l.get("csf", 500) / 1000.0) * 0.4
            
            # Ash effect (Fillers reduce bulk)
            ash_factor = 1.0 - (l.get("ash", 0) / 100.0) * 0.5
            
            layer_bulk = base * csf_factor * ash_factor
            weighted_bulk_sum += layer_bulk * (l.get("gsm", 0) / total_gsm)

        # Press effect (Nip load compresses the sheet)
        # Power law relationship: Bulk ~ Nip^-k
        nip_factor = 1.0 - (process_info.get("nip_load", 50) / 1000.0) * 0.3
        n_nips = process_info.get("n_nips", 2)
        final_bulk = weighted_bulk_sum * (nip_factor ** n_nips)
        
        return max(0.8, final_bulk)
