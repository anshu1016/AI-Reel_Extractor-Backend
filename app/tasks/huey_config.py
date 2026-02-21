"""
Huey configuration for background task processing.
Uses PostgreSQL as the storage backend (no Redis needed).
"""

from huey import SqliteHuey
try:
    # Try importing SqlHuey which supports PostgreSQL via peewee
    from huey.contrib.sql_huey import SqlHuey
    from peewee import PostgresqlDatabase
except ImportError:
    # Fallback to Sqlite if peewee not available
    SqlHuey = None
    PostgresqlDatabase = None

from app.core.config import settings
from app.core.logging import get_logger
import urllib.parse

logger = get_logger(__name__)


def create_huey_instance():
    """
    Create Huey instance based on configuration.
    Uses PostgreSQL for production/shared queue, SQLite for local development.
    """
    is_production = settings.ENVIRONMENT.lower() == "production"
    
    if settings.HUEY_BACKEND == "postgresql":
        if not SqlHuey or not PostgresqlDatabase:
            msg = "PostgreSQL backend requested but 'peewee' or 'huey' sql dependencies missing. Please install huey[postgresql]."
            if is_production:
                logger.error(msg)
                # In production, we MUST not fallback silently to local SQLite if instances are separate
                raise ImportError(msg)
            else:
                logger.warning(f"{msg} Falling back to SQLite for local development.")
                return SqliteHuey(name=settings.HUEY_NAME, filename='/tmp/huey.db', immediate=settings.HUEY_IMMEDIATE)

        try:
            # Parse DATABASE_URL to get connection parameters
            parsed = urllib.parse.urlparse(settings.DATABASE_URL)
            
            # Create PEWEE database instance
            # Note: We use psycopg2-binary which is compatible with peewee.PostgresqlDatabase
            db = PostgresqlDatabase(
                parsed.path.lstrip('/'),
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                autorollback=True,
                # For Render/Production, SSL is usually required
                # if "sslmode" in settings.DATABASE_URL or is_production:
                #    connect_kwargs={'sslmode': 'require'}
            )
            
            huey = SqlHuey(
                name=settings.HUEY_NAME,
                database=db,
                immediate=settings.HUEY_IMMEDIATE,
            )
            
            logger.info(
                "Huey initialized with PostgreSQL",
                database=parsed.path.lstrip('/'),
                host=parsed.hostname
            )
            return huey
            
        except Exception as e:
            logger.error("Failed to initialize Huey with PostgreSQL", error=str(e))
            if is_production:
                # In production, a failed connection should stop the service rather than using a local disconnected queue
                raise RuntimeError(f"Could not connect Huey to PostgreSQL: {str(e)}")
            
            logger.warning("Falling back to SQLite for Huey local development.")
            return SqliteHuey(name=settings.HUEY_NAME, filename='/tmp/huey.db', immediate=settings.HUEY_IMMEDIATE)
    
    # Default to SQLite
    logger.info("Huey initialized with SQLite")
    return SqliteHuey(name=settings.HUEY_NAME, filename='/tmp/huey.db', immediate=settings.HUEY_IMMEDIATE)



# Create global Huey instance
huey = create_huey_instance()


# Huey task decorators
def task(*args, **kwargs):
    """
    Task decorator with default settings.
    
    Usage:
        @task()
        def my_task():
            pass
    """
    # Set default retry settings
    kwargs.setdefault('retries', 3)
    kwargs.setdefault('retry_delay', 60)  # 60 seconds
    
    return huey.task(*args, **kwargs)


def periodic_task(*args, **kwargs):
    """
    Periodic task decorator.
    
    Usage:
        @periodic_task(crontab(hour='0', minute='0'))
        def daily_task():
            pass
    """
    return huey.periodic_task(*args, **kwargs)