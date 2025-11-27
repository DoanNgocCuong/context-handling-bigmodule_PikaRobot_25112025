"""
Color logging utilities specifically for RabbitMQ worker.

Provides worker-specific colored log formatting for better visibility.
"""
from app.utils.color_log import (
    Colors,
    colorize,
    success,
    error,
    warning,
    info,
    debug,
    key_value,
    _supports_color,
)


def worker_start(message: str) -> str:
    """Green color for worker startup messages."""
    return f"{success('🚀')} {success(message)}"


def worker_stop(message: str) -> str:
    """Yellow color for worker shutdown messages."""
    return f"{warning('🛑')} {warning(message)}"


def worker_connected(message: str) -> str:
    """Cyan color for connection success."""
    return f"{success('✅')} {info(message)}"


def worker_error(message: str) -> str:
    """Red color for worker errors."""
    return f"{error('❌')} {error(message)}"


def queue_info(queue_name: str, action: str = "connected") -> str:
    """Format queue information with colors."""
    if not _supports_color():
        return f"Queue: {queue_name} | Action: {action}"
    
    queue_colored = colorize(queue_name, Colors.BRIGHT_MAGENTA, bold=True)
    action_colored = colorize(action, Colors.BRIGHT_CYAN)
    return f"Queue: {queue_colored} | Action: {action_colored}"


def message_received(conversation_id: str) -> str:
    """Format message received log."""
    return (
        f"📥 {info('Processing conversation from queue')} | "
        f"{key_value('conversation_id', conversation_id)}"
    )


def message_processed(conversation_id: str, processed: int, failed: int = 0) -> str:
    """Format message processed log."""
    if failed > 0:
        return (
            f"{warning('⚠️  Partially processed')} | "
            f"{key_value('conversation_id', conversation_id)} | "
            f"{key_value('processed', str(processed))} | "
            f"{key_value('failed', str(failed))}"
        )
    else:
        return (
            f"{success('✅ Successfully processed conversation')} | "
            f"{key_value('conversation_id', conversation_id)} | "
            f"{key_value('processed', str(processed))}"
        )


def message_failed(conversation_id: str, error_msg: str) -> str:
    """Format message failed log."""
    return (
        f"{error('❌ Failed to process conversation')} | "
        f"{key_value('conversation_id', conversation_id)} | "
        f"{key_value('error', error_msg)}"
    )


def consumer_starting() -> str:
    """Format consumer starting log."""
    return f"{info('🔄')} {info('Starting RabbitMQ consumer...')}"


def consumer_stopping() -> str:
    """Format consumer stopping log."""
    return f"{warning('🛑')} {warning('Stopping consumer...')}"


def consumer_stopped() -> str:
    """Format consumer stopped log."""
    return f"{success('✅')} {success('Consumer stopped')}"


def connection_closed() -> str:
    """Format connection closed log."""
    return f"{info('🔌')} {info('Closed RabbitMQ consumer connection')}"


def retry_info(attempt: int, max_attempts: int, next_retry: str) -> str:
    """Format retry information."""
    return (
        f"{warning('🔄 Retry')} | "
        f"{key_value('attempt', f'{attempt}/{max_attempts}')} | "
        f"{key_value('next_retry', next_retry)}"
    )


def db_operation_color(operation: str, table: str = "") -> str:
    """Color database operations for worker logs."""
    from app.utils.color_log import db_operation
    
    op_colored = db_operation(operation)
    if table and _supports_color():
        table_colored = colorize(table, Colors.BRIGHT_BLUE)
        return f"{op_colored} {table_colored}"
    return op_colored


def processing_status(status: str) -> str:
    """Color processing status."""
    status_colors = {
        "PROCESSING": Colors.BRIGHT_YELLOW,
        "PROCESSED": Colors.BRIGHT_GREEN,
        "FAILED": Colors.BRIGHT_RED,
        "PENDING": Colors.BRIGHT_CYAN,
    }
    
    color = status_colors.get(status.upper(), Colors.WHITE)
    if not _supports_color():
        return status
    
    return colorize(status, color, bold=True)

