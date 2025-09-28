# SQL MCP Server - Docker Deployment

This repository contains a containerized SQL MCP Server that provides database interaction tools via the Model Context Protocol (MCP).

## Quick Start

### 1. Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd sql_mcp_server

# Create environment file
cp .env.example .env
# Edit .env file with your database credentials

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f sql-mcp-server
```

### 2. Using Docker directly

```bash
# Build the image
docker build -t sql-mcp-server .

# Run the container
docker run -d \
  --name sql-mcp-server \
  -p 8000:8000 \
  -e DB_SERVER="your-server" \
  -e DB_DATABASE="your-database" \
  -e DB_USER="your-username" \
  -e DB_PASSWORD="your-password" \
  sql-mcp-server
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_SERVER` | SQL Server hostname/IP | `localhost` |
| `DB_DATABASE` | Database name | `defaultdb` |
| `DB_USER` | Database username | `sa` |
| `DB_PASSWORD` | Database password | `` |
| `DB_PORT` | Database port | `1433` |
| `DB_TIMEOUT` | Connection timeout (seconds) | `15` |

## Available MCP Tools

The server exposes the following tools via MCP:

- `query_sql` - Execute SQL queries
- `list_tables` - List all tables in the database
- `describe_table` - Get table structure information
- `execute_nonquery` - Execute INSERT/UPDATE/DELETE operations
- `list_odbc_drivers` - List available ODBC drivers
- `database_info` - Get database server information

## Health Check

The container includes a health check endpoint at `http://localhost:8000/mcp`

## Security Notes

- The container runs as a non-root user for security
- Database passwords are masked in logs
- Use environment variables for sensitive configuration
- Consider using Docker secrets for production deployments

## Development

### Local Development

```bash
# Install dependencies
pip install -r pyproject.toml

# Set environment variables
export DB_SERVER="your-server"
export DB_DATABASE="your-database"
export DB_USER="your-username"
export DB_PASSWORD="your-password"

# Run the server
python sql_mcp.py
```

### Building Custom Images

```bash
# Build with custom tag
docker build -t your-registry/sql-mcp-server:latest .

# Push to registry
docker push your-registry/sql-mcp-server:latest
```

## Troubleshooting

### Common Issues

1. **Connection failures**: Check your database credentials and network connectivity
2. **ODBC driver issues**: The container includes ODBC Driver 17 for SQL Server
3. **Port conflicts**: Ensure port 8000 is available on your host

### Checking Logs

```bash
# Docker Compose
docker-compose logs sql-mcp-server

# Docker
docker logs sql-mcp-server
```

### Testing Connection

```bash
# Check if the server is responding
curl http://localhost:8000/mcp

# Enter the container for debugging
docker exec -it sql-mcp-server bash
```

## Production Deployment

For production deployments, consider:

1. Using a reverse proxy (nginx, traefik)
2. Implementing proper logging and monitoring
3. Using Docker secrets for sensitive data
4. Setting up proper backup and recovery procedures
5. Configuring resource limits and health checks

## License

[Your License Information]