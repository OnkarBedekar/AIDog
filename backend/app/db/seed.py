"""Seed script for demo data."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, init_db
from app.db.models import User, Incident, Recommendation, MemoryProfile, OrgConfig
from app.services.memory_service import MemoryService
from datetime import datetime, timedelta
import bcrypt
import json


def seed_database():
    """Seed database with demo data."""
    db: Session = SessionLocal()

    try:
        # Initialize database
        init_db()

        # Create org config
        org_config = db.query(OrgConfig).first()
        if not org_config:
            org_config = OrgConfig(
                datadog_site="us3.datadoghq.com",
                default_time_window=3600,
                tags_of_interest=["env:production", "service:user-service", "service:payment-service"],
            )
            db.add(org_config)
            db.commit()

        # Create demo users
        # Default password for demo users: "password123"
        default_password_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()
        demo_users = [
            {"email": "sre@example.com", "role": "SRE", "password_hash": default_password_hash},
            {"email": "backend@example.com", "role": "Backend", "password_hash": default_password_hash},
            {"email": "ml@example.com", "role": "ML", "password_hash": default_password_hash},
            {"email": "product@example.com", "role": "Product", "password_hash": default_password_hash},
        ]

        users = []
        for user_data in demo_users:
            user = db.query(User).filter(User.email == user_data["email"]).first()
            if not user:
                user = User(**user_data)
                db.add(user)
                db.commit()
                db.refresh(user)

                # Create memory profile
                memory_service = MemoryService(db)
                memory_profile = memory_service.get_or_create_memory_profile(user.id)

                # Add some initial patterns
                memory_profile.patterns = [
                    {
                        "id": "pattern_001",
                        "description": "Always checks traces before logs for latency issues",
                        "confidence": 85,
                        "frequency": 5,
                    },
                    {
                        "id": "pattern_002",
                        "description": "Prefers conservative recommendations",
                        "confidence": 90,
                        "frequency": 8,
                    },
                ]

                # Add some shortcuts
                memory_profile.shortcuts = [
                    {"id": "shortcut_001", "name": "Check DB latency", "action": "query_metrics", "params": {"query": "p95:db.query.duration"}},
                    {"id": "shortcut_002", "name": "View error logs", "action": "search_logs", "params": {"query": "level:error"}},
                ]

                db.commit()

            users.append(user)

        # Create demo incidents
        incidents_data = [
            {
                "source": "datadog",
                "title": "High Error Rate - user-service",
                "severity": "critical",
                "services": ["user-service", "database"],
                "state": "open",
                "monitor_id": "mon_001",
                "started_at": datetime.now() - timedelta(hours=2),
            },
            {
                "source": "datadog",
                "title": "P95 Latency Spike - payment-service",
                "severity": "warning",
                "services": ["payment-service", "database"],
                "state": "investigating",
                "monitor_id": "mon_002",
                "started_at": datetime.now() - timedelta(minutes=30),
            },
            {
                "source": "datadog",
                "title": "Database Connection Pool Exhausted",
                "severity": "critical",
                "services": ["database"],
                "state": "open",
                "monitor_id": "mon_003",
                "started_at": datetime.now() - timedelta(hours=1),
            },
            {
                "source": "datadog",
                "title": "LLM Quality Score Drop",
                "severity": "warning",
                "services": ["llm-service", "retrieval-service"],
                "state": "resolved",
                "monitor_id": "mon_004",
                "started_at": datetime.now() - timedelta(days=1),
            },
        ]

        incidents = []
        for inc_data in incidents_data:
            incident = db.query(Incident).filter(
                Incident.title == inc_data["title"]
            ).first()

            if not incident:
                incident = Incident(**inc_data)
                db.add(incident)
                db.commit()
                db.refresh(incident)

            incidents.append(incident)

        # Create demo recommendations
        recommendations_data = [
            {
                "user_id": users[0].id,
                "incident_id": incidents[0].id,
                "type": "monitor_tune",
                "content": {
                    "title": "Tune error rate threshold",
                    "description": "Adjust threshold from 10 to 8 to catch issues earlier",
                    "export_payload": {
                        "type": "monitor_tune",
                        "payload": {
                            "monitor_id": "mon_001",
                            "threshold": 8,
                        },
                        "cli_snippet": "datadog monitor update mon_001 --threshold 8",
                    },
                },
                "confidence": 75,
                "status": "proposed",
            },
            {
                "user_id": users[0].id,
                "incident_id": incidents[1].id,
                "type": "dashboard",
                "content": {
                    "title": "Create latency correlation dashboard",
                    "description": "Dashboard showing latency vs error rate correlation",
                    "export_payload": {
                        "type": "dashboard",
                        "payload": {
                            "title": "Latency Correlation",
                            "widgets": [],
                        },
                    },
                },
                "confidence": 80,
                "status": "proposed",
            },
            {
                "user_id": users[0].id,
                "incident_id": incidents[2].id,
                "type": "slo",
                "content": {
                    "title": "Define database connection pool SLO",
                    "description": "SLO: 99.9% of requests have available connection",
                    "export_payload": {
                        "type": "slo",
                        "payload": {
                            "name": "DB Connection Pool Availability",
                            "target": 99.9,
                        },
                    },
                },
                "confidence": 85,
                "status": "accepted",
            },
        ]

        for rec_data in recommendations_data:
            recommendation = db.query(Recommendation).filter(
                Recommendation.user_id == rec_data["user_id"],
                Recommendation.incident_id == rec_data["incident_id"],
                Recommendation.type == rec_data["type"],
            ).first()

            if not recommendation:
                recommendation = Recommendation(**rec_data)
                db.add(recommendation)
                db.commit()

        print("Database seeded successfully!")
        print(f"Created {len(users)} users")
        print(f"Created {len(incidents)} incidents")
        print(f"Created {len(recommendations_data)} recommendations")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
