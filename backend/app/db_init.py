"""
VIGNAI OS — Production Database Initialization & Migration Tool
Executes schema synchronization, migration patches, and optional demo data seeding.
Usage:
    python -m app.db_init          # Initialize schema and run migrations only
    python -m app.db_init --seed   # Initialize and seed synthetic demo data
"""
import sys
import logging
from app.config import settings
from app.database import engine, Base, run_db_migrations, check_database_connection
import app.models  # Register all models

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("db_init")


def init_database(seed_demo: bool = False):
    logger.info("Connecting to database: %s", settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL)
    
    # 1. Verify Connectivity
    if not check_database_connection():
        logger.error("Failed to connect to database. Please check DATABASE_URL credentials and network reachability.")
        sys.exit(1)
    logger.info("Database connection established successfully.")

    # 2. Create Schema
    logger.info("Synchronizing database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema tables created.")

    # 3. Run Column Migrations
    logger.info("Applying schema migration patches...")
    run_db_migrations()
    logger.info("Schema migrations applied.")

    # 4. Optional Demo Data Seeding
    should_seed = seed_demo or settings.ENABLE_DEMO_SEEDING
    if should_seed:
        logger.info("Seeding demo data (ENABLE_DEMO_SEEDING=%s)...", should_seed)
        try:
            from app.seed import run_seed
            run_seed()
            logger.info("Demo data seeding completed successfully.")
        except Exception as err:
            logger.error("Demo data seeding failed: %s", err, exc_info=True)
            sys.exit(1)
    else:
        logger.info("Production mode: Demo data seeding skipped.")

    logger.info("Database initialization complete.")


if __name__ == "__main__":
    seed_flag = "--seed" in sys.argv
    init_database(seed_demo=seed_flag)
