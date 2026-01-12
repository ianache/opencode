# Docker Compose for GraphRAG Neo4j Setup

This directory contains Docker Compose configuration for running Neo4j as part of the GraphRAG project.

## Quick Start

1. **Ensure you have Docker and Docker Compose installed**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Configure your environment**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred Neo4j credentials
   ```

3. **Start Neo4j service**
   ```bash
   docker-compose up -d
   ```

4. **Verify the service is running**
   ```bash
   docker-compose ps
   docker-compose logs neo4j
   ```

5. **Access Neo4j Browser**
   - Open your web browser
   - Navigate to: http://localhost:7474
   - Login with credentials from your .env file

## Configuration

The `docker-compose.yaml` includes:

### Services
- **neo4j**: Neo4j 5.26 Community Edition with optimized settings

### Ports
- `7474`: HTTP interface (Neo4j Browser)
- `7687`: Bolt protocol (application connections)
- Both are bound to `127.0.0.1` for security (localhost only)

### Volumes
- `neo4j_data`: Persistent database storage
- `neo4j_logs`: Neo4j log files
- `neo4j_import`: CSV import directory
- `neo4j_plugins`: Neo4j plugins directory

### Environment Variables
- Memory settings optimized for development
- Security configurations for Graph Data Science and APOC plugins
- Query logging enabled for debugging

## Usage Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs neo4j
docker-compose logs -f neo4j  # Follow logs
```

### Access Container Shell
```bash
docker-compose exec neo4j bash
```

### Run Cypher Shell
```bash
docker-compose exec neo4j cypher-shell -u neo4j -p your_password
```

### Import CSV Files
Place your CSV files in a local directory and mount it to the import volume:
```bash
# Modify docker-compose.yaml to add:
# - ./your-data-directory:/var/lib/neo4j/import-data

# Then import using Cypher:
# LOAD CSV WITH HEADERS FROM 'file:///import-data/your-file.csv' AS row...
```

## Data Persistence

All Neo4j data is persisted in Docker volumes:
- Database files survive container restarts
- Configuration changes don't affect stored data
- To completely reset: `docker-compose down -v` (removes all data)

## Security Notes

- Ports are bound to localhost only (127.0.0.1)
- Change the default password in your .env file
- For production, consider additional security measures
- Backup volumes regularly using `docker run --rm -v neo4j_data:/data -v $(pwd):/backup alpine tar czf /backup/neo4j-backup.tar.gz -C /data .`

## Troubleshooting

### Container Won't Start
- Check .env file has all required variables
- Verify ports aren't in use: `netstat -an | grep 7474`
- View logs: `docker-compose logs neo4j`

### Connection Issues
- Ensure Neo4j is fully started (wait ~30 seconds)
- Check URI in application: `bolt://localhost:7687`
- Verify credentials match .env file

### Performance Issues
- Adjust memory settings in docker-compose.yaml
- Monitor resource usage: `docker stats`
- Consider increasing heap size for larger datasets

## Integration with GraphRAG Application

Once Neo4j is running, your GraphRAG application will automatically connect using the configuration in your `.env` file:

```python
from config.settings import get_settings
settings = get_settings()
# Uses NEO4J_URI=bolt://localhost:7687 from .env
```