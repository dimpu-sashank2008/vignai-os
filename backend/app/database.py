from pathlib import Path
import sqlite3
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

BACKEND_DIR = Path(__file__).resolve().parent.parent

def get_database_url() -> str:
    url = settings.DATABASE_URL
    # Normalize PostgreSQL URL if provided by cloud platforms (e.g. Render, Heroku)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # SQLite relative path resolution
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////") and ":memory:" not in url:
        rel_path = url.replace("sqlite:///", "")
        if rel_path.startswith("./"):
            rel_path = rel_path[2:]
        abs_db_path = (BACKEND_DIR / rel_path).resolve()
        return f"sqlite:///{abs_db_path}"
    return url

db_url = get_database_url()

if db_url.startswith("sqlite"):
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
    )
else:
    # Production PostgreSQL / External SQL with connection pooling
    engine = create_engine(
        db_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_database_connection() -> bool:
    """Verify live database connectivity via simple ping query."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def run_db_migrations():
    """Ensure database tables have all required columns across dialects."""
    with engine.connect() as conn:
        inspector = inspect(engine)
        if "complaint_ai_analyses" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("complaint_ai_analyses")]
            if "department" not in columns:
                conn.execute(text("ALTER TABLE complaint_ai_analyses ADD COLUMN department VARCHAR(100)"))
            if "suggested_route_type" not in columns:
                conn.execute(text("ALTER TABLE complaint_ai_analyses ADD COLUMN suggested_route_type VARCHAR(50)"))
            if "sensitivity" not in columns:
                conn.execute(text("ALTER TABLE complaint_ai_analyses ADD COLUMN sensitivity VARCHAR(50) DEFAULT 'NORMAL'"))
            if "routing_reason" not in columns:
                conn.execute(text("ALTER TABLE complaint_ai_analyses ADD COLUMN routing_reason TEXT"))
            conn.commit()

        if "users" in inspector.get_table_names():
            user_columns = [col["name"] for col in inspector.get_columns("users")]
        if "opportunities" in inspector.get_table_names():
            opp_columns = [col["name"] for col in inspector.get_columns("opportunities")]
            if "source_name" not in opp_columns:
                conn.execute(text("ALTER TABLE opportunities ADD COLUMN source_name VARCHAR(100) DEFAULT 'VIGNAI Development Partner'"))
            if "source_type" not in opp_columns:
                conn.execute(text("ALTER TABLE opportunities ADD COLUMN source_type VARCHAR(50) DEFAULT 'SYNTHETIC_DEVELOPMENT'"))
            if "verification_status" not in opp_columns:
                conn.execute(text("ALTER TABLE opportunities ADD COLUMN verification_status VARCHAR(50) DEFAULT 'VERIFIED'"))
            if "lifecycle_status" not in opp_columns:
                conn.execute(text("ALTER TABLE opportunities ADD COLUMN lifecycle_status VARCHAR(50) DEFAULT 'ACTIVE'"))
            if "submitted_by_id" not in opp_columns:
                conn.execute(text("ALTER TABLE opportunities ADD COLUMN submitted_by_id INTEGER"))
            if "submitted_at" not in opp_columns:
                conn.execute(text("ALTER TABLE opportunities ADD COLUMN submitted_at DATETIME"))
            if "verified_by_id" not in opp_columns:
                conn.execute(text("ALTER TABLE opportunities ADD COLUMN verified_by_id INTEGER"))
            if "verified_at" not in opp_columns:
                conn.execute(text("ALTER TABLE opportunities ADD COLUMN verified_at DATETIME"))
            if "fingerprint" not in opp_columns:
                conn.execute(text("ALTER TABLE opportunities ADD COLUMN fingerprint VARCHAR(64)"))
            if "raw_content" not in opp_columns:
                conn.execute(text("ALTER TABLE opportunities ADD COLUMN raw_content TEXT"))
        if "notifications" in inspector.get_table_names():
            notif_columns = [col["name"] for col in inspector.get_columns("notifications")]
            if "notification_type" not in notif_columns:
                conn.execute(text("ALTER TABLE notifications ADD COLUMN notification_type VARCHAR(50) DEFAULT 'GENERAL'"))
            if "target_route" not in notif_columns:
                conn.execute(text("ALTER TABLE notifications ADD COLUMN target_route VARCHAR(255)"))
            if "target_entity_type" not in notif_columns:
                conn.execute(text("ALTER TABLE notifications ADD COLUMN target_entity_type VARCHAR(50)"))
            if "target_entity_id" not in notif_columns:
                conn.execute(text("ALTER TABLE notifications ADD COLUMN target_entity_id VARCHAR(100)"))
            if "target_anchor" not in notif_columns:
                conn.execute(text("ALTER TABLE notifications ADD COLUMN target_anchor VARCHAR(100)"))
            if "target_query" not in notif_columns:
                conn.execute(text("ALTER TABLE notifications ADD COLUMN target_query VARCHAR(255)"))
            if "source_action_id" not in notif_columns:
                conn.execute(text("ALTER TABLE notifications ADD COLUMN source_action_id INTEGER"))
            if "source_insight_id" not in notif_columns:
                conn.execute(text("ALTER TABLE notifications ADD COLUMN source_insight_id INTEGER"))
            if "source_alert_id" not in notif_columns:
                conn.execute(text("ALTER TABLE notifications ADD COLUMN source_alert_id INTEGER"))
            conn.commit()

        # Create any new tables (e.g. opportunity_sources)
        Base.metadata.create_all(bind=engine)
