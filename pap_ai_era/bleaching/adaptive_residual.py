import numpy as np

class AdaptiveResidualOptimizer:
    """
    Optimizes chemical dosage based on Brightness and Residual signals 
    using the 'Optimum Line' concept and Golden Section Search.
    Eliminates dependency on expensive Kappa Analyzers.
    """
    def __init__(self, target_brightness, target_residual, coefficients=None):
        self.target_b = target_brightness
        self.target_r = target_residual
        
        # Coefficients for the Optimum Line: a*b + b*r + c = 0
        # Default coefficients based on typical mill empirical data
        self.coeffs = coefficients or {
            "a": 1.2,
            "b": 0.8,
            "c": -100.0 # Example: 1.2*b + 0.8*r - 100 = 0
        }

    def optimum_function(self, b, r):
        """
        f(b, r) = a*b + b*r + c
        f > 0: Overcharged
        f < 0: Undercharged
        """
        return self.coeffs["a"] * b + self.coeffs["b"] * r + self.coeffs["c"]

    def objective_function(self, current_b, current_r):
        """
        Minimize z = (b - b_opt)^2 + (r - r_opt)^2
        """
        return (current_b - self.target_b)**2 + (current_r - self.target_r)**2

    def golden_section_search(self, simulate_fn, q_low, q_high, tol=1e-3):
        """
        Golden Section Search to find optimal dosage Q.
        simulate_fn: function that takes Q and returns (b, r)
        """
        inv_phi = (np.sqrt(5) - 1) / 2 # ~0.618
        inv_phi2 = (3 - np.sqrt(5)) / 2 # ~0.382
        
        a, b = q_low, q_high
        h = b - a
        if h <= tol:
            return (a + b) / 2

        # Required number of iterations to reach tolerance
        n = int(np.ceil(np.log(tol / h) / np.log(inv_phi)))

        c = a + inv_phi2 * h
        d = a + inv_phi * h
        
        # Initial simulations
        b_c, r_c = simulate_fn(c)
        yc = self.objective_function(b_c, r_c)
        
        b_d, r_d = simulate_fn(d)
        yd = self.objective_function(b_d, r_d)

        for i in range(n):
            # print(f"GSS Iteration {i}: a={a:.4f}, b={b:.4f}, h={h:.4f}")
            if yc < yd:
                b = d
                d = c
                yd = yc
                h = b - a
                c = a + inv_phi2 * h
                b_c, r_c = simulate_fn(c)
                yc = self.objective_function(b_c, r_c)
            else:
                a = c
                c = d
                yc = yd
                h = b - a
                d = a + inv_phi * h
                b_d, r_d = simulate_fn(d)
                yd = self.objective_function(b_d, r_d)

        return (a + b) / 2

    def optimize(self, current_b, current_r, simulate_fn, q_range=(5, 40), current_q=None, max_delta=5.0):
        """
        Determines the state and calculates the optimal chemical dosage.
        Includes industrial logic: deadband, safety limits, and rate-of-change limits.
        """
        f_val = self.optimum_function(current_b, current_r)
        
        # Deadband logic (Industrial ε)
        epsilon = 1.0 
        if abs(f_val) < epsilon:
            status = "Optimal (Within Deadband)"
            if current_q is not None:
                return {
                    "status": status,
                    "f_value": f_val,
                    "optimal_dosage": current_q, # Hold current
                    "action": "Hold"
                }
        
        if f_val > epsilon:
            status = "Overcharged"
            action = "Decrease Dosage"
        elif f_val < -epsilon:
            status = "Undercharged"
            action = "Increase Dosage"
        else:
            status = "Optimal"
            action = "Hold"

        # Calculate theoretical optimum
        target_q = self.golden_section_search(simulate_fn, q_range[0], q_range[1])
        
        # Rate-of-change limits (Safety)
        if current_q is not None:
            delta = target_q - current_q
            if abs(delta) > max_delta:
                target_q = current_q + np.sign(delta) * max_delta
                status += f" (Rate-limited, Target: {current_q + delta:.2f})"

        return {
            "status": status,
            "action": action,
            "f_value": f_val,
            "optimal_dosage": target_q,
            "target_brightness": self.target_b,
            "target_residual": self.target_r
        }

class BleachingSimulator:
    """
    Simplified process model simulator: b = G1(K, Q), r = G2(K, Q)
    Used for testing the optimizer.
    """
    def __init__(self, kappa):
        self.kappa = kappa

    def simulate(self, q):
        """
        Empirical relationships:
        Brightness increases with Q, but saturates.
        Residual increases with Q, especially after saturation.
        """
        # Example linear/saturation models
        brightness = 30 + (self.kappa * 0.5) + (q * 1.5) - (q**2 * 0.01)
        residual = max(0, (q - (self.kappa * 0.8)) * 2.0)
        
        return brightness, residual
