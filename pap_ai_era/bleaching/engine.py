import numpy as np

class Chemical:
    """
    Represents a bleaching chemical with cost and dosage constraints.
    """
    def __init__(self, name, min_dosage, max_dosage, cost):
        self.name = name
        self.min_dosage = min_dosage
        self.max_dosage = max_dosage
        self.cost = cost

    def __repr__(self):
        return f"Chemical(name='{self.name}', min={self.min_dosage}, max={self.max_dosage}, cost={self.cost})"

class BleachingStage:
    """
    Represents a single stage in the bleaching sequence (e.g., D0, EOP, D1).
    """
    def __init__(self, name, chemicals, model=None, scaler=None):
        self.name = name
        self.chemicals = [Chemical(**c) if isinstance(c, dict) else c for c in chemicals]
        self.model = model
        self.scaler = scaler # Scaler object for normalization

    def normalize_inputs(self, state, dosages):
        """
        Normalizes inputs before passing to the model.
        """
        if self.scaler:
            return self.scaler.transform(state, dosages)
        return state, dosages

    def simulate(self, incoming_state, dosages):
        """
        Simulates the effect of this stage on the pulp state.
        dosages: dict mapping chemical names to dosage values.
        """
        norm_state, norm_dosages = self.normalize_inputs(incoming_state, dosages)
        
        if self.model is None:
            # Fallback to a simple linear heuristic if no model is provided
            return self._heuristic_simulate(norm_state, norm_dosages)
        return self.model.predict(norm_state, norm_dosages)

    def _heuristic_simulate(self, state, dosages):
        """
        A simple empirical heuristic for demonstration when no AI model is loaded.
        """
        new_state = state.copy()
        
        # Example heuristics:
        # ClO2 reduces Kappa and increases Brightness
        # NaOH/H2O2/O2 in extraction stages reduce Kappa
        
        total_active_cl = dosages.get("ClO2", 0) * 2.63  # rough ClO2 to active chlorine
        h2o2 = dosages.get("H2O2", 0)
        o2 = dosages.get("O2", 0)
        naoh = dosages.get("NaOH", 0)

        # Kappa reduction
        reduction = (total_active_cl * 0.5) + (h2o2 * 0.3) + (o2 * 0.2)
        new_state["kappa"] = max(0.5, state.get("kappa", 20) - reduction)
        
        # Brightness increase
        brightness_gain = (total_active_cl * 1.2) + (h2o2 * 0.8)
        new_state["brightness"] = min(92.0, state.get("brightness", 30) + brightness_gain)
        
        # Viscosity loss
        viscosity_loss = (total_active_cl * 5) + (o2 * 10)
        new_state["viscosity"] = max(400, state.get("viscosity", 1000) - viscosity_loss)
        
        return new_state

class BleachingSequence:
    """
    Represents a full sequence of bleaching stages.
    """
    def __init__(self, stages, targets):
        self.stages = stages
        self.targets = targets

    def run_sequence(self, initial_state, dosages_per_stage):
        """
        Runs the full sequence simulation.
        dosages_per_stage: list of dicts (one per stage).
        """
        current_state = initial_state.copy()
        history = [current_state.copy()]
        total_cost = 0

        for i, stage in enumerate(self.stages):
            dosages = dosages_per_stage[i]
            current_state = stage.simulate(current_state, dosages)
            history.append(current_state.copy())
            
            # Calculate cost
            for chem in stage.chemicals:
                dose = dosages.get(chem.name, 0)
                total_cost += dose * chem.cost
        
        return {
            "final_state": current_state,
            "total_cost": total_cost,
            "history": history
        }

    def check_constraints(self, state):
        """
        Checks if the state meets the targets.
        """
        return (
            state.get("brightness", 0) >= self.targets.get("brightness", 0) and
            state.get("kappa", 100) <= self.targets.get("kappa", 100) and
            state.get("viscosity", 0) >= self.targets.get("viscosity_min", 0)
        )
