"""
Decision Engine - Conflict Resolution and Material Determination.

Analyzes detector and classifier outputs to:
1. Detect cross-agent disagreements
2. Identify uncertainty
3. Flag contamination
4. Determine final material category
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from ..detector import DetectorResult
from ..classifier import ClassifierResult
from ..taxonomy import get_material_from_detector
from ..logging_config import inference_logger


@dataclass
class ObjectDecision:
    """Decision result for a single detected object."""
    
    # Identifiers
    object_id: str
    
    # Agent outputs
    detector_label: str
    classifier_label: str
    detector_material: str
    classifier_material: str
    confidence_detector: float
    confidence_classifier: float
    
    # Decision
    decision_type: str  # "HIGH_CONFIDENCE", "UNCERTAIN", "CONTAMINATION"
    final_material: str
    reason: str
    
    # Scores
    confidence_score: float
    contamination_score: float
    agent_disagreement: bool
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "object_id": self.object_id,
            "detector_label": self.detector_label,
            "classifier_label": self.classifier_label,
            "detector_material": self.detector_material,
            "classifier_material": self.classifier_material,
            "confidence_detector": self.confidence_detector,
            "confidence_classifier": self.confidence_classifier,
            "decision_type": self.decision_type,
            "final_material": self.final_material,
            "reason": self.reason,
            "confidence_score": self.confidence_score,
            "contamination_score": self.contamination_score,
            "agent_disagreement": self.agent_disagreement,
        }


class DecisionEngine:
    """
    Decision engine for determining final material classification.
    
    Implements conflict resolution logic:
    - If classifier confidence < threshold → UNCERTAIN
    - If detector material != classifier material → CONTAMINATION
    - Otherwise → HIGH_CONFIDENCE
    
    Final material selection:
    - Use classifier if confidence > high_conf_threshold
    - Otherwise use detector
    """
    
    def __init__(
        self,
        classifier_threshold: float = None,
        high_confidence_threshold: float = 0.70,
        contamination_threshold: float = 0.30,
        verbose: bool = False
    ):
        """
        Initialize decision engine.
        
        Args:
            classifier_threshold: Minimum classifier confidence (from env or 0.55)
            high_confidence_threshold: Threshold for using classifier material
            contamination_threshold: Threshold for contamination score
            verbose: Enable verbose logging
        """
        # Get threshold from env if not provided
        if classifier_threshold is None:
            classifier_threshold = float(os.getenv("MODEL_CONF_TIER2", "0.55"))
        
        self.classifier_threshold = classifier_threshold
        self.high_confidence_threshold = high_confidence_threshold
        self.contamination_threshold = contamination_threshold
        self.verbose = verbose
        
        inference_logger.info(
            "Decision engine initialized",
            extra={
                "classifier_threshold": classifier_threshold,
                "high_confidence_threshold": high_confidence_threshold,
            }
        )
    
    def decide(
        self,
        detector_result: DetectorResult,
        classifier_result: ClassifierResult,
        object_id: str = None
    ) -> ObjectDecision:
        """
        Make decision for a single object.
        
        Args:
            detector_result: Detection from Stage 1
            classifier_result: Classification from Stage 2
            object_id: Optional object identifier
        
        Returns:
            ObjectDecision with final material and reasoning
        """
        if object_id is None:
            object_id = f"obj_{id(detector_result)}"
        
        # Extract labels and confidences
        detector_label = detector_result.label
        classifier_label = classifier_result.label
        detector_conf = detector_result.confidence
        classifier_conf = classifier_result.confidence
        
        # Map to materials
        detector_material = get_material_from_detector(detector_label)
        classifier_material = get_material_from_detector(classifier_label)
        
        # Decision logic
        decision_type, reason = self._determine_decision_type(
            detector_material,
            classifier_material,
            detector_conf,
            classifier_conf
        )
        
        # Determine final material
        final_material = self._determine_final_material(
            detector_material,
            classifier_material,
            classifier_conf,
            decision_type
        )
        
        # Calculate scores
        confidence_score = self._calculate_confidence_score(
            detector_conf,
            classifier_conf,
            decision_type
        )
        
        contamination_score = self._calculate_contamination_score(
            detector_material,
            classifier_material,
            classifier_conf
        )
        
        agent_disagreement = (detector_material != classifier_material)
        
        decision = ObjectDecision(
            object_id=object_id,
            detector_label=detector_label,
            classifier_label=classifier_label,
            detector_material=detector_material,
            classifier_material=classifier_material,
            confidence_detector=detector_conf,
            confidence_classifier=classifier_conf,
            decision_type=decision_type,
            final_material=final_material,
            reason=reason,
            confidence_score=confidence_score,
            contamination_score=contamination_score,
            agent_disagreement=agent_disagreement,
        )
        
        if self.verbose:
            inference_logger.debug(
                f"Decision: {decision_type}",
                extra=decision.to_dict()
            )
        
        return decision
    
    def _determine_decision_type(
        self,
        detector_material: str,
        classifier_material: str,
        detector_conf: float,
        classifier_conf: float
    ) -> tuple[str, str]:
        """
        Determine decision type and reason.
        
        Returns:
            Tuple of (decision_type, reason)
        """
        # Check classifier confidence first
        if classifier_conf < self.classifier_threshold:
            return (
                "UNCERTAIN",
                f"Classifier confidence ({classifier_conf:.2f}) below threshold ({self.classifier_threshold:.2f})"
            )
        
        # Check material agreement
        if detector_material != classifier_material:
            return (
                "CONTAMINATION",
                f"Material mismatch: detector={detector_material}, classifier={classifier_material}"
            )
        
        # High confidence
        return (
            "HIGH_CONFIDENCE",
            f"Both agents agree on {classifier_material} with high confidence"
        )
    
    def _determine_final_material(
        self,
        detector_material: str,
        classifier_material: str,
        classifier_conf: float,
        decision_type: str
    ) -> str:
        """
        Determine final material category.
        
        Logic:
        - If classifier confidence > high_conf_threshold: use classifier
        - Otherwise: use detector (more robust to edge cases)
        """
        # For contamination cases, prefer detector (less specific but safer)
        if decision_type == "CONTAMINATION":
            return detector_material
        
        # For uncertain cases, use detector
        if decision_type == "UNCERTAIN":
            return detector_material
        
        # For high confidence, use classifier if conf > threshold
        if classifier_conf > self.high_confidence_threshold:
            return classifier_material
        
        # Default to detector
        return detector_material
    
    def _calculate_confidence_score(
        self,
        detector_conf: float,
        classifier_conf: float,
        decision_type: str
    ) -> float:
        """
        Calculate overall confidence score.
        
        Weighted average, with penalty for disagreement.
        """
        # Base score: average of both confidences
        base_score = (detector_conf + classifier_conf) / 2.0
        
        # Apply penalty for uncertain or contamination
        if decision_type == "UNCERTAIN":
            return base_score * 0.6
        elif decision_type == "CONTAMINATION":
            return base_score * 0.7
        
        # High confidence: boost score
        return min(1.0, base_score * 1.1)
    
    def _calculate_contamination_score(
        self,
        detector_material: str,
        classifier_material: str,
        classifier_conf: float
    ) -> float:
        """
        Calculate contamination probability.
        
        High if:
        - Materials disagree
        - Classifier is confident in disagreement
        """
        if detector_material == classifier_material:
            return 0.0
        
        # Disagreement exists
        # Higher classifier confidence = higher contamination likelihood
        contamination = classifier_conf * 0.8
        
        # Check for hazardous misclassification (critical)
        hazardous_materials = {"hazardous", "battery", "electronics"}
        if (classifier_material in hazardous_materials or 
            detector_material in hazardous_materials):
            contamination = min(1.0, contamination * 1.5)
        
        return contamination
    
    def batch_decide(
        self,
        detector_results: list[DetectorResult],
        classifier_results: list[ClassifierResult]
    ) -> list[ObjectDecision]:
        """
        Make decisions for multiple objects.
        
        Args:
            detector_results: List of detections
            classifier_results: List of classifications (same order)
        
        Returns:
            List of ObjectDecisions
        """
        if len(detector_results) != len(classifier_results):
            raise ValueError(
                f"Mismatch: {len(detector_results)} detections, "
                f"{len(classifier_results)} classifications"
            )
        
        decisions = []
        for i, (det, clf) in enumerate(zip(detector_results, classifier_results)):
            decision = self.decide(det, clf, object_id=f"obj_{i}")
            decisions.append(decision)
        
        return decisions
    
    def get_info(self) -> dict:
        """Get engine info for logging."""
        return {
            "classifier_threshold": self.classifier_threshold,
            "high_confidence_threshold": self.high_confidence_threshold,
            "contamination_threshold": self.contamination_threshold,
        }
