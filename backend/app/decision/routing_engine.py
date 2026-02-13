"""
Routing Engine - Bin Recommendation and Route Determination.

Converts material classifications into routing decisions:
- Maps material → bin type (BLUE_BIN, GREEN_BIN, etc.)
- Translates bin → backend route (PLASTIC_BIN, PAPER_BIN, etc.)
- Handles special cases (uncertain → manual review, hazardous → special handling)
- Returns Decision schema compatible with existing backend systems
"""

from __future__ import annotations

from typing import Optional

from ..decision.decision_engine import ObjectDecision
from ..taxonomy import (
    get_bin_from_material,
    get_route_from_bin,
    get_final_route,
    MANUAL_REVIEW_ROUTE,
)
from ..schemas import Decision
from ..logging_config import inference_logger


class RoutingEngine:
    """
    Routing engine for converting decisions into bin recommendations.
    
    Maps final material + decision type → routing instructions
    """
    
    def __init__(
        self,
        uncertain_to_review: bool = True,
        contamination_to_review: bool = False,
        verbose: bool = False
    ):
        """
        Initialize routing engine.
        
        Args:
            uncertain_to_review: Send uncertain items to manual review
            contamination_to_review: Send contaminated items to manual review
            verbose: Enable verbose logging
        """
        self.uncertain_to_review = uncertain_to_review
        self.contamination_to_review = contamination_to_review
        self.verbose = verbose
        
        inference_logger.info(
            "Routing engine initialized",
            extra={
                "uncertain_to_review": uncertain_to_review,
                "contamination_to_review": contamination_to_review,
            }
        )
    
    def route(
        self,
        decision: ObjectDecision
    ) -> tuple[Decision, str]:
        """
        Generate routing decision for an object.
        
        Args:
            decision: ObjectDecision from decision engine
        
        Returns:
            Tuple of (Decision schema, recommended_bin)
            - Decision: Compatible with existing backend Event schema
            - recommended_bin: User-friendly bin name (e.g., "BLUE_BIN")
        """
        # Determine if item should go to manual review
        needs_review = self._needs_manual_review(decision)
        
        # Determine contamination flag
        contamination_flag = self._is_contaminated(decision)
        
        # Get route and bin
        if needs_review:
            route = MANUAL_REVIEW_ROUTE
            recommended_bin = "MANUAL_REVIEW"
            reason = self._format_review_reason(decision)
        else:
            route, recommended_bin = get_final_route(
                decision.final_material,
                uncertain=False,
                contaminated=False
            )
            reason = decision.reason
        
        # Create Decision schema
        backend_decision = Decision(
            route=route,
            contamination_flag=contamination_flag,
            agent_disagreement=decision.agent_disagreement,
            reason=reason,
            contamination_score=decision.contamination_score,
            confidence_score=decision.confidence_score,
            material_agent_decision=decision.detector_material,
            routing_agent_decision=decision.classifier_material,
        )
        
        if self.verbose:
            inference_logger.debug(
                f"Routing: {decision.final_material} → {route} ({recommended_bin})",
                extra={
                    "object_id": decision.object_id,
                    "route": route,
                    "bin": recommended_bin,
                    "contamination": contamination_flag,
                }
            )
        
        return backend_decision, recommended_bin
    
    def _needs_manual_review(self, decision: ObjectDecision) -> bool:
        """Check if item needs manual review."""
        if decision.decision_type == "UNCERTAIN" and self.uncertain_to_review:
            return True
        
        if decision.decision_type == "CONTAMINATION" and self.contamination_to_review:
            return True
        
        # Very low confidence
        if decision.confidence_score < 0.40:
            return True
        
        # High contamination score
        if decision.contamination_score > 0.70:
            return True
        
        return False
    
    def _is_contaminated(self, decision: ObjectDecision) -> bool:
        """Determine if item is flagged as contaminated."""
        # Contamination decision type
        if decision.decision_type == "CONTAMINATION":
            return True
        
        # High contamination score
        if decision.contamination_score > 0.50:
            return True
        
        # Hazardous material detected in wrong stream
        hazardous_keywords = {"hazardous", "battery", "electronics"}
        if decision.classifier_material in hazardous_keywords:
            if decision.detector_material not in hazardous_keywords:
                return True
        
        return False
    
    def _format_review_reason(self, decision: ObjectDecision) -> str:
        """Format reason for manual review."""
        reasons = []
        
        if decision.decision_type == "UNCERTAIN":
            reasons.append(
                f"Low classifier confidence ({decision.confidence_classifier:.2f})"
            )
        
        if decision.decision_type == "CONTAMINATION":
            reasons.append(
                f"Material conflict: {decision.detector_material} vs {decision.classifier_material}"
            )
        
        if decision.confidence_score < 0.40:
            reasons.append(f"Very low confidence ({decision.confidence_score:.2f})")
        
        if decision.contamination_score > 0.70:
            reasons.append(f"High contamination risk ({decision.contamination_score:.2f})")
        
        if not reasons:
            reasons.append("Flagged for review")
        
        return " | ".join(reasons)
    
    def batch_route(
        self,
        decisions: list[ObjectDecision]
    ) -> list[tuple[Decision, str]]:
        """
        Route multiple objects.
        
        Args:
            decisions: List of ObjectDecisions
        
        Returns:
            List of (Decision, recommended_bin) tuples
        """
        return [self.route(dec) for dec in decisions]
    
    def get_bin_statistics(
        self,
        decisions: list[ObjectDecision]
    ) -> dict[str, int]:
        """
        Get bin distribution statistics.
        
        Args:
            decisions: List of ObjectDecisions
        
        Returns:
            Dictionary mapping bin names to counts
        """
        bin_counts = {}
        
        for decision in decisions:
            _, bin_name = self.route(decision)
            bin_counts[bin_name] = bin_counts.get(bin_name, 0) + 1
        
        return bin_counts
    
    def get_routing_summary(
        self,
        decisions: list[ObjectDecision]
    ) -> dict:
        """
        Get comprehensive routing summary.
        
        Args:
            decisions: List of ObjectDecisions
        
        Returns:
            Summary dictionary with counts and percentages
        """
        if not decisions:
            return {
                "total_objects": 0,
                "bin_distribution": {},
                "contamination_rate": 0.0,
                "manual_review_rate": 0.0,
            }
        
        total = len(decisions)
        bin_counts = self.get_bin_statistics(decisions)
        
        contaminated = sum(1 for d in decisions if self._is_contaminated(d))
        needs_review = sum(1 for d in decisions if self._needs_manual_review(d))
        
        return {
            "total_objects": total,
            "bin_distribution": bin_counts,
            "contamination_count": contaminated,
            "contamination_rate": contaminated / total,
            "manual_review_count": needs_review,
            "manual_review_rate": needs_review / total,
        }
    
    def get_info(self) -> dict:
        """Get engine info for logging."""
        return {
            "uncertain_to_review": self.uncertain_to_review,
            "contamination_to_review": self.contamination_to_review,
        }
