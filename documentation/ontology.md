# Ontology Documentation

## Overview

This document describes the complete data model and ontology implemented in the GraphRAG system. The ontology defines the structure and relationships between core entities used for product management, incident tracking, and resolution management.

## Core Entities

### Product

**Description**: Top-level entity representing a product or system in the organization.

**Properties**:
- `code` (string, unique): Product unique identifier (max 20 chars)
- `name` (string): Product descriptive name (max 200 chars)
- `created_at` (datetime): Timestamp when product was created
- `updated_at` (datetime, optional): Timestamp when product was last modified

**Neo4j Label**: `Product`
**Constraints**: Unique constraint on `code` property

### Functionality

**Description**: Features or capabilities that can be assigned to products and components.

**Properties**:
- `code` (string, unique): Functionality unique identifier (max 20 chars)
- `name` (string): Functionality descriptive name (max 200 chars)
- `created_at` (datetime): Timestamp when functionality was created

**Neo4j Label**: `Functionality`
**Constraints**: Unique constraint on `code` property

### Component

**Description**: Software components that implement specific functionalities.

**Properties**:
- `code` (string, unique): Component unique identifier (max 20 chars)
- `name` (string): Component descriptive name (max 200 chars)
- `created_at` (datetime): Timestamp when component was created

**Neo4j Label**: `Component`
**Constraints**: Unique constraint on `code` property

### Incident

**Description**: Issues or problems that occur in specific functionalities with SLA requirements.

**Properties**:
- `code` (string, unique): Incident unique identifier (max 20 chars)
- `description` (string): Detailed incident description (max 500 chars)
- `sla_level` (string): SLA priority level for incident resolution
- `functionality_code` (string, implicit): Reference to associated functionality
- `created_at` (datetime): Timestamp when incident was created

**Neo4j Label**: `Incident`
**Constraints**: Unique constraint on `code` property

**SLA Levels**:
- `SLA_CRITICAL`: Highest priority incidents
- `SLA_HIGH`: High priority incidents
- `SLA_MEDIUM`: Medium priority incidents
- `SLA_LOW`: Low priority incidents

### Resolution

**Description**: Solutions or procedures applied to resolve incidents.

**Properties**:
- `incident_code` (string, unique): Reference to incident being resolved
- `procedure` (string): Description of resolution procedure
- `resolution_date` (datetime): Date when resolution was implemented
- `created_at` (datetime): Timestamp when resolution was recorded

**Neo4j Label**: `Resolution`
**Constraints**: Unique constraint on `incident_code` property

## Relationships

### ASIGNACION_FUNCIONALIDAD

**Description**: Assigns functionalities to products and components.

**Directionality**: 
- Product → Functionality
- Component → Functionality

**Cardinality**:
- From Product/Component: "One or more" (1..*)
- To Functionality: "Zero or more" (0..*)

**Neo4j Relationship**: `[:ASIGNACION_FUNCIONALIDAD]`

**Properties**:
- `created_at` (datetime): Timestamp when assignment was created

**Implementation**:
```cypher
// Product to Functionality
MATCH (p:Product {code: $product_code})
MATCH (f:Functionality {code: $functionality_code})
MERGE (p)-[:ASIGNACION_FUNCIONALIDAD]->(f)

// Component to Functionality
MATCH (c:Component {code: $component_code})
MATCH (f:Functionality {code: $functionality_code})
MERGE (c)-[:ASIGNACION_FUNCIONALIDAD]->(f)
```

### HAS_INCIDENT

**Description**: Links functionalities to incidents that occur within them.

**Directionality**: Functionality → Incident

**Cardinality**:
- From Functionality: "Zero or More" (0..*)
- To Incident: "Only One" (1..1)

**Neo4j Relationship**: `[:HAS_INCIDENT]`

**Implementation**:
```cypher
MATCH (f:Functionality {code: $functionality_code})
MATCH (i:Incident {code: $incident_code})
MERGE (f)-[:HAS_INCIDENT]->(i)
```

### HAS_RESOLUTION

**Description**: Associates incidents with their resolutions.

**Directionality**: Bidirectional (Incident ↔ Resolution)

**Cardinality**:
- From Incident: "Zero or More" (0..*)
- To Resolution: "One or More" (1..*)

**Neo4j Relationship**: `[:HAS_RESOLUTION]`

**Implementation**:
```cypher
MATCH (i:Incident {code: $incident_code})
MATCH (r:Resolution {incident_code: $incident_code})
MERGE (i)-[:HAS_RESOLUTION]->(r)
```

## Business Rules

### Entity Creation Rules

1. **Product Creation**: Requires code and name. Functionalities assignment is optional.
2. **Functionality Creation**: Requires code and name. Can be assigned to multiple products/components.
3. **Component Creation**: Requires code and name. Can implement multiple functionalities.
4. **Incident Creation**: Requires code, description, SLA level, and existing functionality.
5. **Resolution Creation**: Requires incident code and procedure. Incident must exist.

### Relationship Rules

1. **Functionality Assignment**: 
   - A product can have one or more functionalities
   - A component can be assigned one or more functionalities
   - A functionality can be assigned to zero or more products/components
   - Assignments are tracked with timestamps

2. **Incident Linking**:
   - Every incident must be linked to exactly one functionality
   - A functionality can have zero or more incidents
   - Incidents cannot exist without functionality reference

3. **Resolution Association**:
   - An incident can have zero or more resolutions
   - A resolution must be associated with exactly one incident
   - Multiple resolutions can exist for the same incident

### Data Integrity Rules

1. **Uniqueness**: All entity codes must be unique within their entity type
2. **Referential Integrity**: All relationships must reference existing entities
3. **SLA Validation**: Incident SLA levels must be from predefined set
4. **Required Fields**: All mandatory fields must be provided during creation

## Query Patterns

### Product-Centric Queries

```cypher
// Get product with all functionalities, incidents, and resolutions
MATCH (p:Product {code: $product_code})
OPTIONAL MATCH (p)-[:ASIGNACION_FUNCIONALIDAD]->(f:Functionality)
OPTIONAL MATCH (f)-[:HAS_INCIDENT]->(i:Incident)
OPTIONAL MATCH (i)-[:HAS_RESOLUTION]->(r:Resolution)
RETURN p, 
       collect(DISTINCT f) as functionalities,
       collect(DISTINCT i) as incidents,
       collect(DISTINCT r) as resolutions
```

### Functionality-Centric Queries

```cypher
// Get functionality with all products, components, and incidents
MATCH (f:Functionality {code: $functionality_code})
OPTIONAL MATCH (p:Product)-[:ASIGNACION_FUNCIONALIDAD]->(f)
OPTIONAL MATCH (f)-[:HAS_INCIDENT]->(i:Incident)
OPTIONAL MATCH (i)-[:HAS_RESOLUTION]->(r:Resolution)
RETURN f,
       collect(DISTINCT p) as products,
       collect(DISTINCT i) as incidents,
       collect(DISTINCT r) as resolutions
```

### Incident Tracking Queries

```cypher
// Get all incidents for a product
MATCH (p:Product {code: $product_code})
MATCH (p)-[:ASIGNACION_FUNCIONALIDAD]->(f:Functionality)
MATCH (f)-[:HAS_INCIDENT]->(i:Incident)
RETURN i, f
ORDER BY i.created_at DESC

// Get resolution history for an incident
MATCH (i:Incident {code: $incident_code})
MATCH (i)-[:HAS_RESOLUTION]->(r:Resolution)
RETURN r, i
ORDER BY r.created_at DESC
```

## API Mappings

### MCP Tools

#### Product Management
- `register_product`: Create product with optional functionality assignment
- `get_product_details`: Retrieve product with all relationships
- `update_product`: Update product properties
- `delete_product`: Remove product and all relationships
- `list_products`: Paginated product listing
- `search_products`: Fuzzy search by code or name

#### Functionality Management
- `register_functionality`: Create new functionality
- `get_functionality_details`: Retrieve functionality with relationships
- `assign_functionalities_to_product`: Bulk assignment to product
- `remove_functionalities_from_product`: Bulk removal from product
- `list_functionalities`: Paginated functionality listing

#### Incident Management
- `register_incident`: Create incident with functionality reference
- `get_incident_details`: Retrieve incident information
- `list_incidents_by_functionality`: Get all incidents for functionality
- `list_incidents_by_product`: Get all incidents for product

## Database Schema

### Constraints

```cypher
CREATE CONSTRAINT product_code_unique IF NOT EXISTS 
FOR (p:Product) REQUIRE p.code IS UNIQUE

CREATE CONSTRAINT functionality_code_unique IF NOT EXISTS 
FOR (f:Functionality) REQUIRE f.code IS UNIQUE

CREATE CONSTRAINT component_code_unique IF NOT EXISTS 
FOR (c:Component) REQUIRE c.code IS UNIQUE

CREATE CONSTRAINT incident_code_unique IF NOT EXISTS 
FOR (i:Incident) REQUIRE i.code IS UNIQUE

CREATE CONSTRAINT resolution_incident_unique IF NOT EXISTS 
FOR (r:Resolution) REQUIRE r.incident_code IS UNIQUE
```

### Indexes

```cypher
// Performance indexes for common queries
CREATE INDEX product_name_index IF NOT EXISTS 
FOR (p:Product) ON (p.name)

CREATE INDEX functionality_name_index IF NOT EXISTS 
FOR (f:Functionality) ON (f.name)

CREATE INDEX incident_sla_level_index IF NOT EXISTS 
FOR (i:Incident) ON (i.sla_level)

CREATE INDEX incident_created_at_index IF NOT EXISTS 
FOR (i:Incident) ON (i.created_at)
```

## Validation Rules

### Input Validation

1. **Code Fields**: Must be 1-20 characters, alphanumeric, unique
2. **Name Fields**: Must be 1-200 characters, non-empty
3. **Description**: Must be 1-500 characters for incidents
4. **SLA Levels**: Must be one of predefined levels
5. **Dates**: Must be valid ISO 8601 datetime strings

### Business Validation

1. **Functionality Assignment**: Cannot assign non-existent functionality
2. **Incident Creation**: Functionality must exist before incident creation
3. **Resolution Creation**: Incident must exist before resolution creation
4. **Relationship Integrity**: All relationships maintain referential integrity

## Error Handling

### Common Error Scenarios

1. **Entity Not Found**: Attempting to reference non-existent entities
2. **Duplicate Codes**: Creating entities with existing codes
3. **Invalid SLA**: Using unsupported SLA levels
4. **Missing Required Fields**: Omitting mandatory fields
5. **Relationship Violations**: Creating invalid relationships

### Error Response Format

```json
{
  "error": "ValidationError",
  "message": "Dato obligatorio 'codigo' omitido",
  "details": {
    "field": "codigo",
    "value": null,
    "constraint": "required"
  }
}
```

## Performance Considerations

### Query Optimization

1. **Pagination**: All list operations support limit/offset pagination
2. **Indexes**: Essential fields indexed for performance
3. **Bulk Operations**: Batch assignment operations supported
4. **Caching**: Frequently accessed entities cached at application level

### Scalability

1. **Horizontal Scaling**: Neo4j clustering support
2. **Connection Pooling**: Database connection reuse
3. **Query Limits**: Maximum result size enforced
4. **Memory Management**: Efficient result set handling

## Security Considerations

### Access Control

1. **Authentication**: JWT-based authentication required
2. **Authorization**: Role-based access to operations
3. **Input Sanitization**: All inputs validated and sanitized
4. **SQL Injection Prevention**: Parameterized queries only

### Data Privacy

1. **Sensitive Data**: No PII stored in primary entities
2. **Audit Trail**: All operations logged with timestamps
3. **Data Retention**: Configurable data retention policies
4. **Backup Strategy**: Regular automated backups