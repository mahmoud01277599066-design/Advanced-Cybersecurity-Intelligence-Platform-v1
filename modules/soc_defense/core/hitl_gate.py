import json
import os
import sys

class HITLGate:
    """
    Human-in-the-Loop Control Layer.
    Evaluates if an action requires human approval and provides a terminal UI bridge.
    """
    
    RISKY_KEYWORDS = [
        "block", "terminate", "delete", "iptables", "firewall", 
        "quarantine", "reset credentials", "shutdown"
    ]
    
    # ANSI Colors
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    @staticmethod
    def assess_risk(decision: str, confidence: float) -> str:
        """Determines if an action is informational or risky."""
        decision_lower = decision.lower()
        is_risky = any(keyword in decision_lower for keyword in HITLGate.RISKY_KEYWORDS)
        is_low_confidence = confidence < 0.7
        
        if is_risky or (is_low_confidence and ("response" in decision_lower or "action" in decision_lower)):
            return "pending"
        return "approved"

    def terminal_ui_intercept(self, pod_name, thoughts, proposed_action, metadata=None):
        """
        Mimics the production SOC intercept screen from user provided screenshot.
        """
        metadata = metadata or {}
        findings = metadata.get("findings", "N/A")
        severity = metadata.get("severity", "N/A")
        target_file = metadata.get("file", "N/A")

        print(f"\n{self.BOLD}{'='*70}")
        print(f"{' '*11}ACTION INTERCEPTED - OPERATOR OVERRIDE REQUIRED")
        print(f"{'='*70}{self.RESET}\n")

        print(f"{self.BOLD}AGENT:{self.RESET} {pod_name}")
        print(f"{self.BOLD}THOUGHT:{self.RESET} {thoughts}\n")
        
        print(f"{self.BOLD}PROPOSED ACTION:{self.RESET} {self.CYAN}{proposed_action}{self.RESET}\n")

        # Draw the box using ASCII for compatibility
        print(" +----------------------------------------------------------+")
        print(f" | Findings Detected: {findings:<37} |")
        print(f" | Severity: {severity:<47} |")
        print(f" | File: {target_file:<51} |")
        print(" +----------------------------------------------------------+\n")

        prompt = f"Action required: [{self.GREEN}y{self.RESET}] Approve, [{self.RED}n{self.RESET}] Reject/Skip, [{self.YELLOW}m{self.RESET}] Modify: "
        
        while True:
            choice = input(prompt).lower().strip()
            if choice == 'y':
                print(f"\n{self.GREEN}[OK] ACTION APPROVED BY OPERATOR{self.RESET}")
                return "approved"
            elif choice == 'n':
                print(f"\n{self.RED}[REJECTED] ACTION REJECTED BY OPERATOR{self.RESET}")
                return "rejected"
            elif choice == 'm':
                modification = input("Enter modified action: ").strip()
                print(f"\n{self.YELLOW}[MODIFIED] ACTION: {modification}{self.RESET}")
                return f"modified: {modification}"
            else:
                print("Invalid input. Please use y, n, or m.")

    def __call__(self, step_name: str, state: dict):
        """
        Global sequential HITL gate override based on Step-by-Step HITL SOC Mode design.
        """
        print("\n" + "="*60)
        print(f" [HITL] STEP: {step_name}")
        print("="*60)

        # عرض مختصر للحالة (Short state overview)
        for k, v in state.items():
            print(f"{k}: {v}")

        decision = input("\n> Continue? (y/n): ").strip().lower()

        if decision != "y":
            print(" [STOPPED] Execution STOPPED by Human Operator")
            sys.exit()

        print(" [APPROVED] - continuing pipeline\n")

hitl_gate = HITLGate()

