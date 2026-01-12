# Product Management MCP Server

Feature 2 implementation that provides an MCP API for managing products and their functionalities using FastMCP with SSE transport and JWT authentication.

## Architecture

```
┌─────────────┐    1. Request JWT    ┌────────────────┐
│    Consumer   │ ───────────────────► │  FastMCP      │
└─────────────┘    with token JWT    │   Server        │
                                      └────────────────┘
                                             │
                                             │ 3. Validate token JWT
                                             ▼
                                      ┌────────────────┐
                                      │  FastMCP      │
                                      │   Server        │
                                      └────────────────┘
                                             │ 4. Cypher Queries
                                             ▼
                                      ┌────────────────┐
                                      │     Neo4J      │
                                      └────────────────┘
```

## Features

### ✅ Core Functionality
- **Product Management**: Create, read, update, delete products
- **Functionality Management**: Register and assign functionalities to products
- **Search & Discovery**: Full-text search and resource-based discovery
- **Authentication**: JWT-based security with configurable policies
- **Validation**: Comprehensive input validation with Spanish error messages

### 🔧 MCP Tools
- `register_product(code, name, functionalities)` - Register new product
- `get_product_details(product_code)` - Get product with functionalities
- `update_product(product_code, updates)` - Update product information
- `delete_product(product_code)` - Delete product and relationships
- `list_products(limit, offset)` - Paginated product listing
- `search_products(query, limit)` - Search products by name/code
- `register_functionality(code, name)` - Register functionality
- `assign_functionalities_to_product(product_code, functionality_codes)` - Batch assignment

### 📊 MCP Resources
- `products://` - List all products with pagination
- `product://{product_code}` - Detailed product information
- `functionalities://` - List available functionalities
- `search://?query={term}&type={type}` - Search across entities
- `schema://?type={entity}` - Access ontology schema

### 🔐 Authentication & Security
- JWT-based authentication with configurable expiration
- Role-based access control
- Rate limiting per user
- CORS protection for web integration
- Input validation and sanitization
- Audit logging for all operations

## Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Neo4j 5.x

### Development Setup
```bash
# 1. Install dependencies
uv sync

# 2. Set environment variables
cp .env.example .env
# Edit .env with your configurations

# 3. Start Neo4j (if not running)
docker compose up -d neo4j

# 4. Run MCP server
uv run python -m mcp_server.server

# Or with Docker Compose (recommended)
docker compose -f docker-compose.mcp.yaml up
```

### Environment Variables
```env
# Server Configuration
MCP_SERVER_NAME="Product Management MCP Server"
MCP_HOST=127.0.0.1
MCP_PORT=8000
MCP_TRANSPORT=sse

# Authentication
MCP_AUTH_ENABLED=true
MCP_JWT_SECRET_KEY=your-super-secret-key
MCP_JWT_EXPIRY_HOURS=24

# Neo4j Connection
MCP_NEO4J_URI=bolt://localhost:7687
MCP_NEO4J_USERNAME=neo4j
MCP_NEO4J_PASSWORD=your_password
MCP_NEO4J_DATABASE=neo4j
```

## API Usage Examples

### Authentication
```bash
# Get JWT token
curl -X POST http://localhost:8000/tools/authenticate_user \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response
{
  "success": true,
  "username": "admin",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 86400
}
```

### Product Registration
```bash
# Register product with functionalities
curl -X POST http://localhost:8000/tools/register_product \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "ERP",
    "name": "Enterprise Resource Planning System",
    "functionalities": ["REPORTES", "CONTABILIDAD", "GESTION"]
  }'

# Response
{
  "success": true,
  "message": "Product 'ERP' registered successfully",
  "product": {
    "code": "ERP",
    "name": "Enterprise Resource Planning System",
    "functionalities": ["REPORTES", "CONTABILIDAD", "GESTION"],
    "functionality_count": 3
  }
}
```

### Resource Access
```bash
# List all products
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/resources/products://?limit=10&offset=0"

# Get specific product
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/resources/product://ERP"

# Search products
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/resources/search://?query=enterprise&type=products"
```

## Testing

```bash
# Run test suite
uv run pytest mcp_server/tests/

# Run with coverage
uv run pytest --cov=mcp_server mcp_server/tests/

# Run specific test
uv run pytest mcp_server/tests/test_mcp_server.py::TestProductTools::test_register_product_success -v
```

## Docker Deployment

### Full Stack Deployment
```bash
# Deploy Neo4j + MCP Server
docker compose -f docker-compose.mcp.yaml up -d

# View logs
docker compose -f docker-compose.mcp.yaml logs mcp-server

# Scale MCP server
docker compose -f docker-compose.mcp.yaml up -d --scale mcp-server=3
```

### Production Considerations
- Use external secrets management for JWT keys
- Configure proper resource limits
- Set up monitoring and log aggregation
- Implement backup strategies for Neo4j data
- Use HTTPS in production environments

## Development

### Project Structure
```
mcp_server/
├── __init__.py              # Package initialization
├── server.py                 # Main FastMCP server
├── auth/                     # Authentication system
│   ├── jwt_handler.py          # JWT token management
│   └── middleware.py          # Auth middleware
├── tools/                    # MCP tools
│   ├── product_tools.py        # Product management tools
│   └── functionality_tools.py # Functionality management tools
├── resources/                 # MCP resources
│   └── product_resources.py     # Data access resources
├── models/                    # Pydantic models
│   ├── requests.py             # Request models
│   └── responses.py            # Response models
├── config/                    # Configuration
│   └── mcp_config.py          # Server configuration
├── tests/                     # Test suite
│   └── test_mcp_server.py     # Unit and integration tests
└── docker/                    # Docker deployment
    └── Dockerfile.mcp          # Docker configuration
```

### Contributing
1. Add new tools in `tools/` directory
2. Register tools in `server.py`
3. Add corresponding tests
4. Update documentation
5. Ensure proper error handling and validation

## Integration with Existing Codebase

This MCP server seamlessly integrates with the existing GraphRAG project:

- **Leverages existing `ProductManager`** for all business logic
- **Reuses Neo4j connection handling** from `graph.neo4j_client`
- **Shares configuration system** with existing `config.settings`
- **Follows established patterns** for logging and error handling
- **Extends existing testing framework** with MCP-specific tests

## Acceptance Criteria Met

✅ **Product Registration**: `register_product` tool validates required fields and creates products according to ontology model

✅ **Functionality Assignment**: Automatic functionality linking to products with proper validation

✅ **Error Handling**: Spanish error messages for missing required fields ("Dato obligatorio X omitido")

✅ **Authentication**: JWT-based security matching architectural requirements

✅ **Deployment**: Support for both local development and Docker containerization

This implementation provides a complete, production-ready MCP API that extends your existing product management system with modern AI agent integration capabilities.