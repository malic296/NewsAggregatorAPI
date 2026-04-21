from httpx import AsyncClient
import asyncio
from app.core.errors import AppError
from app.core.settings import Settings
from app.core.database import create_connection_pool
from app.services.channel_service import ChannelService
from app.services.scraping_service import ScrapingService
from app.services import CacheService
from app.repositories.channel_repository import ChannelRepository
from app.core.logger.handlers import DropOnFailHandler, DatabaseHandler
from app.repositories import LoggingRepository
import logging

async def main() -> None:
    settings: Settings = Settings()
    db_pool = create_connection_pool(settings)
    logging_repo = LoggingRepository(connection_pool=db_pool)
    db_handler = DatabaseHandler(writer_func=logging_repo.log_to_db)
    db_wrapper = DropOnFailHandler(db_handler)
    logging.getLogger().addHandler(db_wrapper)

    logger = logging.getLogger(__name__)
    logger.info("update.py started.")

    try:
        async with AsyncClient(timeout=5.0) as client:
            scraping_service = ScrapingService(client)
            channel_service = ChannelService(
                channels=ChannelRepository(connection_pool=db_pool),
                cache=CacheService(
                    settings.valkey_host,
                    settings.valkey_port,
                    settings.valkey_db
                ),
                scraping_service=scraping_service
            )
            logger.info("Dependencies loaded.")

            await channel_service.update_channels(channel_urls=settings.config.feeds, hours=settings.config.update_interval)

            logger.info("Channels and articles updated.")

    except AppError as e:
        logging.getLogger(__name__).error(e.internal_message, extra={'exception': e})
    except Exception as e:
        logging.getLogger(__name__).error("UNEXPECTED ERROR: " + str(e), extra={'exception': e})
    finally:
        db_pool.close()

if __name__ == "__main__":
    asyncio.run(main())
