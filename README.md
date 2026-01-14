# GraphRAG Project

A Python-based Graph Retrieval-Augmented Generation (GraphRAG) application that uses Neo4j as the graph database and LangChain for graph operations. The project focuses on building and querying knowledge graphs from structured news article data.

## 🚀 Features

- **Secure Configuration**: Environment variable-based credential management
- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Modern Tech Stack**: Uses latest LangChain Neo4j integration
- **Comprehensive Testing**: Unit, integration, and E2E tests with pytest
- **Code Quality**: Automated formatting, linting, and type checking
- **Production Ready**: Error handling, logging, and monitoring

## 📋 Requirements

- **Python**: 3.12+
- **Package Manager**: uv (recommended) or pip
- **Database**: Neo4j 5.0+
- **Operating System**: Windows, Linux, macOS

## 🛠️ Installation

### Using Vibe-Kanban

```bash
npx vibe-kanban
```

### Test with inspector

```
npx @modelcontextprotocol/inspector
```

### Run MCP Server

```
uv run python -m mcp_server.server --transport sse
```

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd 13-GraphRAG

# Install dependencies
uv sync

# Install development dependencies (optional)
uv sync --dev
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd 13-GraphRAG

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .
pip install -e ".[dev,test]"  # For development
```

## ⚙️ Configuration

### 1. Environment Variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your Neo4j configuration:

```env
# Neo4j Database Configuration
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here
NEO4J_DATABASE=neo4j

# Optional Configuration
LOG_LEVEL=INFO
```

### 2. Neo4j Setup

#### Local Neo4j Instance

```bash
# Using Docker (recommended)
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -d \
    -e 'NEO4J_AUTH=neo4j/your_password' \
    -e 'NEO4J_PLUGINS=["apoc"]' \
    neo4j:latest
```

#### Neo4j Desktop

1. Install [Neo4j Desktop](https://neo4j.com/download/)
2. Create a new project and database
3. Set up credentials
4. Update `.env` with connection details

#### Neo4j Aura (Cloud)

1. Sign up for [Neo4j Aura](https://aura.neo4j.com/)
2. Create a free database
3. Copy connection string to `.env`

## 🚀 Quick Start

```bash
# Run the main application
uv run python main.py

# Alternative with pip
python main.py
```

This will:
1. Load configuration from environment variables
2. Connect to Neo4j database
3. Load sample news data
4. Process and clean the data
5. Display summary statistics

## 📁 Project Structure

```
graphrag/
├── main.py                 # Main application entry point
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration management
├── graph/
│   ├── __init__.py
│   └── neo4j_client.py    # Neo4j database operations
├── data/
│   ├── __init__.py
│   └── processor.py        # Data loading and processing
├── utils/
│   ├── __init__.py
│   └── logging.py          # Logging utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest configuration
│   ├── unit/              # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/          # Test data fixtures
├── .env.example           # Environment variables template
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=.

# Run specific test categories
uv run pytest tests/unit/          # Unit tests only
uv run pytest tests/integration/   # Integration tests only

# Run with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/unit/test_settings.py::TestSettings::test_default_settings
```

### Test Categories

- **Unit Tests (70%)**: Test individual functions and classes in isolation
- **Integration Tests (25%)**: Test component interactions with real dependencies
- **E2E Tests (5%)**: Test complete application workflows

### Test Coverage

Target: 90%+ code coverage across all modules

## 🔧 Development

### Code Quality Tools

The project uses automated code quality tools:

```bash
# Format code
uv run black .

# Sort imports
uv run isort .

# Lint code
uv run flake8 .

# Type checking
uv run mypy .

# Run all quality checks
uv run pre-commit run --all-files
```

### Pre-commit Hooks

Pre-commit hooks are configured to run automatically:

```bash
# Install hooks
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files
```

### Adding Dependencies

```bash
# Add runtime dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Add optional dependency group
uv add --group test package-name
```

## 📊 Usage Examples

### Basic Data Processing

```python
from data.processor import DataProcessor

# Initialize processor
processor = DataProcessor()

# Load news data
data = processor.load_news_data()

# Clean and process data
cleaned_data = processor.clean_text_data(data)

# Get summary statistics
summary = processor.get_data_summary(cleaned_data)
print(f"Processed {summary['total_articles']} articles")
```

### Neo4j Operations

```python
from graph.neo4j_client import create_neo4j_client

# Create client and connect
with create_neo4j_client() as client:
    # Execute queries
    result = client.query("MATCH (n) RETURN count(n) as node_count")
    print(f"Database has {result[0]['node_count']} nodes")

    # Get schema
    schema = client.get_schema()
    print("Database schema:", schema)
```

### Configuration Management

```python
from config.settings import get_settings

# Get application settings
settings = get_settings()
print(f"Connected to {settings.neo4j_uri}")
```

## 🐛 Troubleshooting

### Common Issues

#### Connection Errors

```
Error connecting to Neo4j: Failed to establish connection
```

**Solutions:**
1. Check Neo4j is running: `bolt://127.0.0.1:7687`
2. Verify credentials in `.env` file
3. Check network connectivity
4. Ensure firewall allows port 7687

#### Environment Variable Issues

```
Error: Missing required environment variables: NEO4J_PASSWORD
```

**Solutions:**
1. Copy `.env.example` to `.env`
2. Fill in missing values
3. Ensure `.env` is not committed to version control

#### Test Failures

```
FAILED tests/unit/test_settings.py
```

**Solutions:**
1. Install test dependencies: `uv sync --group test`
2. Check environment variables are properly set
3. Run tests from project root directory

### Getting Help

- **Issues**: Create an issue in the project repository
- **Documentation**: Check this README and code comments
- **Neo4j Help**: [Neo4j Documentation](https://neo4j.com/docs/)
- **LangChain Help**: [LangChain Documentation](https://python.langchain.com/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `uv run pytest`
5. Run code quality checks: `uv run pre-commit run --all-files`
6. Commit changes: `git commit -m "Add amazing feature"`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Development Guidelines

- Follow PEP 8 code style (enforced by black)
- Add type hints (checked by mypy)
- Write tests for new functionality
- Update documentation as needed
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Neo4j**: Graph database technology
- **LangChain**: LLM integration framework
- **Pandas**: Data manipulation library
- **pytest**: Testing framework
- **uv**: Fast Python package manager

## 📈 Roadmap

- [ ] Graph schema management
- [ ] Advanced entity extraction
- [ ] Query optimization
- [ ] Performance monitoring dashboard
- [ ] Docker deployment configuration
- [ ] REST API interface
- [ ] Real-time data processing

---

**Note**: This is a demonstration project. For production use, ensure proper security measures, monitoring, and scaling considerations are implemented.
