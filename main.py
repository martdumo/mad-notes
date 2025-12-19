import sys
import os
import re
import ctypes
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QTextEdit, QLineEdit, 
                             QPushButton, QSplitter, QMessageBox, QToolBar, 
                             QColorDialog, QFontComboBox, QSpinBox, QFileDialog,
                             QInputDialog, QLabel, QMenu, QMenuBar, QDialog, 
                             QGridLayout, QCheckBox)
from PyQt6.QtGui import (QAction, QIcon, QFont, QColor, QTextCursor, 
                         QTextListFormat, QTextTableFormat, QTextCharFormat,
                         QTextBlockFormat, QTextDocument, QPixmap, QDesktopServices,
                         QSyntaxHighlighter)
from PyQt6.QtCore import Qt, QSize, QUrl, QRegularExpression

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
APP_NAME = "Gestor Maletín MD (Markdown Edition)"

# ID para la barra de tareas de Windows
myappid = 'martdumo.maletin.md.v1' 
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

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# CAMBIO: CARPETA AHORA ES "maletin"
MODELS_DIR = os.path.join(BASE_DIR, "maletin")

# ESTILOS (14pt Base)
DARK_STYLESHEET = """
QMainWindow, QWidget, QDialog {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14pt;
}
QListWidget {
    background-color: #252526;
    color: #f0f0f0;
    border: 1px solid #3e3e42;
    border-radius: 4px;
    padding: 8px;
}
QListWidget::item:selected {
    background-color: #094771;
    color: white;
}
QTextEdit {
    background-color: #1e1e1e;
    color: #ffffff;
    border: 1px solid #3e3e42;
    selection-background-color: #264f78;
}
QLineEdit {
    background-color: #2d2d30;
    color: #ffffff;
    border: 1px solid #3e3e42;
    padding: 8px;
    border-radius: 4px;
}
QPushButton {
    background-color: #3e3e42;
    color: white;
    border: none;
    padding: 10px 16px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #505050;
}
QPushButton:pressed {
    background-color: #007acc;
}
QToolBar {
    background-color: #2d2d30;
    border-bottom: 1px solid #3e3e42;
    spacing: 8px;
}
QToolButton {
    background-color: transparent; 
    border-radius: 4px; 
    padding: 6px;
}
QToolButton:hover {
    background-color: #3e3e42;
}
QToolButton:disabled {
    color: #555555;
}
QMenuBar {
    background-color: #2d2d30;
    color: #ffffff;
    font-size: 14pt;
}
QMenuBar::item {
    padding: 8px 12px;
}
QMenuBar::item:selected {
    background-color: #3e3e42;
}
QMenu {
    background-color: #2d2d30;
    border: 1px solid #3e3e42;
    font-size: 14pt;
}
QMenu::item:selected {
    background-color: #094771;
}
QStatusBar {
    background-color: #2d2d30;
    color: #e0e0e0;
    border-top: 1px solid #3e3e42;
}
QLabel { color: #e0e0e0; }
"""

# =============================================================================
# DIÁLOGOS Y CLASES AUXILIARES
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
        self.txt_text = QLineEdit()
        lbl_url = QLabel("Dirección (URL):")
        self.txt_url = QLineEdit()
        self.txt_url.setPlaceholderText("https://... o model://...")
        
        btn_ok = QPushButton("Insertar")
        btn_ok.clicked.connect(self.on_ok)
        btn_cancel = QPushButton("Cancelar")
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

class MarkdownLinkHighlighter(QSyntaxHighlighter):
    """Resalta visualmente sintaxis Markdown cruda si aparece"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wiki_link_format = QTextCharFormat()
        self.wiki_link_format.setForeground(QColor("#C586C0")) # Violeta para brackets
        self.wiki_link_format.setFontWeight(QFont.Weight.Bold)
        
        # Detectar [[link]] crudo
        self.wiki_pattern = QRegularExpression(r"\[\[.*?\]\]")

    def highlightBlock(self, text):
        match_iterator = self.wiki_pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.wiki_link_format)

class SmartMarkdownTextEdit(QTextEdit):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.highlighter = MarkdownLinkHighlighter(self.document())
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        # Estilo CSS para enlaces renderizados
        self.document().setDefaultStyleSheet("a { text-decoration: none; color: #4EC9B0; font-weight: bold; }")
        
        font = self.font()
        font.setPointSize(14)
        self.setFont(font)

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)
        # CAMBIO: Detectar cierre de brackets ']'
        if event.text() == "]": self.check_magic_tag()

    def check_magic_tag(self):
        """Convierte [[texto]] en un link visual al escribir"""
        cursor = self.textCursor()
        block_text = cursor.block().text()
        pos_in_block = cursor.positionInBlock()
        text_before = block_text[:pos_in_block]
        
        # Regex para buscar [[algo]] al final
        # Escapamos los corchetes
        match = re.search(r"\[\[([\w\s\.-]+)\]\]$", text_before)
        if match:
            model_name = match.group(1)
            full_tag = match.group(0)
            
            # Borrar [[texto]] e insertar Link HTML real (visual)
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, len(full_tag))
            cursor.removeSelectedText()
            
            # Usamos el protocolo model://
            html = f'<a href="model://{model_name}">{model_name}</a>&nbsp;'
            cursor.insertHtml(html)
            self.setFontPointSize(14) # Restaurar tamaño

    def mouseMoveEvent(self, event):
        # Detectar hover sobre links
        if self.anchorAt(event.pos()):
            self.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.viewport().setCursor(Qt.CursorShape.IBeamCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Click simple para navegar
        if event.button() == Qt.MouseButton.LeftButton:
            url = self.anchorAt(event.pos())
            if url:
                self.parent_window.handle_link(url)
                return 
        super().mouseReleaseEvent(event)

class FindReplaceDialog(QDialog):
    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Buscar y Reemplazar")
        self.setWindowFlags(Qt.WindowType.Window) 
        self.resize(500, 200)
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        layout.setVerticalSpacing(15)
        self.lbl_find = QLabel("Buscar:")
        self.txt_find = QLineEdit()
        self.lbl_rep = QLabel("Reemplazar:")
        self.txt_rep = QLineEdit()
        self.chk_case = QCheckBox("Mayús/Minús")
        self.btn_find = QPushButton("Buscar Siguiente")
        self.btn_rep = QPushButton("Reemplazar")
        self.btn_all = QPushButton("Reemplazar Todo")
        
        self.btn_find.clicked.connect(self.find_next)
        self.btn_rep.clicked.connect(self.replace_one)
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
        self.current_file_path = None
        self.all_files = [] 
        self.content_cache = {} 
        self.find_dialog = None
        
        self.history = []        
        self.history_index = -1  
        self.is_navigating = False
        
        self.init_ui()
        self.ensure_directory()
        self.load_models()

        icon_path = resource_path("app.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def ensure_directory(self):
        if not os.path.exists(MODELS_DIR): os.makedirs(MODELS_DIR)

    def init_ui(self):
        self.setWindowTitle(APP_NAME)
        self.resize(1500, 900) 
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- IZQUIERDA ---
        left_p = QWidget()
        left_l = QVBoxLayout(left_p)
        left_l.setContentsMargins(0,0,0,0)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Filtrar...")
        self.search_bar.textChanged.connect(self.filter_models)
        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self.on_model_selected)
        btn_ref = QPushButton("🔄 Refrescar")
        btn_ref.clicked.connect(self.load_models)
        left_l.addWidget(self.search_bar)
        left_l.addWidget(self.list_widget)
        left_l.addWidget(btn_ref)
        
        # --- DERECHA ---
        right_p = QWidget()
        right_l = QVBoxLayout(right_p)
        right_l.setContentsMargins(0,0,0,0)
        
        self.editor = SmartMarkdownTextEdit(self)
        self.editor.setAcceptRichText(True) # Necesario para mostrar imágenes y links visuales
        self.editor.textChanged.connect(self.update_stats)
        
        self.toolbar = QToolBar()
        self.setup_toolbar()
        self.create_menus()
        
        # --- BOTONERA ---
        bot_layout = QHBoxLayout()
        self.btn_save = QPushButton("Guardar")
        self.btn_save.clicked.connect(self.save_model)
        
        self.btn_delete = QPushButton("Eliminar")
        self.btn_delete.setStyleSheet("background-color: #8B0000; font-weight: bold;")
        self.btn_delete.clicked.connect(self.delete_model)
        
        self.btn_copy = QPushButton("📋 COPIAR TODO")
        self.btn_copy.setStyleSheet("background-color: #006400; font-weight: bold;")
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
        
        self.status_bar = self.statusBar()
        self.lbl_stats = QLabel("L: 0 | C: 0")
        self.status_bar.addPermanentWidget(self.lbl_stats)

    def add_menu_action(self, menu, text, slot, shortcut=None):
        a = QAction(text, self)
        if shortcut: a.setShortcut(shortcut)
        a.triggered.connect(slot)
        menu.addAction(a)

    def create_menus(self):
        mb = self.menuBar()
        m_file = mb.addMenu("&Archivo")
        self.add_menu_action(m_file, "Nuevo", self.new_model, "Ctrl+N")
        self.add_menu_action(m_file, "Guardar", self.save_model, "Ctrl+S")
        m_file.addSeparator()
        self.add_menu_action(m_file, "Importar Masivo (.txt)", self.mass_import)
        m_file.addSeparator()
        self.add_menu_action(m_file, "Salir", self.close)
        
        m_edit = mb.addMenu("&Editar")
        self.add_menu_action(m_edit, "Buscar...", self.show_find, "Ctrl+F")
        m_edit.addSeparator()
        self.add_menu_action(m_edit, "Deshacer", self.editor.undo, "Ctrl+Z")
        self.add_menu_action(m_edit, "Rehacer", self.editor.redo, "Ctrl+Y")
        
        m_ins = mb.addMenu("&Insertar")
        self.add_menu_action(m_ins, "Imagen...", self.insert_image)
        self.add_menu_action(m_ins, "Tabla...", self.insert_table)
        self.add_menu_action(m_ins, "Hipervínculo...", self.insert_hyperlink)
        
        m_fmt = mb.addMenu("&Formato")
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
        self.size_box.setValue(14)
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
        # CAMBIO: Usar model:// para links internos
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
        
        if target_file:
            if self.check_save():
                path = os.path.join(MODELS_DIR, target_file)
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

    def create_new(self, name):
        # CAMBIO: Extensión .md
        filename = f"{name}.md"
        path = os.path.join(MODELS_DIR, filename)
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
        self.list_widget.clear()
        self.all_files = []
        self.content_cache = {}
        try:
            for f in os.listdir(MODELS_DIR):
                # CAMBIO: Solo buscar MD (y TXT/HTML legacy si quieres, pero nos enfocamos en MD)
                if f.lower().endswith('.md'):
                    path = os.path.join(MODELS_DIR, f)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read().lower()
                        self.content_cache[f] = content
                    except: self.content_cache[f] = ""
                    
                    self.all_files.append(f)
                    self.list_widget.addItem(f)
        except: pass

    def filter_models(self, txt):
        txt = txt.lower()
        self.list_widget.clear()
        for f in self.all_files:
            content = self.content_cache.get(f, "")
            if txt in f.lower() or txt in content:
                self.list_widget.addItem(f)

    def on_model_selected(self, curr, prev):
        if not curr: return
        path = os.path.join(MODELS_DIR, curr.text())
        if path == self.current_file_path: return
        if self.check_save(): self.load_file(path)

    def load_file(self, path):
        if not os.path.exists(path): return
        try:
            # 1. LEER RAW MARKDOWN
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 2. PROCESAR [[LINKS]] PARA QUE SEAN VISUALES (HTML)
            # Regex: [[Algo]] -> <a href="model://Algo">Algo</a>
            # Esto es lo que permite que se vean "bonitos" en el editor
            def replace_wiki_link(match):
                name = match.group(1)
                return f'<a href="model://{name}">{name}</a>'
            
            # Reemplazar [[Wiki]] por HTML
            processed_content = re.sub(r'\[\[([\w\s\.-]+)\]\]', replace_wiki_link, content)
            
            # 3. CARGAR EN EDITOR
            # Usamos setMarkdown si fuera MD puro, pero como inyectamos HTML (<a>), usamos setHtml o setMarkdown con dialecto.
            # setMarkdown de Qt NO soporta tags <a> arbitrarios facilmente. 
            # TRUCO: Usamos setHtml para que interprete los links, pero PyQt convierte MD a HTML automágicamente con setMarkdown.
            # Vamos a usar setMarkdown y confiar en que Qt renderice los links estándar.
            # Mejor aun: Convertimos [[Wiki]] a [Wiki](model://Wiki) que es Markdown estándar.
            
            md_content = re.sub(r'\[\[([\w\s\.-]+)\]\]', r'[\1](model://\1)', content)
            
            self.editor.setMarkdown(md_content)
            
            self.current_file_path = path
            self.editor.document().setModified(False)
            self.status_bar.showMessage(f"Archivo: {os.path.basename(path)}")
            
            self.editor.setFontPointSize(14)
            self.size_box.blockSignals(True)
            self.size_box.setValue(14)
            self.size_box.blockSignals(False)
            
            self.update_stats()
            
            fn = os.path.basename(path)
            items = self.list_widget.findItems(fn, Qt.MatchFlag.MatchFixedString)
            if items:
                self.list_widget.blockSignals(True)
                self.list_widget.setCurrentItem(items[0])
                self.list_widget.blockSignals(False)
            self.add_to_history(path)
        except Exception as e: print(f"Error: {e}")

    def save_model(self):
        if self.current_file_path:
            # 1. OBTENER MARKDOWN DE QT
            # Qt devuelve Markdown estándar: [Nombre](model://Nombre)
            markdown_out = self.editor.toMarkdown()
            
            # 2. REVERTIR LINKS AL FORMATO [[Wiki]]
            # Convertir [Nombre](model://Nombre) -> [[Nombre]]
            # Regex busca: [CualquierCosa](model://CualquierCosa)
            # Nota: Qt a veces agrega escapes.
            
            # Patrón simple: [Texto](model://Texto)
            markdown_final = re.sub(r'\[(.*?)\]\(model://.*?\)', r'[[\1]]', markdown_out)
            
            # Guardar
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_final)
            
            # Cache update
            self.content_cache[os.path.basename(self.current_file_path)] = markdown_final.lower()
            
            self.editor.document().setModified(False)
            self.status_bar.showMessage("Guardado (MD).")
        else:
            name, ok = QInputDialog.getText(self, "Guardar", "Nombre:")
            if ok and name:
                if not name.lower().endswith('.md'): name+=".md"
                path = os.path.join(MODELS_DIR, name)
                self.current_file_path = path
                self.save_model()
                self.load_models()
                self.add_to_history(path)

    def new_model(self):
        if self.check_save():
            self.editor.clear()
            self.current_file_path = None
            self.list_widget.clearSelection()
            self.editor.setFontPointSize(14) 

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
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def mass_import(self):
        if QMessageBox.question(self, "Importar", "¿Convertir todos .txt a .md?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            c=0
            for f in os.listdir(MODELS_DIR):
                if f.endswith(".txt"):
                    base = os.path.splitext(f)[0]
                    p = os.path.join(MODELS_DIR, f)
                    rp = os.path.join(MODELS_DIR, base+".md")
                    if not os.path.exists(rp):
                        with open(p, 'r', encoding='utf-8', errors='ignore') as fi: t=fi.read()
                        with open(rp, 'w', encoding='utf-8') as fo: 
                            fo.write(t) # Guardar texto plano como MD
                        c+=1
            self.load_models()
            QMessageBox.information(self,"Info",f"Hecho: {c}")

    # --- TOOLS ---
    def set_fmt(self, t):
        # En modo Markdown (setMarkdown), Qt maneja esto automáticamente como RichText visual
        # pero al guardar con toMarkdown() lo convierte a **bold**, *italic*, etc.
        f = self.editor.fontWeight()
        if t=="bold": self.editor.setFontWeight(QFont.Weight.Bold if f!=QFont.Weight.Bold else QFont.Weight.Normal)
        if t=="italic": self.editor.setFontItalic(not self.editor.fontItalic())
        if t=="under": self.editor.setFontUnderline(not self.editor.fontUnderline())
    
    def set_color(self):
        # OJO: Markdown estándar NO soporta colores. Qt lo mostrará, pero toMarkdown() podría ignorarlo
        # o guardarlo como HTML <span> si el dialecto lo permite.
        c = QColorDialog.getColor()
        if c.isValid(): self.editor.setTextColor(c)
    def set_bg(self):
        c = QColorDialog.getColor()
        if c.isValid(): self.editor.setTextBackgroundColor(c)
    
    def insert_image(self):
        p, _ = QFileDialog.getOpenFileName(self, "Img", "", "Img (*.png *.jpg)")
        if p:
            img = QPixmap(p)
            if img.width()>500: img=img.scaledToWidth(500)
            self.editor.document().addResource(QTextDocument.ResourceType.ImageResource, QUrl(p), img)
            self.editor.textCursor().insertImage(p)
    
    def insert_table(self):
        r,ok1=QInputDialog.getInt(self,"F","F:",2)
        c,ok2=QInputDialog.getInt(self,"C","C:",2)
        if ok1 and ok2:
            fmt = QTextTableFormat()
            fmt.setBorder(1); fmt.setBorderBrush(QColor("white")); fmt.setCellPadding(5)
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
        self.lbl_stats.setText(f"Líneas: {self.editor.document().blockCount()} | Caracteres: {len(t)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLESHEET)
    w = ModelManagerApp()
    w.show()
    sys.exit(app.exec())