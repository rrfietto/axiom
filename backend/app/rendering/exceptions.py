class RenderingError(Exception):
    """Base exception for the rendering layer."""


class RendererConfigurationError(RenderingError):
    """Raised when a renderer declares an invalid contract."""


class DuplicateRendererError(RendererConfigurationError):
    """Raised when two renderers use the same identifier."""


class RendererNotFoundError(RenderingError):
    """Raised when a renderer identifier is not registered."""


class ParameterValidationError(RenderingError):
    """Raised when render parameters do not satisfy the renderer contract."""


class InvalidDimensionsError(RenderingError):
    """Raised when requested image dimensions exceed safe renderer limits."""


class InvalidRendererOutputError(RenderingError):
    """Raised when a renderer returns an invalid image."""
