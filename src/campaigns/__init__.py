"""Campaign orchestration for outbound calling."""
import logging
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class Campaign:
    """Campaign definition."""
    campaign_id: str
    name: str
    campaign_type: str  # "reminder", "followup", "feedback"
    patient_ids: List[str]
    status: str  # "pending", "running", "completed", "failed"
    created_at: datetime
    start_time: datetime | None = None
    end_time: datetime | None = None


class CampaignOrchestrator:
    """Manage outbound calling campaigns."""

    def __init__(self):
        """Initialize campaign orchestrator."""
        self.campaigns: Dict[str, Campaign] = {}
        self.call_logs: Dict[str, List[Dict[str, Any]]] = {}

    async def create_campaign(
        self,
        name: str,
        campaign_type: str,
        patient_ids: List[str]
    ) -> Campaign:
        """Create new campaign."""
        import uuid
        
        campaign = Campaign(
            campaign_id=str(uuid.uuid4()),
            name=name,
            campaign_type=campaign_type,
            patient_ids=patient_ids,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        self.campaigns[campaign.campaign_id] = campaign
        self.call_logs[campaign.campaign_id] = []
        
        logger.info(f"Created campaign: {campaign.campaign_id} ({name})")
        return campaign

    async def start_campaign(self, campaign_id: str) -> bool:
        """Start campaign execution."""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            logger.error(f"Campaign not found: {campaign_id}")
            return False
        
        campaign.status = "running"
        campaign.start_time = datetime.utcnow()
        
        logger.info(f"Started campaign: {campaign_id}")
        return True

    async def log_call(
        self,
        campaign_id: str,
        patient_id: str,
        outcome: str,
        duration_seconds: int,
        notes: str = ""
    ) -> bool:
        """Log a campaign call."""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return False
        
        call_log = {
            "patient_id": patient_id,
            "outcome": outcome,  # "success", "voicemail", "declined", "scheduled"
            "duration_seconds": duration_seconds,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.call_logs[campaign_id].append(call_log)
        logger.debug(f"Logged call for campaign {campaign_id}")
        
        return True

    async def get_campaign_summary(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign statistics."""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return {}
        
        logs = self.call_logs.get(campaign_id, [])
        
        outcomes = {}
        for log in logs:
            outcome = log.get("outcome")
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        total_duration = sum(log.get("duration_seconds", 0) for log in logs)
        
        return {
            "campaign_id": campaign_id,
            "name": campaign.name,
            "status": campaign.status,
            "total_calls_scheduled": len(campaign.patient_ids),
            "total_calls_attempted": len(logs),
            "outcomes": outcomes,
            "total_duration_seconds": total_duration,
            "average_call_duration": total_duration / len(logs) if logs else 0
        }

    async def end_campaign(self, campaign_id: str) -> bool:
        """End campaign."""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return False
        
        campaign.status = "completed"
        campaign.end_time = datetime.utcnow()
        
        summary = await self.get_campaign_summary(campaign_id)
        logger.info(f"Campaign completed: {campaign_id} - {summary}")
        
        return True


# Global orchestrator instance
campaign_orchestrator = CampaignOrchestrator()


def get_campaign_orchestrator() -> CampaignOrchestrator:
    """Get campaign orchestrator instance."""
    return campaign_orchestrator
