"""Audit logging with SQLite for command history tracking."""

import aiosqlite
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from .logger import get_logger

logger = get_logger(__name__)


class AuditLogger:
    """SQLite-based audit logger for tracking command execution history."""

    def __init__(self, db_path: str = "audit.db"):
        """Initialize audit logger with database path."""
        # Convert to absolute path, defaulting to the package directory
        if not os.path.isabs(db_path):
            # Get the directory where this module is located
            module_dir = Path(__file__).parent.parent.resolve()
            self.db_path = module_dir / db_path
        else:
            self.db_path = Path(db_path)

        logger.info(f"AuditLogger initialized with database: {self.db_path}")

    async def init_db(self) -> None:
        """Initialize audit database schema."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS command_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        device_id TEXT NOT NULL,
                        device_name TEXT,
                        device_host TEXT,
                        command TEXT NOT NULL,
                        success BOOLEAN NOT NULL,
                        output TEXT,
                        error TEXT,
                        execution_time_ms REAL,
                        connection_type TEXT,
                        user_context TEXT
                    )
                """)

                # Create indexes for faster queries
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_device_id
                    ON command_history(device_id)
                """)

                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp
                    ON command_history(timestamp DESC)
                """)

                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_success
                    ON command_history(success)
                """)

                await db.commit()
                logger.info("Audit database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize audit database: {e}")
            raise

    async def log_command(
        self,
        device_id: str,
        command: str,
        success: bool,
        output: Optional[str] = None,
        error: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        device_name: Optional[str] = None,
        device_host: Optional[str] = None,
        connection_type: Optional[str] = None,
        user_context: Optional[str] = None
    ) -> None:
        """
        Log command execution to audit database.

        Args:
            device_id: Device identifier
            command: Command that was executed
            success: Whether command succeeded
            output: Command output (optional)
            error: Error message if failed (optional)
            execution_time_ms: Execution time in milliseconds (optional)
            device_name: Human-readable device name (optional)
            device_host: Device hostname/IP (optional)
            connection_type: Connection type (ssh/telnet/api) (optional)
            user_context: User or context info (optional)
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO command_history
                    (timestamp, device_id, device_name, device_host, command,
                     success, output, error, execution_time_ms, connection_type, user_context)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    device_id,
                    device_name,
                    device_host,
                    command,
                    success,
                    output,
                    error,
                    execution_time_ms,
                    connection_type,
                    user_context
                ))
                await db.commit()

                logger.debug(f"Logged command to audit: {device_id} - {command[:50]}...")

        except Exception as e:
            logger.error(f"Failed to log command to audit database: {e}")
            # Don't raise - audit logging should not break main functionality

    async def get_history(
        self,
        device_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        success_only: Optional[bool] = None,
        failed_only: Optional[bool] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> list[dict]:
        """
        Get command history with optional filters.

        Args:
            device_id: Filter by device ID (optional)
            limit: Maximum number of records to return
            offset: Number of records to skip
            success_only: Only return successful commands
            failed_only: Only return failed commands
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)

        Returns:
            List of command history records as dictionaries
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                # Build query with filters
                query = "SELECT * FROM command_history WHERE 1=1"
                params = []

                if device_id:
                    query += " AND device_id = ?"
                    params.append(device_id)

                if success_only:
                    query += " AND success = 1"
                elif failed_only:
                    query += " AND success = 0"

                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date)

                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date)

                query += " ORDER BY id DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()

                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to retrieve command history: {e}")
            return []

    async def get_device_stats(self, device_id: str) -> dict:
        """
        Get statistics for a specific device.

        Args:
            device_id: Device identifier

        Returns:
            Dictionary with device statistics
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total commands
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM command_history WHERE device_id = ?",
                    (device_id,)
                )
                total_commands = (await cursor.fetchone())[0]

                # Successful commands
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM command_history WHERE device_id = ? AND success = 1",
                    (device_id,)
                )
                successful_commands = (await cursor.fetchone())[0]

                # Failed commands
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM command_history WHERE device_id = ? AND success = 0",
                    (device_id,)
                )
                failed_commands = (await cursor.fetchone())[0]

                # Average execution time
                cursor = await db.execute(
                    "SELECT AVG(execution_time_ms) FROM command_history WHERE device_id = ? AND execution_time_ms IS NOT NULL",
                    (device_id,)
                )
                avg_execution_time = (await cursor.fetchone())[0] or 0.0

                # First and last command timestamps
                cursor = await db.execute(
                    "SELECT MIN(timestamp), MAX(timestamp) FROM command_history WHERE device_id = ?",
                    (device_id,)
                )
                first_timestamp, last_timestamp = await cursor.fetchone()

                return {
                    "device_id": device_id,
                    "total_commands": total_commands,
                    "successful_commands": successful_commands,
                    "failed_commands": failed_commands,
                    "success_rate": successful_commands / total_commands if total_commands > 0 else 0.0,
                    "avg_execution_time_ms": round(avg_execution_time, 2),
                    "first_command_at": first_timestamp,
                    "last_command_at": last_timestamp
                }

        except Exception as e:
            logger.error(f"Failed to get device stats: {e}")
            return {
                "device_id": device_id,
                "error": str(e)
            }

    async def get_recent_errors(self, device_id: Optional[str] = None, limit: int = 10) -> list[dict]:
        """
        Get recent failed commands.

        Args:
            device_id: Filter by device ID (optional)
            limit: Maximum number of errors to return

        Returns:
            List of recent error records
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                if device_id:
                    cursor = await db.execute("""
                        SELECT * FROM command_history
                        WHERE device_id = ? AND success = 0
                        ORDER BY id DESC LIMIT ?
                    """, (device_id, limit))
                else:
                    cursor = await db.execute("""
                        SELECT * FROM command_history
                        WHERE success = 0
                        ORDER BY id DESC LIMIT ?
                    """, (limit,))

                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get recent errors: {e}")
            return []

    async def get_command_frequency(self, device_id: Optional[str] = None, limit: int = 10) -> list[dict]:
        """
        Get most frequently executed commands.

        Args:
            device_id: Filter by device ID (optional)
            limit: Maximum number of results to return

        Returns:
            List of commands with execution counts
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                if device_id:
                    cursor = await db.execute("""
                        SELECT command, COUNT(*) as count,
                               SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                               AVG(execution_time_ms) as avg_time_ms
                        FROM command_history
                        WHERE device_id = ?
                        GROUP BY command
                        ORDER BY count DESC
                        LIMIT ?
                    """, (device_id, limit))
                else:
                    cursor = await db.execute("""
                        SELECT command, COUNT(*) as count,
                               SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                               AVG(execution_time_ms) as avg_time_ms
                        FROM command_history
                        GROUP BY command
                        ORDER BY count DESC
                        LIMIT ?
                    """, (limit,))

                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get command frequency: {e}")
            return []

    async def clear_old_records(self, days: int = 90) -> int:
        """
        Clear audit records older than specified days.

        Args:
            days: Number of days to keep (default: 90)

        Returns:
            Number of deleted records
        """
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            cutoff_iso = cutoff_date.isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "DELETE FROM command_history WHERE timestamp < ?",
                    (cutoff_iso,)
                )
                await db.commit()
                deleted_count = cursor.rowcount

                logger.info(f"Cleared {deleted_count} audit records older than {days} days")
                return deleted_count

        except Exception as e:
            logger.error(f"Failed to clear old records: {e}")
            return 0

    async def export_to_csv(self, output_path: str, device_id: Optional[str] = None) -> bool:
        """
        Export audit history to CSV file.

        Args:
            output_path: Path to output CSV file
            device_id: Filter by device ID (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            import csv

            records = await self.get_history(device_id=device_id, limit=100000)

            if not records:
                logger.warning("No records to export")
                return False

            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = records[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for record in records:
                    writer.writerow(record)

            logger.info(f"Exported {len(records)} records to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            return False
