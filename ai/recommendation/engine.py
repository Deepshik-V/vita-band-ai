"""
Recommendation Engine for VITA-BAND AI
Generates contextual, evidence-informed preventive guidance and wellness advice.
Note: Framed strictly as early-warning guidance, NOT a clinical diagnosis.
"""
from datetime import datetime
from typing import List
import uuid

from backend.models.schemas import RiskAssessment, Recommendation, RiskLevel


class RecommendationEngine:
    """Provides non-diagnostic wellness and preventive recommendations based on detected risks."""

    DISCLAIMER_TEXT = (
        "Preventive early-warning guidance only; not medical diagnosis. "
        "Consult healthcare professionals or emergency services for persistent or acute symptoms."
    )

    RECOMMENDATION_CATALOG = {
        "HEAT_STRESS": {
            "title": "Heat Stress Mitigation Protocol",
            "urgency": "high",
            "guidance": [
                "Move to a cooler, shaded, or air-conditioned environment immediately.",
                "Reduce physical activity and rest in a seated or semi-reclined position.",
                "Drink cool water or electrolyte-enhanced fluids in slow sips.",
                "Loosen tight clothing and apply cool damp cloths to skin if available.",
                "Continue continuous monitoring; seek emergency medical assistance if nausea or dizziness develops.",
            ],
        },
        "DEHYDRATION": {
            "title": "Hydration Recovery Advisory",
            "urgency": "medium",
            "guidance": [
                "Consume 300–500ml of water or oral rehydration solution (ORS).",
                "Rest in a cool area out of direct sunlight.",
                "Avoid caffeine, alcohol, or hyper-sugary beverages which accelerate fluid loss.",
                "Monitor for urine color lightening and vital stabilization.",
            ],
        },
        "FATIGUE": {
            "title": "Muscle Fatigue & Exhaustion Relief",
            "urgency": "medium",
            "guidance": [
                "Discontinue strenuous physical tasks or manual labor for at least 20 minutes.",
                "Engage in gentle posture changes and light stretching to reduce localized muscle strain.",
                "Ensure adequate hydration and electrolyte intake.",
                "Avoid operating heavy equipment or vehicles until energy levels normalize.",
            ],
        },
        "ABNORMAL_VITALS": {
            "title": "Vital Sign Anomaly Alert Guidance",
            "urgency": "high",
            "guidance": [
                "Sit down in a stable, supported posture immediately.",
                "Breathe slowly and deeply through the nose and out through the mouth.",
                "Verify that the VITA-BAND sensor strap is firmly in contact with clean, dry skin.",
                "Remain still for 2 minutes while telemetry recalibrates.",
                "If palpitations, chest tightness, or dizziness persist, seek medical attention.",
            ],
        },
        "FALL": {
            "title": "Post-Impact Fall Safety Instructions",
            "urgency": "critical",
            "guidance": [
                "Stay still for a moment; do not attempt to stand up abruptly.",
                "Perform a gentle self-assessment for head trauma, neck pain, or bone fractures.",
                "If uninjured, roll onto your side and slowly use sturdy furniture for support to rise.",
                "If in severe pain or unable to get up, press the SOS button or allow the automatic alert to dispatch to emergency contacts.",
            ],
        },
        "RESPIRATORY_RISK": {
            "title": "Oxygenation & Respiratory Support",
            "urgency": "critical",
            "guidance": [
                "Sit upright in a well-ventilated space to maximize lung expansion.",
                "Loosen restrictive collars, belts, or chest straps.",
                "Practice calm, pursed-lip breathing (inhale 2s, exhale 4s).",
                "If SpO2 remains below 90% or shortness of breath intensifies, contact emergency healthcare immediately.",
            ],
        },
        "ENVIRONMENTAL_STRESS": {
            "title": "Environmental Hazard Precautions",
            "urgency": "medium",
            "guidance": [
                "High ambient heat and humidity elevate heat index danger.",
                "Limit outdoor exposure during peak daylight hours.",
                "Wear loose, lightweight, light-colored breathable clothing.",
                "Ensure continuous cross-ventilation in indoor working areas.",
            ],
        },
        "NORMAL_STATE": {
            "title": "Target Physiological Stability",
            "urgency": "low",
            "guidance": [
                "All primary vital parameters (Heart Rate, SpO2, Temperature) are within stable target ranges.",
                "Maintain baseline hydration (250ml water every 60–90 minutes).",
                "Continue standard daily activities with continuous companion monitoring active.",
            ],
        },
    }

    def generate_recommendations(self, risk_assessment: RiskAssessment) -> List[Recommendation]:
        """Maps active risks in assessment to structured recommendations."""
        recommendations: List[Recommendation] = []
        now_str = datetime.utcnow().isoformat()

        risks = risk_assessment.detected_risks or ["NORMAL_STATE"]

        for risk_key in risks:
            cat_data = self.RECOMMENDATION_CATALOG.get(risk_key)
            if not cat_data and risk_assessment.risk_level == RiskLevel.NORMAL:
                cat_data = self.RECOMMENDATION_CATALOG["NORMAL_STATE"]

            if cat_data:
                rec = Recommendation(
                    id=f"rec-{uuid.uuid4().hex[:8]}",
                    timestamp=now_str,
                    risk_category=risk_key,
                    urgency=cat_data["urgency"],
                    title=cat_data["title"],
                    guidance=cat_data["guidance"],
                    disclaimer=self.DISCLAIMER_TEXT,
                )
                recommendations.append(rec)

        # Fallback if nothing matched
        if not recommendations:
            cat_data = self.RECOMMENDATION_CATALOG["NORMAL_STATE"]
            recommendations.append(Recommendation(
                id=f"rec-{uuid.uuid4().hex[:8]}",
                timestamp=now_str,
                risk_category="GENERAL_WELLNESS",
                urgency="low",
                title=cat_data["title"],
                guidance=cat_data["guidance"],
                disclaimer=self.DISCLAIMER_TEXT,
            ))

        return recommendations
