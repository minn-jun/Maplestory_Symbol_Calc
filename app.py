import sys
from pathlib import Path

import requests
from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from api_handler import NexonAPI
from config import NEXON_API_KEY
from optimizer import find_best_solutions
from symbol_data import (
    AREA_ORDER,
    KEY_TO_NAME_MAP,
    SYMBOL_AREAS,
    get_accessible_areas,
    get_area_key_from_symbol_name,
    get_areas_for_mode,
)


MODE_LABELS = {
    "arcane": "아케인포스",
    "authentic": "어센틱포스",
}

def resource_path(*parts):
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_dir.joinpath(*parts)


SYMBOL_ICON_DIR = resource_path("assets", "symbols")
APP_ICON_PATH = resource_path("assets", "app_icon.png")
SYMBOL_ICON_SIZE = 22
WORLD_ICON_DIR = resource_path("assets", "worlds")
WORLD_ICON_SIZE = 22
ROUTE_ICON_SIZE = 18

WORLD_ICON_KEYS = {
    "스카니아": "scania",
    "베라": "bera",
    "루나": "luna",
    "제니스": "zenith",
    "크로아": "croa",
    "유니온": "union",
    "엘리시움": "elysium",
    "이노시스": "enosis",
    "레드": "red",
    "오로라": "aurora",
    "아케인": "arcane",
    "노바": "nova",
    "리부트": "reboot",
    "리부트2": "reboot",
    "버닝": "burning",
}


class CharacterLoadWorker(QThread):
    loaded = Signal(dict, dict, bytes)
    failed = Signal(str)

    def __init__(self, character_name):
        super().__init__()
        self.character_name = character_name

    def run(self):
        try:
            api = NexonAPI(NEXON_API_KEY)
            character_info = api.get_character_info(self.character_name)
            symbol_info = api.get_symbol_info(self.character_name)
            image_bytes = self._fetch_image(character_info.get("character_image"))
            self.loaded.emit(character_info, symbol_info, image_bytes)
        except Exception as exc:
            self.failed.emit(str(exc))

    def _fetch_image(self, image_url):
        if not image_url:
            return b""
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
        return response.content


class MapleSymbolOptimizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maple Symbol Optimizer")
        if APP_ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(APP_ICON_PATH)))
        self.resize(1180, 780)

        self.character_info = {}
        self.symbol_info = {}
        self.current_symbols = {}
        self.worker = None

        self._setup_ui()
        self._apply_style()
        self._populate_symbol_table()

    def _setup_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)

        layout.addLayout(self._build_header())
        layout.addWidget(self._build_summary_panel())
        layout.addWidget(self._build_tabs(), 1)
        layout.addLayout(self._build_status_bar())

    def _build_header(self):
        header = QHBoxLayout()
        header.setSpacing(12)

        title_box = QVBoxLayout()
        title = QLabel("심볼 강화 최적화")
        title.setObjectName("title")
        subtitle = QLabel("목표 포스까지 최소 비용 강화 경로를 계산합니다.")
        subtitle.setObjectName("subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        search_label = QLabel("캐릭터 검색")
        search_label.setObjectName("fieldLabel")

        self.character_input = QLineEdit()
        self.character_input.setPlaceholderText("캐릭터명")
        self.character_input.returnPressed.connect(self.load_character)

        self.load_button = QPushButton("조회")
        self.load_button.setObjectName("primaryButton")
        self.load_button.clicked.connect(self.load_character)

        header.addLayout(title_box, 1)
        header.addWidget(search_label)
        header.addWidget(self.character_input)
        header.addWidget(self.load_button)
        return header

    def _build_summary_panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 10, 14, 10)
        layout.setSpacing(14)

        self.character_image = QLabel("No Image")
        self.character_image.setObjectName("characterImage")
        self.character_image.setAlignment(Qt.AlignCenter)
        self.character_image.setFixedSize(106, 106)

        info_grid = QGridLayout()
        info_grid.setHorizontalSpacing(34)
        info_grid.setVerticalSpacing(3)

        self.summary_labels = {}
        fields = [
            ("character_name", "캐릭터", "-"),
            ("world_name", "월드", "-"),
            ("character_guild_name", "길드", "-"),
            ("character_class", "직업", "-"),
            ("character_level", "레벨", "-"),
        ]

        for index, (key, label, default) in enumerate(fields):
            label_widget = QLabel(label)
            label_widget.setObjectName("summaryLabel")

            info_grid.addWidget(label_widget, 0, index)

            if key == "world_name":
                value_widget = QWidget()
                value_layout = QHBoxLayout(value_widget)
                value_layout.setContentsMargins(0, 0, 0, 0)
                value_layout.setSpacing(6)

                self.world_icon_label = QLabel()
                self.world_icon_label.setFixedSize(WORLD_ICON_SIZE, WORLD_ICON_SIZE)
                self.world_icon_label.setVisible(False)

                world_label = QLabel(default)
                world_label.setObjectName("summaryValue")
                world_label.setMinimumWidth(92)

                value_layout.addWidget(self.world_icon_label)
                value_layout.addWidget(world_label)
                value_layout.addStretch(1)
                self.summary_labels[key] = world_label
            else:
                value_widget = QLabel(default)
                value_widget.setObjectName("summaryValue")
                value_widget.setMinimumWidth(116)
                self.summary_labels[key] = value_widget

            info_grid.addWidget(value_widget, 1, index)
            info_grid.setColumnStretch(index, 1)

        layout.addWidget(self.character_image)
        layout.addLayout(info_grid, 1)
        return panel

    def _build_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_symbol_tab(), "심볼 현황")
        self.tabs.addTab(self._build_optimizer_tab(), "최적화")
        return self.tabs

    def _build_optimizer_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 18, 14, 8)
        layout.setSpacing(14)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 14)
        controls.setSpacing(12)
        self.mode_combo = QComboBox()
        self.mode_combo.addItem(MODE_LABELS["arcane"], "arcane")
        self.mode_combo.addItem(MODE_LABELS["authentic"], "authentic")
        self.mode_combo.currentIndexChanged.connect(self.refresh_mode_view)

        self.current_force_input = QLineEdit()
        self.current_force_input.setReadOnly(True)
        self.current_force_input.setText("0")
        self.current_force_input.setObjectName("readonlyInput")

        self.target_force_input = QLineEdit()
        self.target_force_input.setPlaceholderText("목표 포스")
        self.target_force_input.returnPressed.connect(self.calculate_optimization)

        self.calculate_button = QPushButton("계산")
        self.calculate_button.setObjectName("primaryButton")
        self.calculate_button.clicked.connect(self.calculate_optimization)

        controls.addWidget(QLabel("계산 대상"))
        controls.addWidget(self.mode_combo)
        controls.addWidget(QLabel("현재 포스"))
        controls.addWidget(self.current_force_input)
        controls.addWidget(QLabel("목표 포스"))
        controls.addWidget(self.target_force_input)
        controls.addStretch(1)
        controls.addWidget(self.calculate_button)

        self.result_table = QTableWidget(0, 4)
        self.result_table.setHorizontalHeaderLabels(["순위", "증가 포스", "추천 경로", "총 비용"])
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.result_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.result_table.setColumnWidth(0, 72)
        self.result_table.setColumnWidth(1, 104)
        self.result_table.setColumnWidth(3, 142)
        self.result_table.verticalHeader().setDefaultSectionSize(36)
        self.result_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result_table.setMinimumHeight(420)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)

        layout.addLayout(controls)
        layout.addWidget(self.result_table, 1)
        return page

    def _build_symbol_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 18, 14, 8)
        layout.setSpacing(14)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 12)
        controls.setSpacing(12)
        self.symbol_mode_combo = QComboBox()
        self.symbol_mode_combo.addItem(MODE_LABELS["arcane"], "arcane")
        self.symbol_mode_combo.addItem(MODE_LABELS["authentic"], "authentic")
        self.symbol_mode_combo.currentIndexChanged.connect(self._populate_symbol_table)
        controls.addWidget(QLabel("조회 대상"))
        controls.addWidget(self.symbol_mode_combo)
        controls.addStretch(1)

        self.symbol_table = QTableWidget(0, 5)
        self.symbol_table.setHorizontalHeaderLabels(["지역", "요구 레벨", "현재 레벨", "현재 포스", "최대 포스"])
        self.symbol_table.verticalHeader().setVisible(False)
        self.symbol_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.symbol_table.verticalHeader().setDefaultSectionSize(36)
        self.symbol_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.symbol_table.setMinimumHeight(380)
        self.symbol_table.setAlternatingRowColors(True)

        layout.addLayout(controls)
        layout.addWidget(self.symbol_table)
        return page

    def _build_status_bar(self):
        row = QHBoxLayout()
        self.status_label = QLabel("캐릭터명을 입력하고 조회를 누르세요.")
        self.status_label.setObjectName("statusLabel")
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.progress.setFixedWidth(180)
        row.addWidget(self.status_label, 1)
        row.addWidget(self.progress)
        return row

    def load_character(self):
        character_name = self.character_input.text().strip()
        if not character_name:
            QMessageBox.warning(self, "입력 필요", "캐릭터명을 입력해주세요.")
            return

        self._set_loading(True, "최신 캐릭터/심볼 데이터를 조회하는 중입니다.")
        self.worker = CharacterLoadWorker(character_name)
        self.worker.loaded.connect(self._on_character_loaded)
        self.worker.failed.connect(self._on_load_failed)
        self.worker.finished.connect(lambda: self._set_loading(False))
        self.worker.start()

    def _on_character_loaded(self, character_info, symbol_info, image_bytes):
        self.character_info = character_info
        self.symbol_info = symbol_info
        self.current_symbols = self._parse_current_symbols(symbol_info)
        self._update_character_summary(image_bytes)
        self._reset_after_character_load()
        self.status_label.setText("최신 데이터 조회가 완료되었습니다.")

    def _on_load_failed(self, message):
        QMessageBox.critical(self, "조회 실패", message)
        self.status_label.setText("조회에 실패했습니다.")

    def _set_loading(self, is_loading, message=None):
        self.progress.setVisible(is_loading)
        self.load_button.setEnabled(not is_loading)
        self.calculate_button.setEnabled(not is_loading)
        if message:
            self.status_label.setText(message)

    def _parse_current_symbols(self, symbol_info):
        parsed = {}
        for symbol in symbol_info.get("symbol", []):
            area_key = get_area_key_from_symbol_name(symbol.get("symbol_name", ""))
            if not area_key:
                continue
            parsed[area_key] = {
                "level": int(symbol.get("symbol_level") or 0),
                "force": int(symbol.get("symbol_force") or 0),
                "name": symbol.get("symbol_name", ""),
            }
        return parsed

    def _update_character_summary(self, image_bytes):
        info = self.character_info
        values = {
            "character_name": info.get("character_name", "-"),
            "world_name": info.get("world_name", "-"),
            "character_guild_name": info.get("character_guild_name") or "길드 없음",
            "character_class": info.get("character_class", "-"),
            "character_level": self._format_level_text(info),
        }
        for key, value in values.items():
            self.summary_labels[key].setText(value)
        self._update_world_icon(values["world_name"])

        pixmap = QPixmap()
        if image_bytes and pixmap.loadFromData(image_bytes):
            cropped = pixmap.copy(105, 115, 90, 90) if pixmap.width() >= 195 and pixmap.height() >= 205 else pixmap
            self.character_image.setPixmap(cropped.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.character_image.setText("No Image")
            self.character_image.setPixmap(QPixmap())

    def _update_world_icon(self, world_name):
        icon_key = self._world_icon_key(world_name)
        icon_path = self._find_icon_path(WORLD_ICON_DIR, icon_key)
        if not icon_path:
            self.world_icon_label.setVisible(False)
            self.world_icon_label.setPixmap(QPixmap())
            return

        pixmap = QPixmap(str(icon_path))
        if pixmap.isNull():
            self.world_icon_label.setVisible(False)
            self.world_icon_label.setPixmap(QPixmap())
            return

        self.world_icon_label.setPixmap(pixmap.scaled(
            WORLD_ICON_SIZE,
            WORLD_ICON_SIZE,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        ))
        self.world_icon_label.setVisible(True)

    def _world_icon_key(self, world_name):
        if not world_name:
            return None
        if world_name.startswith("챌린저스"):
            return "challengers"
        return WORLD_ICON_KEYS.get(world_name)

    def _find_icon_path(self, directory, icon_key):
        if not icon_key:
            return None
        for extension in (".webp", ".png"):
            path = directory / f"{icon_key}{extension}"
            if path.exists():
                return path
        return None

    def _format_level_text(self, info):
        level = info.get("character_level", "-")
        exp_rate = info.get("character_exp_rate")
        if exp_rate is None:
            return f"Lv. {level}"
        return f"Lv. {level} ({exp_rate}%)"

    def refresh_mode_view(self):
        self.target_force_input.clear()
        self._update_current_force_label()
        self._populate_symbol_table()
        self.result_table.setRowCount(0)

    def _reset_after_character_load(self):
        self.mode_combo.blockSignals(True)
        self.symbol_mode_combo.blockSignals(True)
        self.mode_combo.setCurrentIndex(0)
        self.symbol_mode_combo.setCurrentIndex(0)
        self.mode_combo.blockSignals(False)
        self.symbol_mode_combo.blockSignals(False)

        self.target_force_input.clear()
        self.result_table.setRowCount(0)
        self._update_current_force_label()
        self._populate_symbol_table()
        self.tabs.setCurrentIndex(0)

    def _update_current_force_label(self):
        self.current_force_input.setText(str(self._current_force_for_mode(self._current_mode())))

    def _current_mode(self):
        return self.mode_combo.currentData()

    def _character_level(self):
        return int(self.character_info.get("character_level") or 0)

    def _current_force_for_mode(self, mode):
        character_level = self._character_level()
        if character_level:
            area_keys = set(get_accessible_areas(character_level, mode))
        else:
            area_keys = {area.key for area in get_areas_for_mode(mode)}
        return sum(
            int(symbol.get("force") or 0)
            for key, symbol in self.current_symbols.items()
            if key in area_keys
        )

    def _populate_symbol_table(self):
        mode = self.symbol_mode_combo.currentData()
        character_level = self._character_level()
        if character_level:
            accessible_area_keys = set(get_accessible_areas(character_level, mode))
            areas = [area for area in get_areas_for_mode(mode) if area.key in accessible_area_keys]
        else:
            areas = get_areas_for_mode(mode)
        self.symbol_table.setRowCount(len(areas) + 1)
        total_current_force = 0
        total_max_force = 0

        for row, area in enumerate(areas):
            current = self.current_symbols.get(area.key, {})
            current_force = int(current.get("force", 0) or 0)
            total_current_force += current_force
            total_max_force += area.max_force
            values = [
                area.name,
                str(area.required_level),
                str(current.get("level", 0)),
                str(current_force),
                str(area.max_force),
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem("" if col == 0 else value)
                if col != 0:
                    item.setTextAlignment(Qt.AlignCenter)
                self.symbol_table.setItem(row, col, item)
            self.symbol_table.setCellWidget(row, 0, self._symbol_name_widget(area.key, area.name))

        total_row = len(areas)
        total_values = ["합계", "-", "-", str(total_current_force), str(total_max_force)]
        for col, value in enumerate(total_values):
            item = QTableWidgetItem("" if col == 0 else value)
            if col != 0:
                item.setTextAlignment(Qt.AlignCenter)
            item.setBackground(QColor("#1f3f34"))
            self.symbol_table.setItem(total_row, col, item)
        total_icon_key = "select_arcane" if mode == "arcane" else "select_authentic"
        self.symbol_table.setCellWidget(total_row, 0, self._symbol_name_widget(total_icon_key, "합계", is_total=True))

    def _symbol_name_widget(self, icon_key, text, is_total=False):
        widget = QWidget()
        if is_total:
            widget.setObjectName("totalNameCell")

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(8)

        icon_label = QLabel()
        icon_label.setFixedSize(SYMBOL_ICON_SIZE, SYMBOL_ICON_SIZE)
        icon_path = self._find_icon_path(SYMBOL_ICON_DIR, icon_key)
        pixmap = QPixmap(str(icon_path)) if icon_path else QPixmap()
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(
                SYMBOL_ICON_SIZE,
                SYMBOL_ICON_SIZE,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            ))

        text_label = QLabel(text)
        text_label.setObjectName("symbolTotalText" if is_total else "symbolNameText")

        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch(1)
        return widget

    def _route_widget(self, steps, is_best=False):
        widget = QWidget()
        widget.setObjectName("bestRouteCell" if is_best else "routeCell")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(5)

        sorted_steps = sorted(steps, key=lambda step: AREA_ORDER.index(step.area))
        if not sorted_steps:
            empty_label = QLabel("-")
            empty_label.setObjectName("routeText")
            layout.addWidget(empty_label)
            layout.addStretch(1)
            return widget

        for index, step in enumerate(sorted_steps):
            if index:
                comma_label = QLabel(",")
                comma_label.setObjectName("routeText")
                layout.addWidget(comma_label)

            icon_label = QLabel()
            icon_label.setFixedSize(ROUTE_ICON_SIZE, ROUTE_ICON_SIZE)
            icon_path = self._find_icon_path(SYMBOL_ICON_DIR, step.area)
            pixmap = QPixmap(str(icon_path)) if icon_path else QPixmap()
            if not pixmap.isNull():
                icon_label.setPixmap(pixmap.scaled(
                    ROUTE_ICON_SIZE,
                    ROUTE_ICON_SIZE,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                ))

            text_label = QLabel(f"{KEY_TO_NAME_MAP[step.area]} {step.current_level}->{step.target_level}")
            text_label.setObjectName("routeText")
            layout.addWidget(icon_label)
            layout.addWidget(text_label)

        layout.addStretch(1)
        return widget

    def calculate_optimization(self):
        if not self.character_info or not self.symbol_info:
            QMessageBox.warning(self, "조회 필요", "먼저 캐릭터 정보를 조회해주세요.")
            return

        try:
            target_force = int(self.target_force_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "입력 오류", "목표 포스는 숫자로 입력해주세요.")
            return

        mode = self._current_mode()
        character_level = self._character_level()
        accessible_areas = get_accessible_areas(character_level, mode)
        current_force = self._current_force_for_mode(mode)
        max_force = sum(SYMBOL_AREAS[area_key].max_force for area_key in accessible_areas)

        if target_force <= current_force:
            QMessageBox.information(self, "계산 불필요", "이미 목표 포스에 도달했습니다.")
            return
        if target_force > max_force:
            QMessageBox.warning(self, "목표 초과", f"현재 레벨 기준 최대 포스는 {max_force}입니다.")
            return

        needed_force = target_force - current_force
        results = find_best_solutions(self.current_symbols, accessible_areas, needed_force)
        self._populate_results(results, current_force, target_force)

    def _populate_results(self, results, current_force, target_force):
        self.result_table.setRowCount(len(results))

        for row, result in enumerate(results):
            values = [
                str(row + 1),
                f"+{result.added_force}",
                "",
                f"{result.total_cost:,}",
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col != 2:
                    item.setTextAlignment(Qt.AlignCenter)
                if row == 0:
                    item.setBackground(QColor("#1f3f34"))
                self.result_table.setItem(row, col, item)
            self.result_table.setCellWidget(row, 2, self._route_widget(result.steps, row == 0))

        self.status_label.setText(f"최소 비용 경로 {len(results)}개를 계산했습니다.")

    def _apply_style(self):
        QApplication.instance().setFont(QFont("Malgun Gothic", 10))
        self.setStyleSheet(
            """
            #root { background: #111418; color: #e8edf2; }
            QLabel { color: #e8edf2; }
            #title { font-size: 28px; font-weight: 700; }
            #subtitle, #statusLabel, #summaryLabel, #fieldLabel { color: #9aa7b4; }
            #fieldLabel { font-weight: 600; }
            #summaryValue { color: #ffffff; font-size: 16px; font-weight: 700; }
            #symbolNameText {
                color: #e8edf2;
                font-weight: 600;
            }
            QWidget {
                background: transparent;
            }
            #symbolTotalText {
                color: #ffffff;
                font-weight: 700;
            }
            #totalNameCell {
                background: #1f3f34;
            }
            #routeText {
                color: #e8edf2;
                font-weight: 600;
            }
            #bestRouteCell {
                background: #1f3f34;
            }
            QLineEdit#readonlyInput {
                color: #b8c3cf;
                background: #131820;
            }
            #panel {
                background: #1a2027;
                border: 1px solid #2a3440;
                border-radius: 8px;
            }
            #characterImage {
                background: #111820;
                border: 1px solid #2a3440;
                border-radius: 8px;
                color: #65717e;
            }
            QLineEdit, QComboBox {
                background: #171d24;
                color: #edf3f8;
                border: 1px solid #2c3845;
                border-radius: 6px;
                padding: 8px 10px;
                min-width: 160px;
            }
            QComboBox { min-width: 190px; }
            QLineEdit { min-width: 170px; }
            QPushButton {
                background: #26313d;
                color: #edf3f8;
                border: 1px solid #3a4654;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton#primaryButton {
                background: #2f7d5d;
                border-color: #3e9b75;
            }
            QPushButton:disabled { color: #65717e; background: #1d252d; }
            QTabWidget::pane {
                border: 1px solid #2a3440;
                border-radius: 0px;
                background: #151a20;
                top: -1px;
            }
            QTabBar::tab {
                background: #202832;
                color: #aab6c2;
                padding: 10px 28px;
                border: 1px solid #2a3440;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 3px;
            }
            QTabBar::tab:selected {
                background: #2f7d5d;
                color: #ffffff;
                border-color: #2f7d5d;
            }
            QTableWidget {
                background: #151a20;
                alternate-background-color: #1a2027;
                color: #e8edf2;
                gridline-color: #2a3440;
                border: none;
            }
            QHeaderView::section {
                background: #202832;
                color: #d8e0e8;
                border: none;
                border-right: 1px solid #2a3440;
                padding: 8px;
                font-weight: 700;
            }
            QProgressBar {
                border: 1px solid #2a3440;
                border-radius: 5px;
                background: #151a20;
                height: 10px;
            }
            QProgressBar::chunk { background: #2f7d5d; border-radius: 4px; }
            """
        )


def run_app():
    app = QApplication(sys.argv)
    if APP_ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(APP_ICON_PATH)))
    window = MapleSymbolOptimizer()
    window.show()
    sys.exit(app.exec())
