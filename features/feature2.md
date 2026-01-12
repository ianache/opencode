# Feature 2: MCP API to Manage product definition

Este feature añade un API basada en Model Control Protocol (MCP) usando FastMCP (mcp[cli])

## User Story 2.1: 

### Definicion canonica
Como: "administrador de sistemas"
necesito: registrar nuevo producto con su funcionalidades
proposito: de poder gestionar todos los productos y funcionalidades asignadas.

# Requisitos especificos
- se registre el producto de acuerdo con los atributos del modelo Ontologico.
- se registre la lista de funcionalidades y se asignen al producto según el modelo ontologico.

# Criterios de Aceptacion
- Cuando se requiere registrar producto y funcionalidades asignadas entonces un nuevo producto queda registrado, las funcionalidades quedan registradas y se han asignado dichas funcionalidades al producto.
- Cuando se requiere registrar producto sin funcionalidades asignadas entonces un nuevo producto queda registrado.
- Cuando se requiere registrar producto dado que se omite su codigo o nombre entonces se debe reportar error "Dato obligatorio X omitido" (donde X representa el atributo o atributos omisos)