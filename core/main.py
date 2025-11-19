"""
AUTOCOM - Main Application Entry Point

Initializes all components and starts the application.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

from core.event_bus import EventBus
from core.llm import LocalLLM
from core.orchestrator import Orchestrator
from database.memory import MemoryStore

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/autocom.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class AutocomApp:
    """Main application class for AUTOCOM."""

    def __init__(self) -> None:
        """Initialize the application."""
        self.config: dict = {}
        self.event_bus: Optional[EventBus] = None
        self.orchestrator: Optional[Orchestrator] = None
        self.memory: Optional[MemoryStore] = None
        self.llm: Optional[LocalLLM] = None
        self.running = False

    async def initialize(self) -> None:
        """Initialize all application components."""
        logger.info("Initializing AUTOCOM...")

        # Load environment variables
        load_dotenv()

        # Load configuration
        self.config = self._load_config()

        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        Path("memory").mkdir(exist_ok=True)

        # Initialize core components
        self.event_bus = EventBus()
        await self.event_bus.start()

        self.memory = MemoryStore(self.config["database"]["path"])
        await self.memory.initialize()

        self.llm = LocalLLM(
            model=self.config["orchestrator"]["llm_model"],
            endpoint=self.config["orchestrator"]["llm_endpoint"],
            temperature=self.config["orchestrator"]["temperature"],
            max_tokens=self.config["orchestrator"]["max_tokens"],
        )

        self.orchestrator = Orchestrator(
            llm=self.llm,
            memory=self.memory,
            event_bus=self.event_bus,
            confidence_threshold=self.config["orchestrator"]["confidence_threshold"],
        )

        # TODO: Initialize agents
        # TODO: Initialize voice pipeline
        # TODO: Initialize UI

        logger.info("AUTOCOM initialized successfully")

    def _load_config(self) -> dict:
        """
        Load configuration from YAML files.

        Returns:
            Merged configuration dictionary
        """
        config_path = Path("config/config.yaml")
        if not config_path.exists():
            logger.error("Configuration file not found: config/config.yaml")
            sys.exit(1)

        with open(config_path) as f:
            config = yaml.safe_load(f)

        logger.info("Configuration loaded")
        return config

    async def run(self) -> None:
        """Run the main application loop."""
        self.running = True
        logger.info("AUTOCOM is running...")

        try:
            # Keep the application running
            while self.running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        """Gracefully shutdown all components."""
        logger.info("Shutting down AUTOCOM...")
        self.running = False

        if self.event_bus:
            await self.event_bus.stop()

        if self.memory:
            await self.memory.close()

        if self.llm:
            await self.llm.close()

        logger.info("AUTOCOM shutdown complete")

    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(sig: int, frame: any) -> None:
            logger.info(f"Received signal {sig}")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main() -> None:
    """Main entry point."""
    app = AutocomApp()
    app.setup_signal_handlers()

    try:
        await app.initialize()
        await app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
