# MCP SQL Server

A FastMCP server that provides SQL database interaction tools via a conversational AI interface.

## Overview

This project creates a server that exposes MS SQL Server operations through a conversational AI interface. It uses the FastMCP framework to provide tools for querying and manipulating SQL data, allowing users to interact with databases using natural language.

## Features

- Execute SQL queries and view results
- List available tables in the database
- Describe table structure with column information
- Execute non-query operations (INSERT, UPDATE, DELETE)
- List available ODBC drivers on the system
- View database information and server details

## Requirements

- Python 3.7+
- pyodbc
- asyncio
- FastMCP framework
- Microsoft SQL Server
- ODBC Driver 17 for SQL Server

## Installation

1. Install Python dependencies:

```bash
pip install pyodbc asyncio fastmcp
```

2. Ensure you have Microsoft SQL Server installed and the ODBC Driver 17 for SQL Server.

3. Configure the connection settings in the script:

```python
# Connection parameters
SERVER = "server\\instance"  # Change to your SQL Server instance
DATABASE = "db_name"              # Change to your database name
```

## Usage

Run the server:

```bash
python mcp_sql_server.py
```

The server will initialize and establish a connection to the specified SQL Server database.

## Available Tools

### query_sql

Execute a SQL query and return the results.

```
query_sql(query: str = None) -> str
```

- If no query is provided, it defaults to `SELECT * FROM [dbo].[Table_1]`
- Returns query results as a formatted string

### list_tables

List all tables available in the database.

```
list_tables() -> str
```

- Returns a list of table names as a string

### describe_table

Get the structure of a specific table.

```
describe_table(table_name: str) -> str
```

- `table_name`: Name of the table to describe
- Returns column information including names and data types

### execute_nonquery

Execute INSERT, UPDATE, DELETE or other non-query SQL statements.

```
execute_nonquery(sql: str) -> str
```

- `sql`: The SQL statement to execute
- Returns operation results, including number of affected rows
- Automatically handles transactions (commit/rollback)

### list_odbc_drivers

List all available ODBC drivers on the system.

```
list_odbc_drivers() -> str
```

- Returns a comma-separated list of installed ODBC drivers

### database_info

Get general information about the connected database.

```
database_info() -> str
```

- Returns server name, database name, SQL Server version, current server time, and table count

## Architecture

The server uses an asynchronous architecture to avoid blocking operations:

1. **Lifecycle Management**: The `app_lifespan` context manager handles database connection setup and teardown.

2. **Non-blocking Operations**: Database operations run in a separate thread using `asyncio.get_event_loop().run_in_executor()` to prevent blocking the main event loop.

3. **Error Handling**: All operations include comprehensive error handling with useful error messages.

## Error Handling

The server handles various error conditions:

- Database connection failures
- SQL query syntax errors
- Table not found errors
- Permission-related issues

All errors are logged and appropriate error messages are returned to the client.

## Customization

To add new database tools or modify existing ones, follow the pattern used in the existing tools:

```python
@mcp.tool()
async def your_new_tool(ctx: Context, param1: str) -> str:
    """Documentation for your tool"""
    try:
        conn = ctx.request_context.lifespan_context["conn"]
        
        if conn is None:
            return "Database connection is not available."
            
        def your_db_operation():
            # Your database operations here
            pass
            
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, your_db_operation)
        
        # Process and return results
        return "Your result"
    except Exception as e:
        return f"Error: {str(e)}"
```

## Security Considerations

- The server uses Windows Authentication ("Trusted_Connection=yes")
- Consider implementing input validation for SQL queries to prevent SQL injection
- Restrict database user permissions based on the principle of least privilege

## Troubleshooting

Common issues:

1. **Connection errors**: Verify the SQL Server instance name and ensure it's running
2. **ODBC driver errors**: Confirm ODBC Driver 17 for SQL Server is installed
3. **Permission errors**: Check that the Windows user running the application has appropriate SQL Server permissions

## License

[Your License Information]

## Contact

[Your Contact Information]
