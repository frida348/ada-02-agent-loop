# ada-02-agent-loop
 ### 1. ¿Qué es tool calling?

  Es el mecanismo mediante el cual el modelo solicita de forma
  estructurada ejecutar funciones externas predefinidas (como JSON) en lugar de limitarse a
  generar texto libre, permitiéndole interactuar directamente con el
  entorno.
  
  ### 2. ¿Qué es una observation?

  Es la información o resultado que el entorno devuelve tras ejecutar una
  herramienta (por ejemplo el texto de un archivo). Esta respuesta se
  alimenta de vuelta al contexto del agente para que decida el siguiente
  paso.
  
  ### 3. ¿Qué es el Agent Loop?

  Es el ciclo iterativo continuo compuesto por:

    Observe longrightarrow Plan longrightarrow Act longrightarrow Verify

  En cada vuelta, el agente percibe el estado actual, razona sobre el
  objetivo, ejecuta una acción mediante herramientas y valida el resultado
  hasta satisfacer las condiciones de éxito o criterio de parada.
 
  ### 4. ¿Qué operaciones corresponden a read, write, edit y bash?

  • READ: Inspeccionar y leer el contenido de archivos existentes sin
  modificarlos.
  • WRITE: Crear archivos nuevos desde cero o sobrescribir archivos
  completos.
  • EDIT: Realizar modificaciones de
  texto dentro de un archivo existente.
  • BASH: Ejecutar comandos en la consola del sistema operativo para
  interactuar con herramientas externas como pytest.

  ### 5. ¿Dónde intervino el agente?

  • En la inspección y diagnóstico autónomo de los archivos del
  repositorio.
  • En la ejecución de los comandos de prueba para validar el fallo.
  • En la corrección puntual del bug en calculator.py en linea 13-14
  • En la creación de agent-run.md.
  • En la creación del test test_calculator.py:20-21 en test_calculator.py,
  la implementación de calculator.py:17-18, y la codificación de
  agent_loop.py.
  • En la verificación automática re-ejecutando la suite de tests.
 
  ### 6. ¿Dónde intervino el humano?

  • En la definición de metas, restricciones y prioridades (p. ej.
  delimitar no alterar tests, exigir el cambio mínimo, solicitar la nueva
  operación de módulo o pedir la representación formal del loop).
  • En la supervisión y aceptación de cada fase del trabajo.
  
  ### 7. ¿Qué capacidad se perdería sin ejecución de comandos?

  Se perdería la verificación dinámica y empírica en tiempo real. El
  agente no podría ejecutar tests, verificar estados de
  compilación, consultar herramientas como git, ni comprobar si el código
  realmente funciona, quedando reducido a un
  razonamiento propenso a alucinaciones.
