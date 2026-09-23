"""
Smart Health Simulation Framework Routes
"""
from fastapi import APIRouter
from backend.models.schemas import SimulationScenario, SimulationStartRequest
from backend.simulation.simulator import simulator

router = APIRouter(prefix="/api/simulation", tags=["Simulation Engine"])


@router.get("/status", response_model=SimulationScenario)
def get_simulation_status():
    """Returns the current state and parameters of the simulation framework."""
    return simulator.get_status()


@router.post("/start", response_model=SimulationScenario)
def start_simulation(request: SimulationStartRequest):
    """
    Activates one of the 8 deterministic simulation scenarios:
    NORMAL, HEAT_STRESS, DEHYDRATION, FATIGUE, ABNORMAL_VITALS,
    FALL, RESPIRATORY_RISK, ENVIRONMENTAL_STRESS.
    """
    return simulator.start_scenario(
        scenario=request.scenario,
        duration=request.duration_seconds,
        severity=request.severity,
        noise_level=request.noise_level,
    )


@router.post("/stop", response_model=SimulationScenario)
def stop_simulation():
    """Stops any active physiological stress scenario and reverts to NORMAL baseline."""
    from backend.alerts.alert_engine import alert_engine
    alert_engine.clear_active_alert()
    return simulator.stop_scenario()
