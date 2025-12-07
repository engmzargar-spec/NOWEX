from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from backend.core.database.base import Base

class UserScoreSnapshot(Base):
    __tablename__ = "user_score_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    
    # snapshot data
    total_score = Column(Integer)
    level = Column(String(20))
    score_breakdown = Column(JSON)
    
    # metadata
    snapshot_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "total_score": self.total_score,
            "level": self.level,
            "score_breakdown": self.score_breakdown,
            "snapshot_date": self.snapshot_date.isoformat() if self.snapshot_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
