
# ==== FILE 3: services/aiml-orchestration/src/orchestrators/workflow_manager.py ====

"""
Workflow state management for RAG pipeline.
Tracks workflow progress and manages state transitions.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PhaseStatus(Enum):
    """Phase status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowPhase:
    """Individual workflow phase tracking."""
    name: str
    status: PhaseStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error: Optional[str]
    metadata: Dict[str, Any]

@dataclass
class WorkflowState:
    """Complete workflow state."""
    workflow_id: str
    query: str
    status: WorkflowStatus
    phases: Dict[str, WorkflowPhase]
    start_time: datetime
    end_time: Optional[datetime]
    total_duration: Optional[float]
    metadata: Dict[str, Any]

class WorkflowManager:
    """
    Manages workflow states and transitions for RAG pipeline.
    """
    
    def __init__(self):
        self.active_workflows = {}
        self.completed_workflows = {}
        
        self.workflow_stats = {
            'total_workflows': 0,
            'completed_workflows': 0,
            'failed_workflows': 0,
            'cancelled_workflows': 0,
            'average_workflow_duration': 0.0,
            'total_workflow_time': 0.0,
            'phase_failures': 0,
            'phase_completions': 0
        }
        
        # Standard RAG phases
        self.standard_phases = [
            'retrieval',
            'synthesis',
            'fallback'  # Optional phase
        ]

    def start_workflow(self, workflow_id: str, query: str, metadata: Dict[str, Any] = None) -> WorkflowState:
        """
        Start a new workflow.
        """
        if workflow_id in self.active_workflows:
            logger.warning(f"Workflow {workflow_id} already exists, overwriting")
        
        # Initialize phases
        phases = {}
        for phase_name in self.standard_phases:
            phases[phase_name] = WorkflowPhase(
                name=phase_name,
                status=PhaseStatus.NOT_STARTED,
                start_time=None,
                end_time=None,
                error=None,
                metadata={}
            )
        
        # Create workflow state
        workflow_state = WorkflowState(
            workflow_id=workflow_id,
            query=query,
            status=WorkflowStatus.IN_PROGRESS,
            phases=phases,
            start_time=datetime.now(),
            end_time=None,
            total_duration=None,
            metadata=metadata or {}
        )
        
        self.active_workflows[workflow_id] = workflow_state
        self.workflow_stats['total_workflows'] += 1
        
        logger.info(f"Started workflow {workflow_id} for query: {query[:50]}...")
        
        return workflow_state

    def update_phase(
        self, 
        workflow_id: str, 
        phase_name: str, 
        status: str,
        error: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Update phase status within a workflow.
        """
        if workflow_id not in self.active_workflows:
            logger.error(f"Workflow {workflow_id} not found")
            return False
        
        workflow = self.active_workflows[workflow_id]
        
        if phase_name not in workflow.phases:
            # Add new phase if it doesn't exist
            workflow.phases[phase_name] = WorkflowPhase(
                name=phase_name,
                status=PhaseStatus.NOT_STARTED,
                start_time=None,
                end_time=None,
                error=None,
                metadata={}
            )
        
        phase = workflow.phases[phase_name]
        
        # Update phase based on status
        if status == 'in_progress':
            phase.status = PhaseStatus.IN_PROGRESS
            phase.start_time = datetime.now()
        elif status == 'completed':
            phase.status = PhaseStatus.COMPLETED
            phase.end_time = datetime.now()
            self.workflow_stats['phase_completions'] += 1
        elif status == 'failed':
            phase.status = PhaseStatus.FAILED
            phase.end_time = datetime.now()
            phase.error = error
            self.workflow_stats['phase_failures'] += 1
        elif status == 'skipped':
            phase.status = PhaseStatus.SKIPPED
            phase.end_time = datetime.now()
        
        # Update phase metadata
        if metadata:
            phase.metadata.update(metadata)
        
        logger.debug(f"Updated phase {phase_name} to {status} for workflow {workflow_id}")
        return True

    def complete_workflow(
        self, 
        workflow_id: str, 
        success: bool = True, 
        error: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Complete a workflow.
        """
        if workflow_id not in self.active_workflows:
            logger.error(f"Workflow {workflow_id} not found")
            return False
        
        workflow = self.active_workflows[workflow_id]
        
        # Update workflow status
        workflow.end_time = datetime.now()
        workflow.total_duration = (workflow.end_time - workflow.start_time).total_seconds()
        
        if success:
            workflow.status = WorkflowStatus.COMPLETED
            self.workflow_stats['completed_workflows'] += 1
        else:
            workflow.status = WorkflowStatus.FAILED
            self.workflow_stats['failed_workflows'] += 1
            if error:
                workflow.metadata['error'] = error
        
        # Update metadata
        if metadata:
            workflow.metadata.update(metadata)
        
        # Update statistics
        self.workflow_stats['total_workflow_time'] += workflow.total_duration
        self.workflow_stats['average_workflow_duration'] = (
            self.workflow_stats['total_workflow_time'] / 
            self.workflow_stats['total_workflows']
        )
        
        # Move to completed workflows
        self.completed_workflows[workflow_id] = workflow
        del self.active_workflows[workflow_id]
        
        # Keep completed workflows manageable
        if len(self.completed_workflows) > 100:
            oldest_workflows = sorted(
                self.completed_workflows.items(),
                key=lambda x: x[1].start_time
            )[:50]
            for old_id, _ in oldest_workflows:
                del self.completed_workflows[old_id]
        
        logger.info(f"Completed workflow {workflow_id}: success={success}, duration={workflow.total_duration:.2f}s")
        return True

    def cancel_workflow(self, workflow_id: str, reason: str = None) -> bool:
        """
        Cancel an active workflow.
        """
        if workflow_id not in self.active_workflows:
            logger.error(f"Workflow {workflow_id} not found")
            return False
        
        workflow = self.active_workflows[workflow_id]
        workflow.status = WorkflowStatus.CANCELLED
        workflow.end_time = datetime.now()
        workflow.total_duration = (workflow.end_time - workflow.start_time).total_seconds()
        
        if reason:
            workflow.metadata['cancellation_reason'] = reason
        
        self.workflow_stats['cancelled_workflows'] += 1
        
        # Move to completed workflows
        self.completed_workflows[workflow_id] = workflow
        del self.active_workflows[workflow_id]
        
        logger.info(f"Cancelled workflow {workflow_id}: {reason}")
        return True

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific workflow.
        """
        # Check active workflows
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
        elif workflow_id in self.completed_workflows:
            workflow = self.completed_workflows[workflow_id]
        else:
            return None
        
        # Calculate phase progress
        phase_progress = {}
        for phase_name, phase in workflow.phases.items():
            duration = None
            if phase.start_time and phase.end_time:
                duration = (phase.end_time - phase.start_time).total_seconds()
            elif phase.start_time:
                duration = (datetime.now() - phase.start_time).total_seconds()
            
            phase_progress[phase_name] = {
                'status': phase.status.value,
                'duration': duration,
                'error': phase.error,
                'metadata': phase.metadata
            }
        
        return {
            'workflow_id': workflow.workflow_id,
            'query': workflow.query,
            'status': workflow.status.value,
            'total_duration': workflow.total_duration,
            'phases': phase_progress,
            'metadata': workflow.metadata
        }

    def get_active_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active workflows.
        """
        active = {}
        for workflow_id, workflow in self.active_workflows.items():
            active[workflow_id] = self.get_workflow_status(workflow_id)
        
        return active

    def get_workflow_statistics(self) -> Dict[str, Any]:
        """
        Get workflow management statistics.
        """
        return {
            **self.workflow_stats,
            'completion_rate': f"{(self.workflow_stats['completed_workflows'] / max(1, self.workflow_stats['total_workflows'])) * 100:.2f}%",
            'failure_rate': f"{(self.workflow_stats['failed_workflows'] / max(1, self.workflow_stats['total_workflows'])) * 100:.2f}%",
            'active_workflows_count': len(self.active_workflows),
            'completed_workflows_count': len(self.completed_workflows)
        }

    def cleanup_old_workflows(self, max_age_hours: int = 24):
        """
        Cleanup old completed workflows.
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        workflows_to_remove = []
        for workflow_id, workflow in self.completed_workflows.items():
            if workflow.end_time and workflow.end_time < cutoff_time:
                workflows_to_remove.append(workflow_id)
        
        for workflow_id in workflows_to_remove:
            del self.completed_workflows[workflow_id]
        
        logger.info(f"Cleaned up {len(workflows_to_remove)} old workflows")
        return len(workflows_to_remove)

    def get_workflow_health(self) -> Dict[str, Any]:
        """
        Get workflow system health metrics.
        """
        stats = self.get_workflow_statistics()
        completion_rate = float(stats['completion_rate'].rstrip('%'))
        
        health_status = "healthy"
        if completion_rate < 90:
            health_status = "degraded"
        if completion_rate < 70:
            health_status = "unhealthy"
        
        recommendations = []
        if self.workflow_stats['phase_failures'] > self.workflow_stats['phase_completions'] * 0.1:
            recommendations.append("High phase failure rate detected")
        
        if self.workflow_stats['average_workflow_duration'] > 30:
            recommendations.append("Average workflow duration is high")
        
        if len(self.active_workflows) > 10:
            recommendations.append("Many active workflows - consider resource scaling")
        
        return {
            'status': health_status,
            'completion_rate': stats['completion_rate'],
            'average_duration': f"{self.workflow_stats['average_workflow_duration']:.2f}s",
            'active_count': len(self.active_workflows),
            'recommendations': recommendations
        }

    def export_workflow_data(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Export complete workflow data for analysis.
        """
        workflow_status = self.get_workflow_status(workflow_id)
        if not workflow_status:
            return None
        
        return {
            'workflow_data': workflow_status,
            'export_timestamp': datetime.now().isoformat(),
            'system_stats': self.get_workflow_statistics()
        }
