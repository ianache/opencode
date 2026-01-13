# Architecture Documentation

## Overview

This document describes the system architecture for the GraphRAG microservice ecosystem. The architecture consists of two main views: the service authentication flow and the automated code triage system.

## Service Authentication Architecture

### Components

1. **Consumer** - External user/client initiating requests
2. **Identity Management (idm)** - Red Hat Keycloak for authentication
3. **FastMCP Product MCP Server** - Main microservice handling business logic
4. **Neo4j Database** - Graph database for data persistence
5. **Logging Infrastructure** - log4j (v2.23.1) and kafka-client (v3.7.0)
6. **Error Logs** - Apache Kafka topic for error handling

### Authentication Flow

1. **JWT Request**: Consumer requests JWT token from Red Hat Keycloak
2. **Service Request**: Consumer sends request with JWT token to FastMCP Product MCP Server
3. **Token Validation**: FastMCP validates JWT token with Keycloak
4. **Database Operations**: Upon successful validation, FastMCP executes Cypher queries against Neo4j database

### Logging Architecture

- **log4j Framework**: Version 2.23.1 for structured logging
- **Kafka Integration**: Version 3.7.0 kafka-client for asynchronous log shipping
- **Error Topic**: Dedicated Kafka topic `error.logs` for error message aggregation

## Automated Code Triage System

### Components

1. **GitLab CI/CD Pipeline** - Automated deployment and indexing
2. **Neo4j Vector Database** - Stores indexed codebase representations with vector capabilities
3. **Google Gemini AI** - AI model (gemini-2.5-flash) for code analysis
4. **Triage Service** - Automated bug analysis and recommendation system
5. **Kubernetes Production** - Container orchestration platform

### Code Indexing Process

1. **Merge Request**: Developer merges code to master branch for production deployment
2. **CI/CD Trigger**: GitLab CI/CD pipeline automatically starts
3. **Code Indexing**: All Java files and database scripts are processed and indexed
4. **Vector Storage**: Indexed information is stored in the vector database for efficient retrieval

### Automated Triage Process

1. **Error Detection**: ERROR level messages are published to Apache Kafka via log4j
2. **Triage Service**: Consumes error information from Kafka topic
3. **Code Analysis**: Reviews indexed codebase for relevant code sections related to the error
4. **AI-Powered Analysis**: Uses Google Gemini to analyze code and error context
5. **Recommendation Generation**: Provides suggested code changes and fixes
6. **Bug Reporting**: Automatically creates bug reports in GitLab with analysis results

## Technology Stack

### Core Technologies
- **Database**: Neo4j (Graph Database)
- **Authentication**: Red Hat Keycloak
- **Containerization**: Kubernetes
- **CI/CD**: GitLab CI/CD
- **Messaging**: Apache Kafka
- **AI/ML**: Google Gemini (gemini-2.5-flash)

### Development Tools
- **Logging**: Apache log4j v2.23.1
- **Messaging Client**: kafka-client v3.7.0
- **Neo4j Vector Database**: For code indexing and semantic search with graph capabilities

## Security Architecture

- **JWT Authentication**: Token-based authentication via Keycloak
- **Microservice Isolation**: Each service operates with minimal required permissions
- **Secure Communication**: All inter-service communications use authenticated channels

## Data Flow

1. User requests flow through Keycloak for authentication
2. Authenticated requests are processed by FastMCP services
3. Database operations use Cypher queries against Neo4j
4. Errors are captured and sent to Kafka for triage processing
5. Code changes trigger automated indexing in CI/CD pipeline
6. AI analysis provides intelligent recommendations for bug fixes

## Deployment Architecture

- **Production Environment**: Kubernetes cluster
- **Service Mesh**: Microservice communication patterns
- **Observability**: Centralized logging via Kafka
- **Automation**: CI/CD pipeline with automated testing and deployment