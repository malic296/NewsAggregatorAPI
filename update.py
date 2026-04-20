from httpx import AsyncClient
#from logger.logging_manager import LoggerMode, LoggingManager
import asyncio
from app.core.errors import AppError
from app.core.settings import Settings
from app.core.database import create_connection_pool
from app.services.channel_service import ChannelService
from app.services.scraping_service import ScrapingService
from app.services import CacheService
from app.repositories.channel_repository import ChannelRepository


async def main() -> None:
    settings: Settings = Settings()
    db_pool = create_connection_pool(settings)
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
            print("hi")
            await channel_service.update_channels(channel_urls=settings.config.feeds, hours=settings.config.update_interval)
            print("hi")
    except Exception as e:
        print(e)
    finally:
        db_pool.close()



if __name__ == "__main__":
    #log_manager = LoggingManager(mode=LoggerMode.ALL)
    #logger = log_manager.get_logger(__name__)

    try:
        asyncio.run(main())
    except AppError as e:
        print(e)
        #logger.error(str(e))
    except Exception as e:
        print(e)
        #logger.error("Unexpected error: " + str(e))