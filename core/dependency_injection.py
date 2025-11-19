"""
Dependency Injection Container

Enterprise-grade DI system for managing component lifecycles
and dependencies (like Spring/NestJS).
"""

import inspect
import logging
from enum import Enum
from typing import Any, Callable, Optional, Type, TypeVar, get_type_hints

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Scope(str, Enum):
    """Dependency scope/lifetime."""

    SINGLETON = "singleton"  # One instance for entire application
    TRANSIENT = "transient"  # New instance every time
    SCOPED = "scoped"  # One instance per scope (e.g., per request)


class DependencyContainer:
    """
    Dependency injection container.

    Manages component registration, resolution, and lifecycle.
    """

    def __init__(self) -> None:
        """Initialize dependency container."""
        self.singletons: dict[Type, Any] = {}
        self.factories: dict[Type, tuple[Callable, Scope]] = {}
        self.scoped_instances: dict[str, dict[Type, Any]] = {}
        self.current_scope: Optional[str] = None

    def register(
        self,
        interface: Type[T],
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
        scope: Scope = Scope.SINGLETON,
    ) -> None:
        """
        Register a dependency.

        Args:
            interface: Interface or base class
            implementation: Concrete implementation class
            factory: Factory function to create instances
            scope: Dependency scope

        Example:
            container.register(BaseAgent, GmailAgent, scope=Scope.TRANSIENT)
            container.register(EventBus, factory=lambda: EventBus(), scope=Scope.SINGLETON)
        """
        if factory:
            self.factories[interface] = (factory, scope)
        elif implementation:
            self.factories[interface] = (implementation, scope)
        else:
            self.factories[interface] = (interface, scope)

        logger.info(
            f"Registered {interface.__name__} with scope {scope.value}"
        )

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register an existing instance as singleton.

        Args:
            interface: Interface type
            instance: Instance to register
        """
        self.singletons[interface] = instance
        logger.info(f"Registered instance of {interface.__name__}")

    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a dependency.

        Args:
            interface: Interface to resolve

        Returns:
            Instance of the requested type

        Raises:
            ValueError: If dependency not registered
        """
        # Check if already instantiated as singleton
        if interface in self.singletons:
            return self.singletons[interface]

        # Check if registered
        if interface not in self.factories:
            raise ValueError(f"Dependency not registered: {interface.__name__}")

        factory, scope = self.factories[interface]

        # Handle different scopes
        if scope == Scope.SINGLETON:
            if interface not in self.singletons:
                self.singletons[interface] = self._create_instance(factory)
            return self.singletons[interface]

        elif scope == Scope.SCOPED:
            if not self.current_scope:
                raise RuntimeError("No active scope for scoped dependency")

            if self.current_scope not in self.scoped_instances:
                self.scoped_instances[self.current_scope] = {}

            if interface not in self.scoped_instances[self.current_scope]:
                self.scoped_instances[self.current_scope][interface] = (
                    self._create_instance(factory)
                )

            return self.scoped_instances[self.current_scope][interface]

        else:  # TRANSIENT
            return self._create_instance(factory)

    def _create_instance(self, factory: Callable) -> Any:
        """
        Create instance using factory with dependency injection.

        Args:
            factory: Factory function or class

        Returns:
            Created instance
        """
        # If factory is a class, inspect constructor
        if inspect.isclass(factory):
            sig = inspect.signature(factory.__init__)
            type_hints = get_type_hints(factory.__init__)

            # Resolve constructor dependencies
            kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue

                param_type = type_hints.get(param_name)
                if param_type and param_type in self.factories:
                    kwargs[param_name] = self.resolve(param_type)

            return factory(**kwargs)

        # If factory is a function, call it
        else:
            return factory()

    def create_scope(self, scope_id: str) -> "ScopeContext":
        """
        Create a new dependency scope.

        Args:
            scope_id: Unique scope identifier

        Returns:
            Scope context manager
        """
        return ScopeContext(self, scope_id)

    def clear_scope(self, scope_id: str) -> None:
        """
        Clear a dependency scope.

        Args:
            scope_id: Scope identifier to clear
        """
        if scope_id in self.scoped_instances:
            del self.scoped_instances[scope_id]
            logger.debug(f"Cleared scope: {scope_id}")

    def clear_all(self) -> None:
        """Clear all dependencies and instances."""
        self.singletons.clear()
        self.factories.clear()
        self.scoped_instances.clear()
        logger.info("Cleared all dependencies")


class ScopeContext:
    """Context manager for dependency scopes."""

    def __init__(self, container: DependencyContainer, scope_id: str) -> None:
        """
        Initialize scope context.

        Args:
            container: Dependency container
            scope_id: Scope identifier
        """
        self.container = container
        self.scope_id = scope_id
        self.previous_scope: Optional[str] = None

    def __enter__(self) -> "ScopeContext":
        """Enter scope context."""
        self.previous_scope = self.container.current_scope
        self.container.current_scope = self.scope_id
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit scope context and clean up."""
        self.container.clear_scope(self.scope_id)
        self.container.current_scope = self.previous_scope


# Decorators for dependency injection
def inject(container: DependencyContainer) -> Callable:
    """
    Decorator for automatic dependency injection.

    Args:
        container: Dependency container

    Returns:
        Decorator function

    Example:
        @inject(container)
        async def process_data(agent: BaseAgent, memory: MemoryStore):
            # Dependencies automatically injected
            pass
    """

    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)

        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Resolve dependencies
            for param_name, param in sig.parameters.items():
                if param_name not in kwargs:
                    param_type = type_hints.get(param_name)
                    if param_type and param_type in container.factories:
                        kwargs[param_name] = container.resolve(param_type)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Global container instance
_global_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """
    Get global dependency container.

    Returns:
        Global container instance
    """
    global _global_container
    if _global_container is None:
        _global_container = DependencyContainer()
    return _global_container


def configure_container(container: DependencyContainer) -> None:
    """
    Configure the global container.

    Args:
        container: Container to set as global
    """
    global _global_container
    _global_container = container
