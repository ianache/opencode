# Feature 3: MCP API to Register an Incident in a functionality

## User Story 3.1: 

### Definicion canonica
Como: "administrador de sistemas"
necesito: registrar un incidente sobre funcionalidad de un producto
proposito: de poder gestionar todos incidentes en produccion para mejorar la calidad del producto.

# Requisitos especificos
- se registre el incidente conforme a la información del modelo Ontologico.
- se debe proporcionar la referencia de la funcionalidad sobre la que se reporta el incidente segun la relación entre Incident y Functionality en el modelo Ontologico.

# Criterios de Aceptacion
- Cuando ocurre un incidente en una funcionalidad de un producto entonces se debe registrar el incidente según los datos previstos en el modelo ontologico y se debe considerar el SLA con el mas alto nivel.
- Cuando ocurre un incidente en una funcionalidad de un producto dado que se omiten datos para alguno de los atributos del Incident considerado en el modelo ontologico entonces se debe reportar un error "Datos incompletos proporcionados". 