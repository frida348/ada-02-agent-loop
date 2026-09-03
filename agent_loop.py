"""
Simplified representation of an Agent Loop in Python.
Explicitly models the loop stages (OBSERVE, PLAN, ACT, VERIFY)
and core operations (READ, WRITE, EDIT, BASH).
"""

from dataclasses import dataclass, field
from enum import Enum
import os
import subprocess
from typing import Any, Callable, Dict, List, Optional


# ============================================================================
# 1. CORE OPERATIONS (READ, WRITE, EDIT, BASH)
# ============================================================================

class Operations:
    """Explicit primitives for agent interaction with the filesystem and shell."""

    @staticmethod
    def read(file_path: str) -> str:
        """READ operation: Read contents of a file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def write(file_path: str, content: str) -> str:
        """WRITE operation: Create or overwrite a file with given content."""
        parent_dir = os.path.dirname(os.path.abspath(file_path))
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {file_path}"

    @staticmethod
    def edit(file_path: str, old_text: str, new_text: str) -> str:
        """EDIT operation: Perform a targeted replacement within an existing file."""
        content = Operations.read(file_path)
        if old_text not in content:
            raise ValueError(f"Target text '{old_text}' not found in {file_path}")
        updated_content = content.replace(old_text, new_text, 1)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        return f"Successfully replaced target text in {file_path}"

    @staticmethod
    def bash(command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """BASH operation: Execute a shell command and capture outputs."""
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True
        )
        return {
            "command": command,
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }


# ============================================================================
# 2. STAGES OF THE AGENT LOOP
# ============================================================================

class Stage(str, Enum):
    OBSERVE = "OBSERVE"   # Gather environment state, command outputs, or user goal
    PLAN    = "PLAN"      # Reason about what to do next based on observations
    ACT     = "ACT"       # Dispatch an operation (READ, WRITE, EDIT, BASH)
    VERIFY  = "VERIFY"    # Evaluate outcomes and decide whether the goal is met


# ============================================================================
# 3. AGENT STATE AND STEP DATA STRUCTURES
# ============================================================================

@dataclass
class Action:
    operation: str  # "READ", "WRITE", "EDIT", "BASH", or "STOP"
    params: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""


@dataclass
class StepRecord:
    iteration: int
    stage: Stage
    detail: str
    result: Optional[Any] = None


@dataclass
class AgentState:
    goal: str
    iteration: int = 0
    max_iterations: int = 10
    history: List[StepRecord] = field(default_factory=list)
    last_observation: Any = None
    is_finished: bool = False
    success: bool = False


# ============================================================================
# 4. THE AGENT LOOP ENGINE
# ============================================================================

class AgentLoop:
    """
    Executes the autonomous loop through its explicit stages:
    OBSERVE -> PLAN -> ACT -> VERIFY
    """

    def __init__(
        self,
        goal: str,
        planner_fn: Callable[[AgentState], Action],
        verifier_fn: Callable[[AgentState, Action, Any], bool],
        max_iterations: int = 10,
    ):
        self.state = AgentState(goal=goal, max_iterations=max_iterations)
        self.planner = planner_fn
        self.verifier = verifier_fn

    def _execute_act(self, action: Action) -> Any:
        """Executes the specific operation chosen during the PLAN stage."""
        op = action.operation.upper()
        params = action.params

        if op == "READ":
            return Operations.read(params["file_path"])
        elif op == "WRITE":
            return Operations.write(params["file_path"], params["content"])
        elif op == "EDIT":
            return Operations.edit(
                params["file_path"], params["old_text"], params["new_text"]
            )
        elif op == "BASH":
            return Operations.bash(params["command"], cwd=params.get("cwd"))
        elif op == "STOP":
            return "Task signaled completion."
        else:
            raise ValueError(f"Unknown operation: {op}")

    def run(self) -> AgentState:
        """Runs the loop until goal is verified, max iterations reached, or stopped."""
        print(f"=== Starting Agent Loop: '{self.state.goal}' ===")

        while not self.state.is_finished and self.state.iteration < self.state.max_iterations:
            self.state.iteration += 1
            print(f"\n--- Iteration {self.state.iteration} ---")

            # ----------------------------------------------------------------
            # STAGE 1: OBSERVE
            # ----------------------------------------------------------------
            obs = self.state.last_observation or "Initial task start."
            self.state.history.append(
                StepRecord(self.state.iteration, Stage.OBSERVE, f"Observed: {str(obs)[:100]}")
            )
            print(f"[{Stage.OBSERVE.value}] State / Prior observation checked.")

            # ----------------------------------------------------------------
            # STAGE 2: PLAN
            # ----------------------------------------------------------------
            action = self.planner(self.state)
            self.state.history.append(
                StepRecord(
                    self.state.iteration,
                    Stage.PLAN,
                    f"Selected {action.operation} - Rationale: {action.rationale}"
                )
            )
            print(f"[{Stage.PLAN.value}] Next Action: {action.operation} ({action.rationale})")

            # ----------------------------------------------------------------
            # STAGE 3: ACT
            # ----------------------------------------------------------------
            try:
                op_result = self._execute_act(action)
                self.state.last_observation = op_result
                self.state.history.append(
                    StepRecord(self.state.iteration, Stage.ACT, f"Executed {action.operation}", op_result)
                )
                print(f"[{Stage.ACT.value}] Executed {action.operation} successfully.")
            except Exception as e:
                self.state.last_observation = f"Error during {action.operation}: {e}"
                self.state.history.append(
                    StepRecord(self.state.iteration, Stage.ACT, f"Failed {action.operation}", str(e))
                )
                print(f"[{Stage.ACT.value}] Operation failed: {e}")
                continue

            # ----------------------------------------------------------------
            # STAGE 4: VERIFY
            # ----------------------------------------------------------------
            goal_achieved = self.verifier(self.state, action, op_result)
            self.state.history.append(
                StepRecord(
                    self.state.iteration,
                    Stage.VERIFY,
                    f"Verification result: {'MET' if goal_achieved else 'UNMET'}"
                )
            )
            print(f"[{Stage.VERIFY.value}] Goal condition satisfied: {goal_achieved}")

            if goal_achieved or action.operation.upper() == "STOP":
                self.state.is_finished = True
                self.state.success = goal_achieved
                break

        print(f"\n=== Finished: {'SUCCESS' if self.state.success else 'INCOMPLETE'} ===")
        return self.state


# ============================================================================
# 5. DEMONSTRATION RUN
# ============================================================================

if __name__ == "__main__":
    sandbox_file = "sandbox_example.py"

    # Plan demonstrating WRITE, BASH, READ, and EDIT operations
    demo_plan = [
        Action(
            operation="WRITE",
            params={
                "file_path": sandbox_file,
                "content": "def double(n):\n    return n + 1\n",
            },
            rationale="Initialize sandbox module with a buggy function."
        ),
        Action(
            operation="BASH",
            params={
                "command": f'python -c "import sandbox_example; assert sandbox_example.double(4) == 8"'
            },
            rationale="Run assertion to test the sandbox module."
        ),
        Action(
            operation="READ",
            params={"file_path": sandbox_file},
            rationale="Inspect the source code to find the discrepancy."
        ),
        Action(
            operation="EDIT",
            params={
                "file_path": sandbox_file,
                "old_text": "return n + 1",
                "new_text": "return n * 2",
            },
            rationale="Fix the logic error in the function."
        ),
        Action(
            operation="BASH",
            params={
                "command": f'python -c "import sandbox_example; assert sandbox_example.double(4) == 8"'
            },
            rationale="Re-run the assertion to verify fix."
        ),
    ]

    def rule_based_planner(state: AgentState) -> Action:
        step_idx = state.iteration - 1
        if step_idx < len(demo_plan):
            return demo_plan[step_idx]
        return Action(operation="STOP", rationale="Completed plan sequence.")

    def outcome_verifier(state: AgentState, action: Action, result: Any) -> bool:
        # Check if the BASH verification command exited successfully
        if action.operation == "BASH" and isinstance(result, dict):
            if result.get("exit_code") == 0 and state.iteration > 2:
                return True
        return False

    try:
        agent = AgentLoop(
            goal="Fix logic bug in sandbox_example.py and pass assertion",
            planner_fn=rule_based_planner,
            verifier_fn=outcome_verifier,
            max_iterations=10,
        )
        final_state = agent.run()
    finally:
        # Cleanup sandbox file
        if os.path.exists(sandbox_file):
            os.remove(sandbox_file)
