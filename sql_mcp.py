from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import logging
import sys
import pyodbc
import asyncio
from mcp.server.fastmcp import Context, FastMCP

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("server_module")

# Connection parameters
SERVER = "74.235.211.131"
DATABASE = "Demo Database NAV (7-0)"
USER = "mcp"
PASSWORD = "Qualia@321@"

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage application lifecycle with type-safe context"""
    logger.debug("Initializing database connection")
    conn = None
    
    try:
        # Connect using a loop.run_in_executor to avoid blocking
        def connect_db():
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={SERVER};"
                f"DATABASE={DATABASE};"
                f"UID={USER};"
                f"PWD={PASSWORD};"
                f"Encrypt=no;"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout=15;"
            )
            logger.debug(f"Connection string: {connection_string}")
            return pyodbc.connect(connection_string, timeout=15)
            
        loop = asyncio.get_event_loop()
        conn = await loop.run_in_executor(None, connect_db)
        logger.debug("Database connection established successfully")
        
        # Yield a dictionary instead of a dataclass to match example
        yield {"conn": conn}
    except Exception as e:
        logger.error(f"Database connection error: {type(e).__name__}: {str(e)}", exc_info=True)
        # Continue without database but with empty dict
        yield {"conn": None}
    finally:
        if conn:
            logger.debug("Closing database connection")
            await asyncio.get_event_loop().run_in_executor(None, conn.close)

# Create an MCP server with the lifespan
mcp = FastMCP("My MS SQL Integrated App", lifespan=app_lifespan)

@mcp.tool()
async def query_sql(ctx: Context, query: str | None = None) -> str:
    """
    Tool to query the SQL database with a custom query.
    
    Args:
        query: The SQL query to execute. If not provided, will run a default query.
    
    Returns:
        The query results as a string.
    """
    try:
        # Access the connection using dictionary access
        conn = ctx.request_context.lifespan_context["conn"]
        
        if conn is None:
            return "Database connection is not available. Check server logs for details."
        
        # Use default query if none provided
        if not query:
            query = "SELECT * FROM [dbo].[Table_1]"
            
        logger.debug(f"Executing query: {query}")
        
        # Execute query in a non-blocking way
        def run_query():
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                if cursor.description:  # Check if the query returns results
                    columns = [column[0] for column in cursor.description]
                    results = []
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))
                    return {"success": True, "results": results, "rowCount": len(results)}
                else:
                    # For non-SELECT queries (INSERT, UPDATE, etc.)
                    return {"success": True, "rowCount": cursor.rowcount, "message": f"Query affected {cursor.rowcount} rows"}
            except Exception as e:
                return {"success": False, "error": str(e)}
            finally:
                cursor.close()
            
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_query)
        
        if result["success"]:
            if "results" in result:
                return f"Query results: {result['results']}"
            else:
                return result["message"]
        else:
            return f"Query error: {result['error']}"
    except Exception as e:
        logger.error(f"Query execution error: {type(e).__name__}: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
async def list_tables(ctx: Context) -> str:
    """List all tables in the database that can be queried."""
    try:
        conn = ctx.request_context.lifespan_context["conn"]
        
        if conn is None:
            return "Database connection is not available."
            
        def get_tables():
            cursor = conn.cursor()
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return tables
            
        loop = asyncio.get_event_loop()
        tables = await loop.run_in_executor(None, get_tables)
        
        return f"Available tables: {tables}"
    except Exception as e:
        return f"Error listing tables: {str(e)}"

@mcp.tool()
async def describe_table(ctx: Context, table_name: str) -> str:
    """
    Get the structure of a specific table.
    
    Args:
        table_name: Name of the table to describe
        
    Returns:
        Column information for the specified table
    """
    try:
        conn = ctx.request_context.lifespan_context["conn"]
        
        if conn is None:
            return "Database connection is not available."
            
        def get_structure():
            cursor = conn.cursor()
            cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
            columns = []
            for row in cursor.fetchall():
                col_name, data_type, max_length = row
                if max_length:
                    columns.append(f"{col_name} ({data_type}({max_length}))")
                else:
                    columns.append(f"{col_name} ({data_type})")
            cursor.close()
            return columns
            
        loop = asyncio.get_event_loop()
        structure = await loop.run_in_executor(None, get_structure)
        
        if structure:
            return f"Structure of table '{table_name}':\n" + "\n".join(structure)
        else:
            return f"Table '{table_name}' not found or has no columns."
    except Exception as e:
        return f"Error describing table: {str(e)}"

@mcp.tool()
async def execute_nonquery(ctx: Context, sql: str) -> str:
    """
    Execute a non-query SQL statement (INSERT, UPDATE, DELETE, etc.).
    
    Args:
        sql: The SQL statement to execute
        
    Returns:
        Result of the operation
    """
    try:
        conn = ctx.request_context.lifespan_context["conn"]
        
        if conn is None:
            return "Database connection is not available."
            
        def run_nonquery():
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                row_count = cursor.rowcount
                # Commit changes
                conn.commit()
                cursor.close()
                return {"success": True, "rowCount": row_count}
            except Exception as e:
                # Rollback in case of error
                conn.rollback()
                return {"success": False, "error": str(e)}
            
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_nonquery)
        
        if result["success"]:
            return f"Operation successful. Rows affected: {result['rowCount']}"
        else:
            return f"Operation failed: {result['error']}"
    except Exception as e:
        return f"Error executing SQL: {str(e)}"

@mcp.tool()
async def list_odbc_drivers(ctx: Context) -> str:
    """List available ODBC drivers on the system"""
    try:
        def get_drivers():
            return pyodbc.drivers()
            
        drivers = await asyncio.get_event_loop().run_in_executor(None, get_drivers)
        return f"Available ODBC drivers: {', '.join(drivers)}"
    except Exception as e:
        return f"Error listing drivers: {str(e)}"

@mcp.tool()
async def database_info(ctx: Context) -> str:
    """Get general information about the connected database"""
    try:
        conn = ctx.request_context.lifespan_context["conn"]
        
        if conn is None:
            return "Database connection is not available."
            
        def get_info():
            cursor = conn.cursor()
            
            # Get SQL Server version
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            
            # Get database name and size
            cursor.execute("""
                SELECT 
                    DB_NAME() AS DatabaseName,
                    CONVERT(VARCHAR(50), GETDATE(), 120) AS CurrentDateTime,
                    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE') AS TableCount
            """)
            db_info = cursor.fetchone()
            
            cursor.close()
            return {
                "version": version,
                "database": db_info[0],
                "current_time": db_info[1],
                "table_count": db_info[2]
            }
            
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, get_info)
        
        return (
            f"Database Information:\n"
            f"Server: {SERVER}\n"
            f"Database: {info['database']}\n"
            f"User: {USER}\n"
            f"Server Version: {info['version'].split('\\n')[0]}\n"
            f"Current Server Time: {info['current_time']}\n"
            f"Number of Tables: {info['table_count']}"
        )
    except Exception as e:
        return f"Error getting database info: {str(e)}"

# Run the server
if __name__ == "__main__":
    try:
        logger.info("Starting MCP server")
        mcp.run()
    except Exception as e:
        logger.critical(f"Server startup failed: {e}", exc_info=True)
        sys.exit(1)