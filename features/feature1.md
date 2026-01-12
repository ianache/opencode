# Feature 1: Manage product definition in Neo4j

## User Story 1: Definir la estructura ontologia para definir un producto

### Definicion canonica
Como: "administrador de sistemas"
necesito: registrar la definicion de la ontologia para definir cualquier producto
proposito: de poder gestionar todos los productos que se desarrollan en la organizacion.

# Requisitos especificos
- Definir un tipo de nodo (Product) que registre los datos basicos del producto como son codigo (siglas identificaticas) y nombre (texto descriptivo) del producto
- Definir un tipo de nodo (Funcionality) que defina funcionalmente el producto y tenga por atributos el codigo (sigla identificativa) y nombre (de la funcionalidad)
- Definir un tipo de nodo (Component) que define un componente arquitectural y tenga por atributos el codigo (sigla identificativa) y nombre del componente.
- Definir la relacion de "asignacion de funcionalidad" entre el nodo Product y el nodo Funcionality.
- Definir la relacion de "asignacion de funcionalidad" entre el Component y Funcionality.
- Definir un tipo de nodo (Incident) que define un incidente reportado sobre una funcionalidad del producto e incluye como atributos el codigo (interno unico), descripcion del incidente, nivel de SLA.
- Definir un tipo de nodo (Resolution) que define la solución estandar realizada a uno o varios incidentes similares y tiene por atributos la fecha y el procedimiento de resolucion.
