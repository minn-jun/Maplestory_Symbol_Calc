import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from PIL import ImageTk

import symbol_data as sd
from api_handler import NexonAPI
from optimizer import find_best_solutions
from utils import fetch_and_crop_character_image

class MapleSymbolOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("메이플스토리 심볼 최적화 프로그램")
        self.root.geometry("1000x800")
        
        # 변수 설정
        self.api_key = tk.StringVar()
        self.character_name = tk.StringVar()
        self.target_force = tk.IntVar()
        self.symbol_type = tk.StringVar(value="arcane")
        
        # 데이터 및 상태 저장
        self.character_info = {}
        self.symbol_info = {}
        self.current_force = 0
        self.api_handler = None
        
        self.setup_gui()
        
    def setup_gui(self):
        """애플리케이션의 전체 GUI를 구성합니다."""
        outer_frame = ttk.Frame(self.root)
        outer_frame.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        canvas = tk.Canvas(outer_frame)
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        outer_frame.rowconfigure(0, weight=1)
        outer_frame.columnconfigure(0, weight=1)

        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        scrollable_frame.columnconfigure(0, weight=1)

        window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_canvas_resize(event):
            canvas.itemconfig(window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_resize)

        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(1, weight=1)

        # --- 입력 섹션 ---
        ttk.Label(main_frame, text="API 키:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(main_frame, textvariable=self.api_key, width=50, show="*").grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        ttk.Label(main_frame, text="캐릭터명:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(main_frame, textvariable=self.character_name, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(main_frame, text="캐릭터 로드", command=self.load_character).grid(row=1, column=2, padx=(10, 0), pady=2)

        # --- 캐릭터 정보 섹션 ---
        info_frame = ttk.LabelFrame(main_frame, text="캐릭터 정보", padding="10")
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        char_info_frame = ttk.Frame(info_frame)
        char_info_frame.pack(fill=tk.BOTH, expand=True)
        self.image_label = ttk.Label(char_info_frame)
        self.image_label.pack(side=tk.LEFT, padx=(0, 10))
        self.info_text = scrolledtext.ScrolledText(char_info_frame, height=8, width=60, state='disabled')
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- 심볼 정보 섹션 ---
        symbol_frame = ttk.LabelFrame(main_frame, text="심볼 타입 선택", padding="10")
        symbol_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        ttk.Radiobutton(symbol_frame, text="아케인 심볼", variable=self.symbol_type, value="arcane").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(symbol_frame, text="어센틱 심볼", variable=self.symbol_type, value="authentic").pack(side=tk.LEFT, padx=10)
        ttk.Button(symbol_frame, text="심볼 정보 로드", command=self.load_symbols).pack(side=tk.LEFT, padx=20)
        self.symbol_text = scrolledtext.ScrolledText(main_frame, height=8, width=80, state='disabled')
        self.symbol_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # --- 목표 설정 섹션 ---
        target_frame = ttk.LabelFrame(main_frame, text="목표 설정", padding="10")
        target_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(target_frame, text="목표 포스:").pack(side=tk.LEFT)
        self.target_force_entry = ttk.Entry(target_frame, textvariable=self.target_force, width=10)
        self.target_force_entry.pack(side=tk.LEFT, padx=10)
        ttk.Button(target_frame, text="최적화 계산", command=self.calculate_optimization).pack(side=tk.LEFT, padx=20)

        # --- 결과 출력 섹션 ---
        result_frame = ttk.LabelFrame(main_frame, text="최적화 결과", padding="10")
        result_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, width=80, state='disabled')
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # --- 진행 바 ---
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

    def _update_text_widget(self, widget, content):
        """ScrolledText 위젯의 내용을 업데이트합니다."""
        widget.config(state='normal')
        widget.delete(1.0, tk.END)
        widget.insert(1.0, content)
        widget.config(state='disabled')

    def load_character(self):
        """캐릭터 정보 로드를 시작합니다."""
        if not self.api_key.get() or not self.character_name.get():
            messagebox.showerror("오류", "API 키와 캐릭터명을 입력해주세요.")
            return

        # 이전 심볼 정보 초기화
        self._update_text_widget(self.symbol_text, "")
        self.symbol_info = {}
        
        # 이전 최적화 결과창 초기화
        self._update_text_widget(self.result_text, "")
        
        # 목표 포스 입력창 초기화
        self.target_force.set("")
        
        # 심볼 타입 기본값으로 설정
        self.symbol_type.set("arcane")
        
        self.api_handler = NexonAPI(self.api_key.get())
        threading.Thread(target=self._load_character_thread, daemon=True).start()

    def _load_character_thread(self):
        """백그라운드에서 캐릭터 정보를 로드합니다."""
        try:
            self.progress.start()
            char_name = self.character_name.get()
            
            # API를 통해 기본 정보 및 이미지 URL 가져오기
            self.character_info = self.api_handler.get_character_info(char_name)
            
            # 이미지 로드 및 크롭
            image_url = self.character_info.get('character_image')
            self.character_image = fetch_and_crop_character_image(image_url) if image_url else None
            
            self.root.after(0, self.update_character_info_gui)
        except Exception as e:
            # [FIXED] 람다에 e=e를 추가하여 예외 객체를 캡처합니다.
            self.root.after(0, lambda e=e: messagebox.showerror("오류", f"캐릭터 로드 실패: {e}"))
        finally:
            self.root.after(0, self.progress.stop)
            
    def update_character_info_gui(self):
        """가져온 캐릭터 정보로 GUI를 업데이트합니다."""
        if self.character_image:
            self.image_label.configure(image=self.character_image)
        else:
            self.image_label.configure(text="이미지 없음", image="")
        
        info = self.character_info
        text = (
            f"캐릭터명: {info.get('character_name', 'N/A')}\n"
            f"월드명: {info.get('world_name', 'N/A')}\n"
            f"클래스: {info.get('character_class', 'N/A')}\n"
            f"레벨: {info.get('character_level', 'N/A')}\n"
            f"길드명: {info.get('character_guild_name') or '길드 없음'}\n"
            f"전직: {info.get('character_class_level', 'N/A')}차 전직 완료\n"
            f"경험치: {info.get('character_exp_rate', 'N/A')}%"
        )
        self._update_text_widget(self.info_text, text)

    def load_symbols(self):
        """심볼 정보 로드를 시작합니다."""
        if not self.character_info:
            messagebox.showerror("오류", "먼저 캐릭터를 로드해주세요.")
            return
        threading.Thread(target=self._load_symbols_thread, daemon=True).start()
        
    def _load_symbols_thread(self):
        """백그라운드에서 심볼 정보를 로드합니다."""
        try:
            self.progress.start()
            self.symbol_info = self.api_handler.get_symbol_info(self.character_name.get())
            self.root.after(0, self.update_symbol_info_gui)
        except Exception as e:
            # [FIXED] 람다에 e=e를 추가하여 예외 객체를 캡처합니다.
            self.root.after(0, lambda e=e: messagebox.showerror("오류", f"심볼 로드 실패: {e}"))
        finally:
            self.root.after(0, self.progress.stop)

    def update_symbol_info_gui(self):
        """가져온 심볼 정보로 GUI를 업데이트합니다."""
        symbol_text = ""
        total_force = 0
        
        is_arcane = self.symbol_type.get() == "arcane"
        symbol_title = "아케인" if is_arcane else "어센틱"
        symbol_names_map = sd.ARCANE_SYMBOLS_NAMES if is_arcane else sd.AUTHENTIC_SYMBOLS_NAMES

        symbol_text += f"=== {symbol_title} 심볼 정보 ===\n\n"
        
        if self.symbol_info and 'symbol' in self.symbol_info:
            for symbol in self.symbol_info['symbol']:
                s_name = symbol.get('symbol_name', '')
                if any(key in s_name for key in symbol_names_map):
                    symbol_text += f"{s_name}: Lv.{symbol['symbol_level']} (포스 +{symbol['symbol_force']})\n"
                    total_force += int(symbol['symbol_force'])
            
            self.current_force = total_force
            symbol_text += f"\n{symbol_title} 포스 : {total_force}\n"
        else:
            symbol_text += "심볼 정보를 찾을 수 없습니다.\n"
        
        self._update_text_widget(self.symbol_text, symbol_text)

    def calculate_optimization(self):
        """최적화 계산을 시작하기 전 유효성을 검사합니다."""
        if not self.symbol_info:
            messagebox.showerror("오류", "심볼 정보를 로드해주세요.")
            return

        target_force_str = self.target_force_entry.get()
        if not target_force_str:
            messagebox.showerror("오류", "목표 포스를 입력해주세요.")
            return
        
        try:
            target_force_val = int(target_force_str)
            self.target_force.set(target_force_val)
        except ValueError:
            messagebox.showerror("오류", "목표 포스는 숫자로 입력해주세요.")
            return
            
        threading.Thread(target=self._calculate_optimization_thread, daemon=True).start()

    def _calculate_optimization_thread(self):
        """백그라운드에서 최적화 계산을 수행합니다."""
        try:
            self.progress.start()
            
            is_arcane = self.symbol_type.get() == "arcane"
            character_level = self.character_info.get('character_level', 200)
            
            accessible_areas = self._get_accessible_areas(character_level)
            
            # 현재 심볼 정보 파싱
            current_symbols = {}
            symbol_set = sd.ARCANE_SYMBOLS_SET if is_arcane else sd.AUTHENTIC_SYMBOLS_SET
            
            for symbol in self.symbol_info.get('symbol', []):
                s_name = symbol['symbol_name'].replace("아케인심볼 : ", "").replace("어센틱심볼 : ", "")
                if s_name in symbol_set:
                    area_key = sd.NAME_TO_KEY_MAP.get(s_name)
                    if area_key in accessible_areas:
                        current_symbols[area_key] = {
                            "level": symbol['symbol_level'],
                            "force": symbol['symbol_force']
                        }
            
            target_force = self.target_force.get()

            if self.current_force >= target_force:
                self.root.after(0, lambda: messagebox.showinfo("알림", "이미 목표 포스에 도달했습니다!"))
                return
            
            max_force = len(accessible_areas) * (220 if is_arcane else 110)
            if target_force > max_force:
                self.root.after(0, lambda: messagebox.showwarning("경고", f"목표 포스가 최댓값({max_force})을 초과했습니다."))
                return

            needed_force = target_force - self.current_force
            
            if (target_force != max_force) and needed_force > 200:
                proceed = messagebox.askyesno(
                    "계산량 경고",
                    f"필요 포스가 {needed_force}로 매우 큽니다.\n"
                    f"계산량이 많아 정확한 값이 안나올 수 있습니다.\n\n"
                    f"실행하시겠습니까?\n(권장: 목표 포스를 단계별로 나누어 계산)"
                )
                if not proceed: return
            
            # 최적화 알고리즘 실행
            best_solutions = find_best_solutions(current_symbols, accessible_areas, needed_force, is_arcane)
            
            # 결과 포맷팅 및 GUI 업데이트
            result_text = self._format_results(best_solutions, self.current_force, target_force, is_arcane)
            self.root.after(0, lambda: self._update_text_widget(self.result_text, result_text))
            
        except Exception as e:
            self.root.after(0, lambda e=e: messagebox.showerror("오류", f"계산 실패: {e}"))
        finally:
            self.root.after(0, self.progress.stop)

    def _get_accessible_areas(self, character_level):
        """캐릭터 레벨에 따라 접근 가능한 지역 목록을 반환합니다."""
        accessible = []
        level_reqs = sd.ARCANE_LEVEL_REQS if self.symbol_type.get() == "arcane" else sd.AUTHENTIC_LEVEL_REQS
        
        for level, area in level_reqs.items():
            if character_level >= level:
                accessible.append(area)
        return accessible

    def _format_results(self, solutions, current_force, target_force, is_arcane):
        """계산 결과를 사용자가 보기 쉬운 문자열로 변환합니다."""
        if not solutions:
            return "오류: 목표 포스에 도달할 수 있는 조합이 없습니다."
        
        num_results = len(solutions)
        result = (
            f"현재 포스: {current_force}\n"
            f"목표 포스: {target_force}\n"
            f"필요 포스: {target_force - current_force}\n\n"
            f"=== 최적화 결과 (비용 기준 오름차순 상위 {num_results}개) ===\n\n"
        )
        
        sort_order = sd.ARCANE_SORT_ORDER if is_arcane else sd.AUTHENTIC_SORT_ORDER
        
        for i, (upgrade_plan, total_cost, added_force) in enumerate(solutions, 1):
            result += f"[방법 {i}] 총 비용: {total_cost:,} 메소, 추가 포스: +{added_force}\n"

            sorted_plan_items = sorted(upgrade_plan.items(), key=lambda item: sort_order.index(item[0]))
            
            for area, (current, target, cost) in sorted_plan_items:
                area_name = sd.KEY_TO_NAME_MAP.get(area, area)
                result += f"  {area_name}: Lv.{current} → Lv.{target} (비용: {cost:,} 메소)\n"
            result += "\n"
        
        return result