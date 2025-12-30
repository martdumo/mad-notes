import sys
import os
import re
import ctypes
import json
import platform
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QTextEdit, QLineEdit, 
                             QPushButton, QSplitter, QMessageBox, QToolBar, 
                             QColorDialog, QFontComboBox, QSpinBox, QFileDialog,
                             QInputDialog, QLabel, QMenu, QMenuBar, QDialog, 
                             QGridLayout, QCheckBox, QComboBox)
from PyQt6.QtGui import (QAction, QIcon, QFont, QColor, QTextCursor, 
                         QTextListFormat, QTextTableFormat, QTextCharFormat,
                         QTextBlockFormat, QTextDocument, QPixmap, QDesktopServices,
                         QSyntaxHighlighter, QKeySequence, QShortcut)  # QShortcut va aquí
from PyQt6.QtCore import Qt, QSize, QUrl, QRegularExpression, QEvent

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
APP_NAME = "Gestor Maletín (Tokyo Terminal)"

# ID de Aplicación
myappid = 'martdumo.maletin.tokyo.v17' 
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_app_config_dir():
    """Obtiene el directorio de configuración de la aplicación según el sistema operativo"""
    if platform.system() == "Windows":
        return os.path.join(os.getenv('APPDATA'), 'maletin-app')
    elif platform.system() == "Darwin":  # macOS
        return os.path.join(os.path.expanduser('~/Library/Application Support'), 'maletin-app')
    else:  # Linux y otros
        return os.path.join(os.path.expanduser('~/.config'), 'maletin-app')

# Directorio de configuración de la app
APP_CONFIG_DIR = get_app_config_dir()
os.makedirs(APP_CONFIG_DIR, exist_ok=True)

# Archivo de configuración para guardar el vault actual
CONFIG_FILE = os.path.join(APP_CONFIG_DIR, "app_config.json")
VAULT_HISTORY_FILE = os.path.join(APP_CONFIG_DIR, "vault_history.json")

# =============================================================================
# ESTILOS TOKYO NIGHT (KITTY STYLE)
# =============================================================================
C_BG      = "#1a1b26"
C_SIDE    = "#16161e"
C_FG      = "#c0caf5"
C_SEL     = "#33467c"
C_ACCENT  = "#7aa2f7"
C_URGENT  = "#f7768e"
C_SUCCESS = "#9ece6a"
C_WARNING = "#e0af68"
C_BORDER  = "#414868"
C_LINE    = "#292e42"

FONT_FAMILY = "'Cascadia Code', 'Consolas', 'Courier New', monospace"
FONT_SIZE   = "16pt"

TOKYO_STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {C_BG};
    color: {C_FG};
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
}}
QWidget {{
    background-color: {C_BG};
    color: {C_FG};
}}
QListWidget {{
    background-color: {C_SIDE};
    color: {C_FG};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 10px;
    selection-background-color: {C_SEL};
    selection-color: #ffffff;
}}
QListWidget::item:hover {{
    background-color: {C_LINE};
}}
QListWidget::item:selected {{
    background-color: {C_SEL};
    border: 1px solid {C_ACCENT};
}}
QTextEdit {{
    background-color: {C_BG};
    color: {C_FG};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 10px;
    selection-background-color: {C_SEL};
    selection-color: #ffffff;
    font-family: {FONT_FAMILY};
}}
QLineEdit {{
    background-color: {C_SIDE};
    color: {C_FG};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 8px;
    selection-background-color: {C_SEL};
}}
QLineEdit:focus {{
    border: 1px solid {C_ACCENT};
}}
QPushButton {{
    background-color: {C_LINE};
    color: {C_ACCENT};
    border: 1px solid {C_BORDER};
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
    text-transform: uppercase;
}}
QPushButton:hover {{
    background-color: {C_SEL};
    border: 1px solid {C_ACCENT};
    color: #ffffff;
}}
QPushButton:pressed {{
    background-color: {C_ACCENT};
    color: {C_BG};
}}
QToolBar {{
    background-color: {C_BG};
    border-bottom: 2px solid {C_LINE};
    spacing: 10px;
    padding: 5px;
}}
QToolButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 6px;
    color: {C_FG};
}}
QToolButton:hover {{
    background-color: {C_LINE};
    border: 1px solid {C_BORDER};
}}
QToolButton:pressed {{
    background-color: {C_SEL};
}}
QMenuBar {{
    background-color: {C_SIDE};
    color: {C_FG};
    border-bottom: 1px solid {C_BORDER};
}}
QMenuBar::item:selected {{
    background-color: {C_SEL};
}}
QMenu {{
    background-color: {C_SIDE};
    border: 1px solid {C_ACCENT};
    padding: 5px;
}}
QMenu::item {{
    padding: 8px 20px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: {C_SEL};
}}
QStatusBar {{
    background-color: {C_SIDE};
    color: {C_FG};
    border-top: 1px solid {C_ACCENT};
}}
QLabel {{ 
    color: {C_FG}; 
    font-family: {FONT_FAMILY};
}}
QComboBox {{
    background-color: {C_SIDE};
    color: {C_FG};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 8px;
    selection-background-color: {C_SEL};
}}
QComboBox:hover {{
    border: 1px solid {C_ACCENT};
}}
QScrollBar:vertical {{
    border: none;
    background: {C_BG};
    width: 10px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: {C_BORDER};
    min-height: 20px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background: {C_ACCENT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

# =============================================================================
# FUNCIONES DE CONFIGURACIÓN DEL VAULT
# =============================================================================
def load_vault_config():
    """Carga la configuración del vault actual"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('current_vault', ''), config.get('startup_file', '')
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
    return '', ''

def save_vault_config(vault_path, startup_file=''):
    """Guarda la configuración del vault actual"""
    try:
        config = {
            'current_vault': vault_path,
            'startup_file': startup_file
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error al guardar configuración: {e}")
        return False

def load_vault_history():
    """Carga el historial de vaults utilizados"""
    if os.path.exists(VAULT_HISTORY_FILE):
        try:
            with open(VAULT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar historial de vaults: {e}")
    return []

def save_vault_history(vault_path):
    """Guarda un vault en el historial"""
    history = load_vault_history()
    
    # Si el vault ya existe en el historial, lo movemos al inicio
    if vault_path in history:
        history.remove(vault_path)
    
    # Agregamos el vault al inicio del historial
    history.insert(0, vault_path)
    
    # Limitamos el historial a 10 entradas
    history = history[:10]
    
    try:
        with open(VAULT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
        return True
    except Exception as e:
        print(f"Error al guardar historial de vaults: {e}")
        return False

def select_vault_directory(parent=None, current_vault=''):
    """Diálogo para seleccionar un directorio de vault"""
    dialog = QDialog(parent)
    dialog.setWindowTitle("Seleccionar Carpeta del Maletín")
    dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
    dialog.resize(600, 400)
    
    layout = QVBoxLayout()
    
    # Etiqueta de instrucciones
    lbl_info = QLabel("Selecciona la carpeta donde se guardarán tus archivos RTF")
    lbl_info.setStyleSheet(f"color: {C_FG}; font-size: 14pt; padding: 10px;")
    layout.addWidget(lbl_info)
    
    # Historial de vaults
    if os.path.exists(VAULT_HISTORY_FILE):
        history = load_vault_history()
        if history:
            lbl_history = QLabel("Ubicaciones recientes:")
            lbl_history.setStyleSheet(f"color: {C_ACCENT}; font-weight: bold; margin-top: 15px;")
            layout.addWidget(lbl_history)
            
            combo_history = QComboBox()
            combo_history.setStyleSheet(f"""
                QComboBox {{
                    background-color: {C_SIDE};
                    color: {C_FG};
                    border: 1px solid {C_BORDER};
                    border-radius: 4px;
                    padding: 8px;
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 30px;
                }}
            """)
            
            for vault in history:
                combo_history.addItem(vault)
            
            layout.addWidget(combo_history)
    
    # Campo de ruta actual
    lbl_current = QLabel(f"Ubicación actual: {current_vault if current_vault else 'Ninguna'}")
    lbl_current.setStyleSheet(f"color: {C_WARNING}; margin-top: 10px;")
    layout.addWidget(lbl_current)
    
    # Botón para seleccionar carpeta
    btn_select = QPushButton("🔍 Seleccionar Carpeta")
    btn_select.setStyleSheet(f"""
        QPushButton {{
            background-color: {C_ACCENT};
            color: {C_BG};
            border: 1px solid {C_ACCENT};
            border-radius: 5px;
            padding: 12px;
            font-weight: bold;
            font-size: 14pt;
        }}
        QPushButton:hover {{
            background-color: #5d8cda;
            border: 1px solid #5d8cda;
        }}
    """)
    layout.addWidget(btn_select)
    
    # Campo de ruta seleccionada
    txt_path = QLineEdit()
    txt_path.setPlaceholderText("Ruta de la carpeta del maletín...")
    txt_path.setStyleSheet(f"""
        QLineEdit {{
            background-color: {C_SIDE};
            color: {C_FG};
            border: 1px solid {C_BORDER};
            border-radius: 4px;
            padding: 8px;
            font-family: {FONT_FAMILY};
        }}
    """)
    layout.addWidget(txt_path)
    
    # Botones de acción
    btn_layout = QHBoxLayout()
    btn_ok = QPushButton("✅ ACEPTAR")
    btn_ok.setStyleSheet(f"""
        QPushButton {{
            background-color: {C_SUCCESS};
            color: {C_BG};
            border: 1px solid {C_SUCCESS};
            border-radius: 5px;
            padding: 10px;
            font-weight: bold;
        }}
    """)
    btn_cancel = QPushButton("❌ CANCELAR")
    btn_cancel.setStyleSheet(f"""
        QPushButton {{
            background-color: {C_URGENT};
            color: {C_BG};
            border: 1px solid {C_URGENT};
            border-radius: 5px;
            padding: 10px;
            font-weight: bold;
        }}
    """)
    btn_layout.addWidget(btn_ok)
    btn_layout.addWidget(btn_cancel)
    layout.addLayout(btn_layout)
    
    dialog.setLayout(layout)
    
    # Conectar señales
    def on_select_folder():
        folder = QFileDialog.getExistingDirectory(
            parent, 
            "Seleccionar Carpeta del Maletín",
            current_vault if current_vault else os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            txt_path.setText(folder)
            lbl_current.setText(f"Ubicación seleccionada: {folder}")
    
    def on_history_change(index):
        if index >= 0 and index < combo_history.count():
            vault_path = combo_history.itemText(index)
            txt_path.setText(vault_path)
            lbl_current.setText(f"Ubicación seleccionada: {vault_path}")
    
    btn_select.clicked.connect(on_select_folder)
    if 'combo_history' in locals():
        combo_history.currentIndexChanged.connect(on_history_change)
    btn_ok.clicked.connect(dialog.accept)
    btn_cancel.clicked.connect(dialog.reject)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        vault_path = txt_path.text().strip()
        if vault_path and os.path.isdir(vault_path):
            return vault_path
    return None

# =============================================================================
# CLASES AUXILIARES
# =============================================================================
class InsertLinkDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Insertar Hipervínculo")
        self.resize(500, 200)
        self.result_data = None
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        layout.setVerticalSpacing(15)
        
        lbl_text = QLabel("Texto a mostrar:")
        lbl_text.setStyleSheet(f"color: {C_FG};")
        self.txt_text = QLineEdit()
        
        lbl_url = QLabel("Dirección (URL):")
        lbl_url.setStyleSheet(f"color: {C_FG};")
        self.txt_url = QLineEdit()
        self.txt_url.setPlaceholderText("https://... o model://...")
        
        btn_ok = QPushButton("Insertar")
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_ACCENT};
                color: {C_BG};
                border: 1px solid {C_ACCENT};
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        btn_ok.clicked.connect(self.on_ok)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_LINE};
                color: {C_URGENT};
                border: 1px solid {C_URGENT};
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        
        layout.addWidget(lbl_text, 0, 0)
        layout.addWidget(self.txt_text, 0, 1)
        layout.addWidget(lbl_url, 1, 0)
        layout.addWidget(self.txt_url, 1, 1)
        layout.addWidget(btn_ok, 2, 0)
        layout.addWidget(btn_cancel, 2, 1)
        self.setLayout(layout)

    def on_ok(self):
        if self.txt_text.text() and self.txt_url.text():
            self.result_data = (self.txt_text.text(), self.txt_url.text())
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Complete ambos campos.")

class EnhancedLinkHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.internal_link_format = QTextCharFormat()
        self.internal_link_format.setForeground(QColor("#4EC9B0")) 
        self.internal_link_format.setFontUnderline(True)
        self.internal_link_format.setFontWeight(QFont.Weight.Bold)
        self.external_link_format = QTextCharFormat()
        self.external_link_format.setForeground(QColor("#6A9955")) 
        self.external_link_format.setFontUnderline(True)
        self.external_link_format.setFontWeight(QFont.Weight.Bold)
        self.internal_pattern = QRegularExpression(r"@@[\w\.-]+")
        self.external_pattern = QRegularExpression(r"https?://[\w./?=&#-]+")

    def highlightBlock(self, text):
        match_iterator = self.external_pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.external_link_format)
        match_iterator = self.internal_pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.internal_link_format)

class SmartLinkTextEdit(QTextEdit):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.highlighter = EnhancedLinkHighlighter(self.document())
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.document().setDefaultStyleSheet(f"a {{ text-decoration: underline; color: {C_ACCENT}; font-weight: bold; }}")
        
        font = self.font()
        font.setPointSize(16)
        font.setFamily("Cascadia Code")
        self.setFont(font)
        
        # --- Solución para Ctrl+S BUG: Instalar filtro de eventos ---
        self.installEventFilter(self)
        # --------------------------------------------------------------

    # --- Solución para Ctrl+S BUG: Filtro de eventos para capturar Ctrl+S ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_S:
                # Llamar directamente a la función de guardar
                self.parent_window.save_model()
                return True  # Consumir el evento para que no se propague
        return super().eventFilter(obj, event)
    # -------------------------------------------------------------------------

    # --- ZOOM CON CTRL + SCROLL ---
    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
            event.accept()
        else:
            super().wheelEvent(event)

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)
        if event.text() == "#": self.check_magic_tag()

    def check_magic_tag(self):
        cursor = self.textCursor()
        block_text = cursor.block().text()
        pos_in_block = cursor.positionInBlock()
        text_before = block_text[:pos_in_block]
        
        match = re.search(r"##([\w\.-]+)##$", text_before)
        if match:
            model_name = match.group(1)
            full_tag = match.group(0)
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, len(full_tag))
            cursor.removeSelectedText()
            html = f'<a href="model://{model_name}">{model_name}</a>&nbsp;'
            cursor.insertHtml(html)
            self.setFontPointSize(16)

    def mouseMoveEvent(self, event):
        if self.anchorAt(event.pos()) or self.get_link_at_pos(event.pos()):
            self.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.viewport().setCursor(Qt.CursorShape.IBeamCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            url = self.anchorAt(event.pos())
            if url:
                self.parent_window.handle_link(url)
                return 
            link_info = self.get_link_at_pos(event.pos())
            if link_info:
                l_type, l_target = link_info
                if l_type == "internal":
                    self.parent_window.handle_internal_link(l_target)
                elif l_type == "external":
                    self.parent_window.handle_external_link(l_target)
                return
        super().mouseReleaseEvent(event)

    def get_link_at_pos(self, pos):
        cursor = self.cursorForPosition(pos)
        block_text = cursor.block().text()
        pos_in_block = cursor.positionInBlock()
        internal_regex = re.compile(r"##[\w\.-]+##")
        for match in internal_regex.finditer(block_text):
            start, end = match.span()
            if start <= pos_in_block <= end:
                return ("internal", match.group()[2:-2]) 
        external_regex = re.compile(r"https?://[\w./?=&#-]+")
        for match in external_regex.finditer(block_text):
            start, end = match.span()
            if start <= pos_in_block <= end:
                return ("external", match.group())
        return None

class FindReplaceDialog(QDialog):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Buscar y Reemplazar")
        self.setWindowFlags(Qt.WindowType.Window) 
        self.resize(600, 250)
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        layout.setVerticalSpacing(15)
        self.lbl_find = QLabel("BUSCAR:")
        self.lbl_find.setStyleSheet(f"color: {C_FG};")
        self.txt_find = QLineEdit()
        self.lbl_rep = QLabel("REEMPLAZAR CON:")
        self.lbl_rep.setStyleSheet(f"color: {C_FG};")
        self.txt_rep = QLineEdit()
        self.chk_case = QCheckBox("Coincidir Mayús/Minús")
        self.chk_case.setStyleSheet(f"color: {C_FG};")
        
        self.btn_find = QPushButton("BUSCAR SIGUIENTE")
        self.btn_find.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_ACCENT};
                color: {C_BG};
                border: 1px solid {C_ACCENT};
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }}
        """)
        self.btn_find.clicked.connect(self.find_next)
        
        self.btn_rep = QPushButton("REEMPLAZAR")
        self.btn_rep.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_WARNING};
                color: {C_BG};
                border: 1px solid {C_WARNING};
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }}
        """)
        self.btn_rep.clicked.connect(self.replace_one)
        
        self.btn_all = QPushButton("REEMPLAZAR TODO")
        self.btn_all.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_SUCCESS};
                color: {C_BG};
                border: 1px solid {C_SUCCESS};
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }}
        """)
        self.btn_all.clicked.connect(self.replace_all)
        
        layout.addWidget(self.lbl_find, 0, 0)
        layout.addWidget(self.txt_find, 0, 1, 1, 2)
        layout.addWidget(self.lbl_rep, 1, 0)
        layout.addWidget(self.txt_rep, 1, 1, 1, 2)
        layout.addWidget(self.chk_case, 2, 0, 1, 3)
        layout.addWidget(self.btn_find, 3, 0)
        layout.addWidget(self.btn_rep, 3, 1)
        layout.addWidget(self.btn_all, 3, 2)
        self.setLayout(layout)

    def get_flags(self):
        f = QTextDocument.FindFlag(0)
        if self.chk_case.isChecked(): f |= QTextDocument.FindFlag.FindCaseSensitively
        return f

    def find_next(self):
        txt = self.txt_find.text()
        if not txt: return
        if not self.editor.find(txt, self.get_flags()):
            self.editor.moveCursor(QTextCursor.MoveOperation.Start)
            if not self.editor.find(txt, self.get_flags()):
                QMessageBox.information(self, "Info", "No encontrado.")

    def replace_one(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == self.txt_find.text():
            cursor.insertText(self.txt_rep.text())
            self.find_next()
        else: self.find_next()

    def replace_all(self):
        txt = self.txt_find.text()
        rep = self.txt_rep.text()
        if not txt: return
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        c = 0
        while self.editor.find(txt, self.get_flags()):
            self.editor.textCursor().insertText(rep)
            c += 1
        QMessageBox.information(self, "Info", f"Reemplazados: {c}")

# =============================================================================
# APP PRINCIPAL
# =============================================================================
class ModelManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_vault = ""
        self.current_file_path = None
        self.all_files = [] 
        self.content_cache = {} 
        self.find_dialog = None
        self.history = []        
        self.history_index = -1  
        self.is_navigating = False
        
        # Cargar configuración del vault
        self.current_vault, self.startup_file = load_vault_config()
        
        # Si no hay vault configurado, pedirlo en la primera ejecución
        if not self.current_vault or not os.path.exists(self.current_vault):
            self.select_vault_on_first_run()
        
        self.init_ui()
        
        # --- Solución para Ctrl+S BUG: Configurar atajos globales ---
        self.setup_global_shortcuts()
        # ------------------------------------------------------------
        
        if self.current_vault:
            self.ensure_vault_directory()
            self.load_models()
        
        icon_path = resource_path("app.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # --- LÓGICA DE APERTURA (Argumentos vs Inicio) ---
        opened = False
        if len(sys.argv) > 1:
            external_file = sys.argv[1]
            if os.path.exists(external_file):
                self.open_external_file(external_file)
                opened = True
        
        # Si no se abrió nada externo y tenemos un archivo de inicio configurado
        if not opened and self.startup_file and self.current_vault:
            path_inicio = os.path.join(self.current_vault, self.startup_file)
            if os.path.exists(path_inicio):
                # Seleccionarlo y abrirlo
                items = self.list_widget.findItems(self.startup_file, Qt.MatchFlag.MatchFixedString)
                if items:
                    self.list_widget.setCurrentItem(items[0])

    def select_vault_on_first_run(self):
        """Muestra el diálogo para seleccionar el vault en la primera ejecución"""
        vault_path = select_vault_directory(self, self.current_vault)
        if vault_path:
            self.current_vault = vault_path
            save_vault_config(self.current_vault)
            save_vault_history(self.current_vault)
            QMessageBox.information(self, "Vault Configurado", 
                                   f"¡Vault configurado correctamente!\n\n"
                                   f"Ubicación: {self.current_vault}\n\n"
                                   "Todos tus archivos se guardarán en esta carpeta.")
        else:
            # Si el usuario cancela, usar un vault por defecto
            default_vault = os.path.join(os.path.expanduser("~"), "Maletin_Notas")
            self.current_vault = default_vault
            save_vault_config(self.current_vault)
            save_vault_history(self.current_vault)
            os.makedirs(self.current_vault, exist_ok=True)
            QMessageBox.information(self, "Vault por Defecto", 
                                   f"Se ha creado un vault por defecto en:\n\n"
                                   f"{self.current_vault}")

    def ensure_vault_directory(self):
        """Asegura que el directorio del vault exista"""
        if self.current_vault and not os.path.exists(self.current_vault):
            try:
                os.makedirs(self.current_vault, exist_ok=True)
                QMessageBox.information(self, "Vault Creado", 
                                       f"Se ha creado el directorio del vault:\n{self.current_vault}")
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                                   f"No se pudo crear el directorio del vault:\n{e}")
                self.current_vault = ""

    def setup_global_shortcuts(self):
        """Configura atajos de teclado globales que funcionan en toda la aplicación"""
        # Ctrl+S para guardar
        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.activated.connect(self.save_model)
        
        # Ctrl+N para nuevo
        new_shortcut = QShortcut(QKeySequence.StandardKey.New, self)
        new_shortcut.activated.connect(self.new_model)
        
        # Ctrl+F para buscar
        find_shortcut = QShortcut(QKeySequence.StandardKey.Find, self)
        find_shortcut.activated.connect(self.show_find)
        
        # Ctrl+Z para deshacer
        undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        undo_shortcut.activated.connect(self.editor.undo)
        
        # Ctrl+Y para rehacer
        redo_shortcut = QShortcut(QKeySequence.StandardKey.Redo, self)
        redo_shortcut.activated.connect(self.editor.redo)

    def init_ui(self):
        self.setWindowTitle(APP_NAME)
        self.resize(1600, 950) 
        
        # Barra de estado con información del vault
        self.status_bar = self.statusBar()
        self.vault_label = QLabel(f"📁 Vault: {self.current_vault if self.current_vault else 'No configurado'}")
        self.vault_label.setStyleSheet(f"color: {C_ACCENT}; font-weight: bold; padding: 5px;")
        self.status_bar.addPermanentWidget(self.vault_label)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # IZQUIERDA
        left_p = QWidget()
        left_l = QVBoxLayout(left_p)
        left_l.setContentsMargins(0,0,0,0)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Filtrar...")
        self.search_bar.textChanged.connect(self.filter_models)
        
        # LISTA CON CONTEXT MENU
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.list_widget.currentItemChanged.connect(self.on_model_selected)
        
        btn_ref = QPushButton("🔄 REFRESCAR")
        btn_ref.clicked.connect(self.load_models)
        left_l.addWidget(self.search_bar)
        left_l.addWidget(self.list_widget)
        left_l.addWidget(btn_ref)
        
        # DERECHA
        right_p = QWidget()
        right_l = QVBoxLayout(right_p)
        right_l.setContentsMargins(0,0,0,0)
        
        self.editor = SmartLinkTextEdit(self)
        self.editor.setAcceptRichText(True)
        self.editor.textChanged.connect(self.update_stats)
        
        self.toolbar = QToolBar()
        self.setup_toolbar()
        self.create_menus()
        
        # BOTONERA
        bot_layout = QHBoxLayout()
        self.btn_save = QPushButton("GUARDAR")
        self.btn_save.clicked.connect(self.save_model)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_SUCCESS};
                color: {C_BG};
                border: 1px solid {C_SUCCESS};
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #7ec55d;
                border: 1px solid #7ec55d;
            }}
        """)
        
        self.btn_delete = QPushButton("ELIMINAR")
        self.btn_delete.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_URGENT};
                color: {C_BG};
                border: 1px solid {C_URGENT};
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #e05e7d;
                border: 1px solid #e05e7d;
            }}
        """)
        self.btn_delete.clicked.connect(self.delete_model)
        
        self.btn_copy = QPushButton("📋 COPIAR TODO")
        self.btn_copy.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_ACCENT};
                color: {C_BG};
                border: 1px solid {C_ACCENT};
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #5d8cda;
                border: 1px solid #5d8cda;
            }}
        """)
        self.btn_copy.clicked.connect(self.copy_all)
        
        bot_layout.addWidget(self.btn_save)
        bot_layout.addWidget(self.btn_delete)
        bot_layout.addWidget(self.btn_copy)
        
        right_l.addWidget(self.toolbar)
        right_l.addWidget(self.editor)
        right_l.addLayout(bot_layout)
        
        splitter.addWidget(left_p)
        splitter.addWidget(right_p)
        splitter.setSizes([350, 1150]) 
        layout.addWidget(splitter)
        
        # --- ELIMINADO: self.btn_save.setShortcut("Ctrl+S") - Ahora se maneja con atajos globales ---
        
        self.lbl_stats = QLabel("LINEAS: 0 | CARACTERES: 0")
        self.lbl_stats.setStyleSheet(f"color: {C_FG}; padding: 5px;")
        self.status_bar.addWidget(self.lbl_stats)

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if item:
            menu = QMenu()
            menu.setStyleSheet(f"""
                QMenu {{ 
                    background-color: {C_BG}; 
                    border: 1px solid {C_ACCENT}; 
                    padding: 5px;
                }}
                QMenu::item {{ 
                    padding: 8px 20px; 
                    color: {C_FG}; 
                    border-radius: 4px;
                }}
                QMenu::item:selected {{ 
                    background-color: {C_SEL}; 
                }}
            """)
            
            act_home = QAction("🏠 Establecer como Inicio", self)
            act_home.triggered.connect(lambda: self.set_as_startup(item.text()))
            menu.addAction(act_home)
            
            menu.exec(self.list_widget.mapToGlobal(pos))

    def set_as_startup(self, filename):
        try:
            save_vault_config(self.current_vault, filename)
            self.startup_file = filename
            QMessageBox.information(self, "Inicio", f"'{filename}' se abrirá al iniciar el programa.", QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la configuración: {e}")

    def add_menu_action(self, menu, text, slot, shortcut=None):
        a = QAction(text, self)
        if shortcut: a.setShortcut(shortcut)
        a.triggered.connect(slot)
        menu.addAction(a)

    def create_menus(self):
        mb = self.menuBar()
        m_file = mb.addMenu("&ARCHIVO")
        self.add_menu_action(m_file, "Nuevo", self.new_model, "Ctrl+N")
        # --- CORREGIDO: Eliminar shortcut del menú para evitar conflictos ---
        self.add_menu_action(m_file, "Guardar", self.save_model)
        m_file.addSeparator()
        self.add_menu_action(m_file, "Abrir...", self.open_any_file)
        self.add_menu_action(m_file, "Localizar Maletín...", self.select_vault_directory_menu)
        m_file.addSeparator()
        self.add_menu_action(m_file, "Salir", self.close)
        
        m_edit = mb.addMenu("&EDICIÓN")
        self.add_menu_action(m_edit, "Buscar...", self.show_find, "Ctrl+F")
        m_edit.addSeparator()
        self.add_menu_action(m_edit, "Deshacer", self.editor.undo, "Ctrl+Z")
        self.add_menu_action(m_edit, "Rehacer", self.editor.redo, "Ctrl+Y")
        
        m_ins = mb.addMenu("&INSERTAR")
        self.add_menu_action(m_ins, "Imagen...", self.insert_image)
        self.add_menu_action(m_ins, "Tabla...", self.insert_table)
        self.add_menu_action(m_ins, "Hipervínculo...", self.insert_hyperlink)
        
        m_fmt = mb.addMenu("&FORMATO")
        m_align = m_fmt.addMenu("Alineación")
        self.add_menu_action(m_align, "Izquierda", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft))
        self.add_menu_action(m_align, "Centro", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignCenter))
        self.add_menu_action(m_align, "Derecha", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignRight))
        self.add_menu_action(m_align, "Justificado", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignJustify))
        
        m_list = m_fmt.addMenu("Listas")
        self.add_menu_action(m_list, "Viñetas", lambda: self.editor.textCursor().createList(QTextListFormat.Style.ListDisc))
        self.add_menu_action(m_list, "Numeración", lambda: self.editor.textCursor().createList(QTextListFormat.Style.ListDecimal))

    def setup_toolbar(self):
        self.act_back = QAction("◀", self)
        self.act_back.triggered.connect(self.go_back)
        self.act_back.setEnabled(False) 
        self.toolbar.addAction(self.act_back)

        self.act_fwd = QAction("▶", self)
        self.act_fwd.triggered.connect(self.go_forward)
        self.act_fwd.setEnabled(False) 
        self.toolbar.addAction(self.act_fwd)

        self.toolbar.addSeparator()

        self.font_box = QFontComboBox()
        self.font_box.currentFontChanged.connect(self.editor.setCurrentFont)
        self.toolbar.addWidget(self.font_box)
        
        self.size_box = QSpinBox()
        self.size_box.setValue(16)
        self.size_box.valueChanged.connect(lambda s: self.editor.setFontPointSize(s))
        self.toolbar.addWidget(self.size_box)
        self.toolbar.addSeparator()
        
        def tb_act(txt, slot, short=None):
            a = QAction(txt, self)
            a.triggered.connect(slot)
            if short: a.setShortcut(short)
            self.toolbar.addAction(a)
            
        tb_act("𝐁", lambda: self.set_fmt("bold"), "Ctrl+B")
        tb_act("𝐼", lambda: self.set_fmt("italic"), "Ctrl+I")
        tb_act("U̲", lambda: self.set_fmt("under"), "Ctrl+U")
        self.toolbar.addSeparator()
        tb_act("🎨", self.set_color)
        tb_act("🖍️", self.set_bg)
        
        self.toolbar.addSeparator()
        tb_act("|<", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft))
        tb_act("><", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignCenter))
        tb_act(">|", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignRight))
        tb_act("|=|", lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignJustify))
        
        self.toolbar.addSeparator()
        self.btn_open = QAction("📂 ABRIR", self)
        self.btn_open.triggered.connect(self.open_any_file)
        self.toolbar.addAction(self.btn_open)

    def select_vault_directory_menu(self):
        """Permite cambiar el vault desde el menú"""
        vault_path = select_vault_directory(self, self.current_vault)
        if vault_path and vault_path != self.current_vault:
            # Preguntar si guardar cambios antes de cambiar de vault
            if self.current_file_path and self.editor.document().isModified():
                reply = QMessageBox.question(self, "Cambiar Vault", 
                                            "Hay cambios sin guardar. ¿Guardar antes de cambiar de vault?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
                if reply == QMessageBox.StandardButton.Cancel:
                    return
                if reply == QMessageBox.StandardButton.Yes:
                    self.save_model()
            
            self.current_vault = vault_path
            save_vault_config(self.current_vault, self.startup_file)
            save_vault_history(self.current_vault)
            self.ensure_vault_directory()
            
            # Actualizar interfaz
            self.vault_label.setText(f"📁 Vault: {self.current_vault}")
            self.load_models()
            self.editor.clear()
            self.current_file_path = None
            
            QMessageBox.information(self, "Vault Cambiado", 
                                   f"¡Vault cambiado exitosamente!\n\n"
                                   f"Ubicación: {self.current_vault}")

    def add_to_history(self, filepath):
        if self.is_navigating: return
        if self.history and self.history_index >= 0:
            if self.history[self.history_index] == filepath: return
        self.history = self.history[:self.history_index + 1]
        self.history.append(filepath)
        self.history_index += 1
        self.update_nav_buttons()

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            path = self.history[self.history_index]
            self.is_navigating = True
            self.load_file(path) 
            self.is_navigating = False
            self.update_nav_buttons()

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            path = self.history[self.history_index]
            self.is_navigating = True
            self.load_file(path)
            self.is_navigating = False
            self.update_nav_buttons()

    def update_nav_buttons(self):
        self.act_back.setEnabled(self.history_index > 0)
        self.act_fwd.setEnabled(self.history_index < len(self.history) - 1)

    def handle_link(self, url):
        if url.startswith("model://"):
            target = url.replace("model://", "")
            self.handle_internal_link(target)
        else:
            try:
                QDesktopServices.openUrl(QUrl(url))
                self.status_bar.showMessage(f"Abriendo: {url}")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def handle_internal_link(self, target_name):
        target_file = None
        for f in self.all_files:
            if os.path.splitext(f)[0].lower() == target_name.lower():
                target_file = f
                break
        
        if target_file and self.current_vault:
            if self.check_save():
                path = os.path.join(self.current_vault, target_file)
                self.load_file(path)
        else:
            self.handle_external_link(target_name)

    def handle_external_link(self, url):
        try:
            if not url.startswith(('http://', 'https://')):
                reply = QMessageBox.question(self, "Crear", f"'{url}' no existe. ¿Crear Modelo?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    if self.check_save(): self.create_new(url)
                return

            QDesktopServices.openUrl(QUrl(url))
            self.status_bar.showMessage(f"Abriendo URL: {url}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error abriendo: {e}")

    def open_any_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", "", "Archivos (*.rtf *.md *.txt);;Todos (*.*)")
        if path:
            self.open_external_file(path)

    def open_external_file(self, filepath):
        try:
            ext = os.path.splitext(filepath)[1].lower()
            content = ""
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()

            if ext == '.md':
                content = self.parse_markdown_visual(raw_text)
            else:
                content = raw_text

            filename = os.path.basename(filepath)
            filename = os.path.splitext(filename)[0] + ".rtf"
            
            if not self.current_vault:
                vault_path = select_vault_directory(self, self.current_vault)
                if vault_path:
                    self.current_vault = vault_path
                    save_vault_config(self.current_vault)
                    save_vault_history(self.current_vault)
                    self.ensure_vault_directory()
                else:
                    return
            
            target_path = os.path.join(self.current_vault, filename)
            
            if "{\\rtf" in content or "<html" in content or ext == '.md':
                self.editor.setHtml(content)
            else:
                self.editor.setPlainText(content)
            
            self.editor.setFontPointSize(16)
            self.current_file_path = target_path
            self.save_model() 
            self.load_models() 
            self.status_bar.showMessage(f"Abierto e Importado: {filename}")
            
            items = self.list_widget.findItems(filename, Qt.MatchFlag.MatchFixedString)
            if items: self.list_widget.setCurrentItem(items[0])

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir:\n{e}")

    def parse_markdown_visual(self, text):
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = re.sub(r'^# (.*?)$', r'<h1 style="font-size:24pt; color:#7aa2f7;">\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'<h2 style="font-size:20pt; color:#7aa2f7;">\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        text = re.sub(r'\[\[(.*?)\]\]', r'<a href="model://\1" style="color:#7dcfff;">\1</a>', text)
        text = text.replace('\n', '<br>')
        return text

    def create_new(self, name):
        if not self.current_vault:
            vault_path = select_vault_directory(self, self.current_vault)
            if vault_path:
                self.current_vault = vault_path
                save_vault_config(self.current_vault)
                save_vault_history(self.current_vault)
                self.ensure_vault_directory()
            else:
                return
        
        filename = f"{name}.rtf"
        path = os.path.join(self.current_vault, filename)
        try:
            with open(path, 'w', encoding='utf-8') as f: f.write("")
            self.load_models()
            self.load_file(path)
            self.status_bar.showMessage(f"Creado: {filename}")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def check_save(self):
        if self.editor.document().isModified():
            r = QMessageBox.question(self, "Guardar", "Cambios pendientes. ¿Guardar?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if r == QMessageBox.StandardButton.Cancel: return False
            if r == QMessageBox.StandardButton.Yes: self.save_model()
        return True

    def load_models(self):
        """Carga los archivos del vault actual"""
        if not self.current_vault or not os.path.exists(self.current_vault):
            self.list_widget.clear()
            self.all_files = []
            self.content_cache = {}
            self.vault_label.setText("📁 Vault: No configurado")
            return
        
        self.list_widget.clear()
        self.all_files = []
        self.content_cache = {}
        try:
            for f in os.listdir(self.current_vault):
                if f.lower().endswith(('.rtf','.txt','.html')):
                    path = os.path.join(self.current_vault, f)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read().lower()
                        self.content_cache[f] = content
                    except: self.content_cache[f] = ""
                    self.all_files.append(f)
                    self.list_widget.addItem(f)
            
            # Actualizar etiqueta del vault
            self.vault_label.setText(f"📁 Vault: {self.current_vault}")
        except Exception as e:
            print(f"Error al cargar modelos: {e}")
            QMessageBox.warning(self, "Error", f"No se pudieron cargar los archivos del vault:\n{e}")

    def filter_models(self, txt):
        txt = txt.lower()
        self.list_widget.clear()
        for f in self.all_files:
            content = self.content_cache.get(f, "")
            if txt in f.lower() or txt in content:
                self.list_widget.addItem(f)

    def on_model_selected(self, curr, prev):
        if not curr: return
        if not self.current_vault:
            return
        
        path = os.path.join(self.current_vault, curr.text())
        if path == self.current_file_path: return
        if self.check_save(): self.load_file(path)

    def load_file(self, path):
        if not os.path.exists(path): 
            QMessageBox.warning(self, "Error", f"El archivo no existe:\n{path}")
            return
        
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if "{\\rtf" in content or "<html" in content: self.editor.setHtml(content)
            else: self.editor.setPlainText(content)
            
            self.current_file_path = path
            self.editor.document().setModified(False)
            self.status_bar.showMessage(f"Archivo: {os.path.basename(path)}")
            
            self.editor.setFontPointSize(16)
            self.size_box.blockSignals(True)
            self.size_box.setValue(16)
            self.size_box.blockSignals(False)
            
            self.update_stats()
            
            fn = os.path.basename(path)
            items = self.list_widget.findItems(fn, Qt.MatchFlag.MatchFixedString)
            if items:
                self.list_widget.blockSignals(True)
                self.list_widget.setCurrentItem(items[0])
                self.list_widget.blockSignals(False)
            self.add_to_history(path)
        except Exception as e: 
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{e}")

    def save_model(self):
        """Método mejorado para guardar con mejor manejo de errores"""
        if not self.current_vault:
            vault_path = select_vault_directory(self, self.current_vault)
            if vault_path:
                self.current_vault = vault_path
                save_vault_config(self.current_vault)
                save_vault_history(self.current_vault)
                self.ensure_vault_directory()
            else:
                return False
        
        if self.current_file_path:
            content = self.editor.toHtml()
            try:
                # Validar que el contenido no esté vacío
                if not content.strip():
                    reply = QMessageBox.question(self, "Guardar", "El contenido está vacío. ¿Guardar igual?",
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No:
                        return False
                
                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.editor.document().setModified(False)
                self.status_bar.showMessage(f"Guardado: {os.path.basename(self.current_file_path)}", 3000)
                
                # Actualizar el título de la ventana para mostrar estado guardado
                current_title = self.windowTitle()
                if "*" in current_title:
                    self.setWindowTitle(APP_NAME)
                    
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error de Guardado", 
                                   f"No se pudo guardar el archivo:\n\n{str(e)}\n\n"
                                   f"Ruta: {self.current_file_path}")
                return False
        else:
            name, ok = QInputDialog.getText(self, "Guardar como", "Nombre del archivo:")
            if ok and name.strip():
                # Asegurar que tenga extensión .rtf
                if not name.lower().endswith('.rtf'):
                    name += ".rtf"
                
                # Validar nombre de archivo
                if any(char in name for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
                    QMessageBox.warning(self, "Nombre inválido", "El nombre no puede contener caracteres especiales como /, \\, :, *, ?, \", <, >, |")
                    return False
                
                path = os.path.join(self.current_vault, name)
                
                # Verificar si el archivo ya existe
                if os.path.exists(path):
                    reply = QMessageBox.question(self, "Archivo existente", 
                                               f"El archivo '{name}' ya existe. ¿Sobrescribir?",
                                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No:
                        return False
                
                self.current_file_path = path
                return self.save_model()
            return False
        
        return False

    def new_model(self):
        if self.check_save():
            self.editor.clear()
            self.current_file_path = None
            self.list_widget.clearSelection()
            self.editor.setFontPointSize(16)
            self.setWindowTitle(f"{APP_NAME} - Nuevo documento")
            return True
        return False

    def delete_model(self):
        if not self.current_file_path: return
        reply = QMessageBox.question(self, "Eliminar", f"¿Eliminar '{os.path.basename(self.current_file_path)}'?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(self.current_file_path)
                self.current_file_path = None
                self.editor.clear()
                self.load_models()
                self.status_bar.showMessage("Archivo eliminado.")
                self.setWindowTitle(APP_NAME)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    # --- TOOLS ---
    def set_fmt(self, t):
        f = self.editor.fontWeight()
        if t=="bold": self.editor.setFontWeight(QFont.Weight.Bold if f!=QFont.Weight.Bold else QFont.Weight.Normal)
        if t=="italic": self.editor.setFontItalic(not self.editor.fontItalic())
        if t=="under": self.editor.setFontUnderline(not self.editor.fontUnderline())
    
    def set_color(self):
        c = QColorDialog.getColor()
        if c.isValid(): self.editor.setTextColor(c)
    def set_bg(self):
        c = QColorDialog.getColor()
        if c.isValid(): self.editor.setTextBackgroundColor(c)
    
    def insert_image(self):
        p, _ = QFileDialog.getOpenFileName(self, "Img", "", "Img (*.png *.jpg *.jpeg *.gif *.bmp)")
        if p:
            img = QPixmap(p)
            if img.width()>500: img=img.scaledToWidth(500)
            self.editor.document().addResource(QTextDocument.ResourceType.ImageResource, QUrl(p), img)
            self.editor.textCursor().insertImage(p)
    
    def insert_table(self):
        r,ok1=QInputDialog.getInt(self,"F","F:",2, 1, 100)
        c,ok2=QInputDialog.getInt(self,"C","C:",2, 1, 100)
        if ok1 and ok2:
            fmt = QTextTableFormat()
            fmt.setBorder(1); fmt.setBorderBrush(QColor(C_BORDER)); fmt.setCellPadding(5)
            self.editor.textCursor().insertTable(r, c, fmt)

    def insert_hyperlink(self):
        dlg = InsertLinkDialog(self)
        if dlg.exec():
            txt, url = dlg.result_data
            self.editor.textCursor().insertHtml(f'<a href="{url}">{txt}</a>')

    def copy_all(self):
        self.editor.selectAll()
        self.editor.copy()
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        self.status_bar.showMessage("Copiado")

    def show_find(self):
        if not self.find_dialog: self.find_dialog = FindReplaceDialog(self, self.editor)
        self.find_dialog.show()
        c = self.editor.textCursor()
        if c.hasSelection():
            self.find_dialog.txt_find.setText(c.selectedText())

    def update_stats(self):
        t = self.editor.toPlainText()
        self.lbl_stats.setText(f"LÍNEAS: {self.editor.document().blockCount()} | CARACTERES: {len(t)}")
        
        # Actualizar título de la ventana si hay cambios sin guardar
        if self.editor.document().isModified():
            if "*" not in self.windowTitle():
                self.setWindowTitle(f"*{self.windowTitle()}")
        else:
            if self.windowTitle().startswith("*"):
                self.setWindowTitle(self.windowTitle()[1:])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(TOKYO_STYLESHEET)
    w = ModelManagerApp()
    w.show()
    sys.exit(app.exec())