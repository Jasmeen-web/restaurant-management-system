"""Custom exceptions for the restaurant system."""


class RestaurantError(Exception):
    """Base exception for domain-specific application errors."""


class ValidationError(RestaurantError):
    """Raised when user input or stored data is invalid."""


class NotFoundError(RestaurantError):
    """Raised when the requested entity does not exist."""


class StockError(RestaurantError):
    """Raised when there is not enough stock to complete an action."""
