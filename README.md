# MAD Notes - Gestor de Modelos Profesional (Pro Wiki Edition)

**MAD Notes** es un editor de texto enriquecido (RTF) avanzado y un gestor de conocimientos desarrollado en Python utilizando el framework **PyQt6**. Diseñado para flujos de trabajo de alta productividad, combina la simplicidad de un bloc de notas con la potencia de una Wiki personal, permitiendo la interconexión de documentos mediante hipervínculos dinámicos y etiquetas inteligentes.

## 🚀 Características Principales

### 1. Sistema de "Hipervínculos Mágicos" (Smart Links)
Esta es la funcionalidad estrella del sistema. Permite vincular documentos entre sí sin menús complejos.
*   **Sintaxis Rápida:** Al escribir `##nombre_documento##` y presionar `#`, el sistema convierte automáticamente el texto en un hipervínculo interno.
*   **Protocolo Personalizado:** Utiliza un esquema interno `model://` para diferenciar entre navegación local y web.
*   **Auto-Creación:** Si haces clic en un enlace a un modelo que no existe, el sistema ofrece crearlo, guardarlo y abrirlo automáticamente en una nueva pestaña lógica.

### 2. Edición de Texto Enriquecido (RTF/HTML)
Soporte completo para formato profesional:
*   **Tipografía:** Negrita, Cursiva, Subrayado, Fuentes y Tamaños personalizados.
*   **Color:** Control total sobre el color de la fuente y el resaltado del fondo.
*   **Estructura:** Listas (viñetas y numeración) y Alineación de párrafos (Izquierda, Centro, Derecha, Justificado).
*   **Multimedia:** Inserción de imágenes y tablas con bordes personalizados para el modo oscuro.

### 3. Interfaz "Dark Mode" Nativa
La aplicación no utiliza los controles estándar de Windows, sino que renderiza su propia interfaz utilizando hojas de estilo QSS (Qt Style Sheets) para garantizar un **Modo Oscuro Real** (`#1e1e1e`), reduciendo la fatiga visual y ofreciendo una estética moderna tipo VS Code.

### 4. Navegación y Búsqueda Avanzada
*   **Filtrado en Tiempo Real:** Barra de búsqueda lateral que filtra la lista de archivos instantáneamente.
*   **Buscador Interno:** Diálogo flotante (no modal) para Buscar y Reemplazar texto, con soporte para coincidencia de mayúsculas/minúsculas.
*   **One-Click Navigation:** Detección inteligente del cursor. No requiere `Ctrl+Click`; un clic simple abre tanto enlaces web como internos.

### 5. Gestión de Archivos Robusta
*   **Importación Masiva:** Algoritmo capaz de escanear directorios completos, detectar archivos `.txt`, escapar caracteres conflictivos y convertirlos a `.rtf` preservando la estructura.
*   **Protección de Datos:** Sistema de seguridad que detecta cambios no guardados antes de cambiar de archivo, cerrar la app o crear uno nuevo.

---

## 🔧 Implementación Técnica y Arquitectura

El proyecto está construido sobre **Python 3.10+** y **PyQt6**, siguiendo una arquitectura orientada a objetos (OOP) modular. A continuación se detallan los componentes clave:

### 1. `SmartLinkTextEdit` (Hereda de `QTextEdit`)
Esta clase es el corazón del editor. Sobrescribe los eventos nativos del mouse y teclado para lograr la interactividad.
*   **`keyReleaseEvent`:** Escucha la tecla `#`. Utiliza **RegEx** (`re.search`) para analizar el texto precedente. Si detecta el patrón `##([\w\.-]+)##`, elimina el texto plano e inyecta un objeto HTML Anchor (`<a href="model://...">`).
*   **`mouseMoveEvent`:** Implementa `setMouseTracking(True)`. Analiza constantemente la posición del puntero usando `anchorAt(event.pos())`. Si detecta un ancla, cambia el cursor a `PointingHandCursor` para dar feedback visual.
*   **`mouseReleaseEvent`:** Intercepta el clic. Si el objeto bajo el mouse es un enlace, detiene la propagación del evento de edición y dispara el método `handle_link` de la ventana principal.

### 2. `EnhancedLinkHighlighter` (Hereda de `QSyntaxHighlighter`)
Un motor de renderizado de texto pasivo que se ejecuta en segundo plano.
*   Utiliza `QRegularExpression` para escanear el documento en busca de patrones de URL (`https://...`) y etiquetas internas.
*   Aplica `QTextCharFormat` (color turquesa y subrayado) a los patrones coincidentes sin alterar el contenido real del documento, proporcionando ayudas visuales inmediatas al usuario.

### 3. `ModelManagerApp` (Clase Principal `QMainWindow`)
Controlador principal que gestiona el estado de la aplicación.
*   **Gestión de Rutas:** Utiliza `os.path` y `sys` para determinar rutas relativas, asegurando que la aplicación sea portable (puedes mover la carpeta y seguirá funcionando).
*   **Persistencia:** Escribe y lee archivos utilizando codificación `utf-8` explícita para soportar caracteres internacionales y emojis.
*   **Sistema de Vínculos (`handle_link`):**
    *   Si el protocolo es `model://`, busca el archivo en la lista interna. Si no existe, invoca `QMessageBox` para confirmar la creación.
    *   Si el protocolo es `http://` o `https://`, utiliza `QDesktopServices.openUrl` para delegar la apertura al navegador predeterminado del sistema operativo.

### 4. Interfaz Gráfica (UI)
*   **Layouts:** Uso intensivo de `QHBoxLayout` y `QVBoxLayout` dentro de un `QSplitter`, permitiendo al usuario redimensionar el panel de lista y el editor dinámicamente.
*   **QSS (Qt Style Sheets):** Se define una constante `DARK_STYLESHEET` al inicio que inyecta CSS a nivel de aplicación (`QApplication.setStyleSheet`), asegurando consistencia visual en todos los widgets, diálogos y menús contextuales.

---

## 📦 Instalación y Uso

### Requisitos
*   Python 3.8 o superior.
*   Librería PyQt6.

### Pasos
1.  Clonar el repositorio:
    ```bash
    git clone https://github.com/martdumo/mad-notes.git
    ```
2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ejecutar la aplicación:
    ```bash
    python main.py
    ```

---

## 📝 Licencia
Este proyecto es de código abierto. Siéntete libre de contribuir o modificarlo para tus necesidades.