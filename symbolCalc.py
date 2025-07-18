'''
202135905 고민준
메이플스토리 심볼 최적화 프로그램

README.md 읽어주세요..

실행 환경 : VS Code
활용 데이터 : https://openapi.nexon.com/ko/ Nexon Open API
'''

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from datetime import datetime, timedelta
import threading
import heapq
from PIL import Image, ImageTk
import io

class MapleSymbolOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("메이플스토리 심볼 최적화 프로그램")
        self.root.geometry("1000x800")
        
        # 심볼 데이터
        self.setup_symbol_data()
        
        # GUI 구성 요소
        self.api_key = tk.StringVar()
        self.character_name = tk.StringVar()
        self.target_force = tk.IntVar()
        self.symbol_type = tk.StringVar(value="arcane")
        
        # 캐릭터 정보 저장
        self.character_info = {}
        self.symbol_info = {}
        self.current_force = 0
        
        self.setup_gui()
        

    ## 심볼 데이터 초기화 - Dictionary 자료구조 사용
    '''
    Dictionary

      개발단계에서 가장 많이 사용한 자료구조
      Key-Value 형태로 데이터 저장
      검색 추가 삭제를 평균 O(1)의 시간 복잡도로 처리 가능
    '''
    def setup_symbol_data(self):
        # 아케인 심볼 데이터
        self.arcane_symbols = {
            'vanishing_journey': {2: 97, 3: 123, 4: 166, 5: 226, 6: 306, 7: 404, 8: 522, 9: 660, 10: 818, 11: 999, 12: 1201, 13: 1426, 14: 1674, 15: 1945, 16: 2242, 17: 2563, 18: 2910, 19: 3283, 20: 3682},
            'chu_chu_island': {2: 121, 3: 153, 4: 206, 5: 280, 6: 378, 7: 498, 8: 642, 9: 810, 10: 1002, 11: 1221, 12: 1465, 13: 1736, 14: 2034, 15: 2359, 16: 2714, 17: 3097, 18: 3510, 19: 3953, 20: 4426},
            'lachelein': {2: 145, 3: 183, 4: 246, 5: 334, 6: 450, 7: 592, 8: 762, 9: 960, 10: 1186, 11: 1443, 12: 1729, 13: 2046, 14: 2394, 15: 2773, 16: 3186, 17: 3631, 18: 4110, 19: 4623, 20: 5170},
            'arcana': {2: 169, 3: 213, 4: 286, 5: 388, 6: 522, 7: 686, 8: 882, 9: 1110, 10: 1370, 11: 1665, 12: 1993, 13: 2356, 14: 2754, 15: 3187, 16: 3658, 17: 4165, 18: 4710, 19: 5293, 20: 5914},
            'morass': {2: 193, 3: 243, 4: 326, 5: 442, 6: 594, 7: 780, 8: 1002, 9: 1260, 10: 1554, 11: 1887, 12: 2257, 13: 2666, 14: 3114, 15: 3601, 16: 4130, 17: 4699, 18: 5310, 19: 5963, 20: 6658},
            'esfera': {2: 217, 3: 273, 4: 366, 5: 496, 6: 666, 7: 874, 8: 1122, 9: 1410, 10: 1738, 11: 2109, 12: 2521, 13: 2976, 14: 3474, 15: 4015, 16: 4602, 17: 5233, 18: 5910, 19: 6633, 20: 7402}
        }
        
        # 어센틱 심볼 데이터
        self.authentic_symbols = {
            'cernium': {2: 3650, 3: 9120, 4: 16070, 5: 24190, 6: 33150, 7: 42620, 8: 52290, 9: 61820, 10: 70900, 11: 79200},
            'arcus_island': {2: 4170, 3: 10480, 4: 18610, 5: 28220, 6: 39000, 7: 50610, 8: 62740, 9: 75070, 10: 87260, 11: 99000},
            'odium': {2: 4690, 3: 11850, 4: 21150, 5: 32250, 6: 44850, 7: 58600, 8: 73200, 9: 88320, 10: 103620, 11: 118800},
            'shangri_la': {2: 5220, 3: 13220, 4: 23680, 5: 36280, 6: 50700, 7: 66600, 8: 83660, 9: 101560, 10: 119980, 11: 138600},
            'arteria': {2: 5740, 3: 14590, 4: 26220, 5: 40320, 6: 56550, 7: 74590, 8: 94120, 9: 114810, 10: 136350, 11: 158400},
            'carcion': {2: 6260, 3: 15960, 4: 28760, 5: 44350, 6: 62400, 7: 82580, 8: 104580, 9: 128060, 10: 152710, 11: 178200},
            'tallahart': {2: 11360, 3: 29330, 4: 53580, 5: 83770, 6: 119600, 7: 160720, 8: 206830, 9: 257600, 10: 312690, 11: 371800}
        }
        
        # 레벨별 접근 가능 지역 매핑
        self.level_access = {
            200: 'vanishing_journey',
            210: 'chu_chu_island',
            220: 'lachelein',
            225: 'arcana',
            230: 'morass',
            235: 'esfera',
            260: 'cernium',
            265: 'arcus_island',
            270: 'odium',
            275: 'shangri_la',
            280: 'arteria',
            285: 'carcion',
            290: 'tallahart'
        }
    

    ## 전체 GUI 구성
    def setup_gui(self):
        
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
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        scrollable_frame.columnconfigure(0, weight=1)

        window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_canvas_resize(event):
            canvas.itemconfig(window, width=event.width)

        canvas.bind("<Configure>", _on_canvas_resize)

        # 메인 프레임
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(1, weight=1)

        # API 키 입력
        ttk.Label(main_frame, text="API 키:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(main_frame, textvariable=self.api_key, width=50, show="*").grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)

        # 캐릭터명 입력
        ttk.Label(main_frame, text="캐릭터명:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(main_frame, textvariable=self.character_name, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(main_frame, text="캐릭터 로드", command=self.load_character).grid(row=1, column=2, padx=(10, 0), pady=2)

        # 캐릭터 정보 출력
        info_frame = ttk.LabelFrame(main_frame, text="캐릭터 정보", padding="10")
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        char_info_frame = ttk.Frame(info_frame)
        char_info_frame.pack(fill=tk.BOTH, expand=True)

        self.image_label = ttk.Label(char_info_frame)
        self.image_label.pack(side=tk.LEFT, padx=(0, 10))

        self.info_text = scrolledtext.ScrolledText(char_info_frame, height=8, width=60)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 심볼 타입 선택
        symbol_frame = ttk.LabelFrame(main_frame, text="심볼 타입 선택", padding="10")
        symbol_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Radiobutton(symbol_frame, text="아케인 심볼", variable=self.symbol_type, value="arcane").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(symbol_frame, text="어센틱 심볼", variable=self.symbol_type, value="authentic").pack(side=tk.LEFT, padx=10)
        ttk.Button(symbol_frame, text="심볼 정보 로드", command=self.load_symbols).pack(side=tk.LEFT, padx=20)

        # 심볼 정보 표시
        self.symbol_text = scrolledtext.ScrolledText(main_frame, height=8, width=80)
        self.symbol_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # 목표 설정
        target_frame = ttk.LabelFrame(main_frame, text="목표 설정", padding="10")
        target_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(target_frame, text="목표 포스:").pack(side=tk.LEFT)
        ttk.Entry(target_frame, textvariable=self.target_force, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(target_frame, text="최적화 계산", command=self.calculate_optimization).pack(side=tk.LEFT, padx=20)

        # 최적화 결과 출력
        result_frame = ttk.LabelFrame(main_frame, text="최적화 결과", padding="10")
        result_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, width=80)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 진행 상황 프로그래스바
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)


    ## 캐릭터 정보 로드
    def load_character(self):
        if not self.api_key.get() or not self.character_name.get():
            messagebox.showerror("오류", "API 키와 캐릭터명을 입력해주세요.")
            return
        
        # thread 처리
        threading.Thread(target=self.load_character_thread).start()
    
    ## 캐릭터 정보 로드 thread
    def load_character_thread(self):
        try:
            self.progress.start()
            
            # 캐릭터 고유 OCID 조회
            ocid_url = f"https://open.api.nexon.com/maplestory/v1/id?character_name={self.character_name.get()}"
            headers = {"x-nxopen-api-key": self.api_key.get()}
            
            response = requests.get(ocid_url, headers=headers)

            if response.status_code != 200:
                raise Exception(f"API 호출 실패: {response.status_code} - {response.text}")
            
            ocid = response.json()["ocid"]
            
            # 어제 날짜로 캐릭터 정보 조회 (오늘 데이터는 아직 갱신되지 않을 수 있음)
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            # today = datetime.now().strftime("%Y-%m-%d")
            
            # 기본 정보 조회
            basic_url = f"https://open.api.nexon.com/maplestory/v1/character/basic?ocid={ocid}&date={yesterday}"
            basic_response = requests.get(basic_url, headers=headers)
            basic_info = basic_response.json()
            
            self.character_info = basic_info
            
            # 캐릭터 이미지 조회
            try:
                image_url = basic_info.get('character_image')
                if image_url:
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        image_data = Image.open(io.BytesIO(image_response.content))
                        # 이미지 크기 조정
                        image_data = image_data.resize((96, 96), Image.Resampling.LANCZOS)
                        self.character_image = ImageTk.PhotoImage(image_data)
                    else:
                        self.character_image = None
                else:
                    self.character_image = None

            except Exception as img_error:
                print(f"이미지 로드 오류: {img_error}")
                self.character_image = None
            
            # GUI 업데이트
            self.root.after(0, self.update_character_info)
            
        except Exception as e:
            self.root.after(0, lambda e=e: messagebox.showerror("오류", f"캐릭터 로드 실패: {str(e)}"))
        finally:
            self.root.after(0, self.progress.stop)
    
    ## 캐릭터 정보 GUI 업데이트
    def update_character_info(self):
        
        # 캐릭터 이미지 표시
        if hasattr(self, 'character_image') and self.character_image:
            self.image_label.configure(image=self.character_image)
        else:
            self.image_label.configure(text="이미지 없음", image="")
        
        # 캐릭터 정보 표시
        info = self.character_info
        text = f"""캐릭터명: {info.get('character_name', 'N/A')}
월드명: {info.get('world_name', 'N/A')}
클래스: {info.get('character_class', 'N/A')}
레벨: {info.get('character_level', 'N/A')}
길드명: {info.get('character_guild_name', 'N/A') or '길드 없음'}
전직: {info.get('character_class_level', 'N/A')}차 전직 완료
경험치: {info.get('character_exp_rate', 'N/A')}%"""
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text)
    

    ## 심볼 정보 로드
    def load_symbols(self):
        if not self.character_info:
            messagebox.showerror("오류", "먼저 캐릭터를 로드해주세요.")
            return
        
        # thread 처리
        threading.Thread(target=self.load_symbols_thread).start()
    
    ## 심볼 정보 로드 thread
    def load_symbols_thread(self):
        try:
            self.progress.start()
            
            # OCID와 날짜 설정
            ocid_url = f"https://open.api.nexon.com/maplestory/v1/id?character_name={self.character_name.get()}"
            headers = {"x-nxopen-api-key": self.api_key.get()}
            response = requests.get(ocid_url, headers=headers)
            ocid = response.json()["ocid"]
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            # today = datetime.now().strftime("%Y-%m-%d")

            # 심볼 정보 조회
            symbol_url = f"https://open.api.nexon.com/maplestory/v1/character/symbol-equipment?ocid={ocid}&date={yesterday}"
            symbol_response = requests.get(symbol_url, headers=headers)
            
            if symbol_response.status_code != 200:
                raise Exception(f"심볼 API 호출 실패: {symbol_response.status_code} - {symbol_response.text}")
            
            symbol_data = symbol_response.json()
            # print(f"심볼 API 응답: {json.dumps(symbol_data, indent=2, ensure_ascii=False)}")  # 디버깅용
            
            self.symbol_info = symbol_data
            
            # GUI 업데이트
            self.root.after(0, self.update_symbol_info)
            
        except Exception as e:
            self.root.after(0, lambda e=e: messagebox.showerror("오류", f"심볼 로드 실패: {str(e)}"))
        finally:
            self.root.after(0, self.progress.stop)
    
    ## 심볼 정보 GUI 업데이트
    def update_symbol_info(self):        
        # 아케인 심볼 이름 매핑
        arcane_symbol_names = {
            '소멸의 여로': 'vanishing_journey',
            'VanishingJourney': 'vanishing_journey',
            '츄츄 아일랜드': 'chu_chu_island', 
            'ChuChuIsland': 'chu_chu_island',
            '레헬른': 'lachelein',
            'Lachelein': 'lachelein',
            '아르카나': 'arcana',
            'Arcana': 'arcana',
            '모라스': 'morass',
            'Morass': 'morass',
            '에스페라': 'esfera',
            'Esfera': 'esfera'
        }
        
        # 어센틱 심볼 이름 매핑
        authentic_symbol_names = {
            '세르니움': 'cernium',
            'Cernium': 'cernium',
            '아르크스': 'arcus_island',
            'Arcus': 'arcus_island',
            '오디움': 'odium',
            'Odium': 'odium',
            '도원경': 'shangri_la',
            'Shangri-La': 'shangri_la',
            '아르테리아': 'arteria',
            'Arteria': 'arteria',
            '카르시온': 'carcion',
            'Carcion': 'carcion',
            '탈라하트': 'tallahart',
            'Tallahart': 'tallahart'
        }
        
        symbol_text = ""
        total_force = 0

        if self.symbol_type.get() == "arcane":
            symbol_text = "=== 아케인 심볼 정보 ===\n\n"
            if self.symbol_info and 'symbol' in self.symbol_info:
                for symbol in self.symbol_info['symbol']:
                    symbol_name = symbol.get('symbol_name', '')
                    symbol_level = symbol.get('symbol_level', 0)
                    symbol_force = symbol.get('symbol_force', 0)
                    
                    # 아케인 심볼인지 확인
                    if symbol_name in arcane_symbol_names or any(key in symbol_name for key in arcane_symbol_names.keys()):
                        symbol_text += f"{symbol_name}: Lv.{symbol_level} (포스 +{symbol_force})\n"
                        total_force += int(symbol_force)

                self.current_force = total_force
                symbol_text += f"\n아케인 포스 : {total_force}\n"
            else:
                symbol_text += "심볼 정보를 찾을 수 없습니다.\n"
        else:
            symbol_text = "=== 어센틱 심볼 정보 ===\n\n"
            if self.symbol_info and 'symbol' in self.symbol_info:
                for symbol in self.symbol_info['symbol']:
                    symbol_name = symbol.get('symbol_name', '')
                    symbol_level = symbol.get('symbol_level', 0)
                    symbol_force = symbol.get('symbol_force', 0)
                    
                    # 어센틱 심볼인지 확인
                    if symbol_name in authentic_symbol_names or any(key in symbol_name for key in authentic_symbol_names.keys()):
                        symbol_text += f"{symbol_name}: Lv.{symbol_level} (포스 +{symbol_force})\n"
                        total_force += int(symbol_force)

                self.current_force = total_force
                symbol_text += f"\n어센틱 포스 : {total_force}\n"
            else:
                symbol_text += "심볼 정보를 찾을 수 없습니다.\n"
        
        self.symbol_text.delete(1.0, tk.END)
        self.symbol_text.insert(1.0, symbol_text)

        ### 디버깅
        print(self.symbol_info)
    

    ## DP + 백트래킹을 이용한 최적화 계산
    def calculate_optimization(self):
        if not self.symbol_info:
            messagebox.showerror("오류", "심볼 정보를 로드해주세요.")
            return
        
        value = self.target_force.get()
        if not value:
            messagebox.showerror("오류", "목표 포스를 입력해주세요.")
            return
        
        try:
            value = int(value)
        except ValueError:
            messagebox.showerror("오류", "목표 포스는 숫자로 입력해주세요.")
            return
        
        # thread 처리
        threading.Thread(target=self.calculate_optimization_thread).start()

    ## 최적화 계산 thread
    def calculate_optimization_thread(self):
        try:
            self.progress.start()
            
            # 현재 심볼 레벨과 포스 계산
            current_symbols = {}
            character_level = self.character_info.get('character_level', 200)
            current_force = self.current_force

            # 접근 가능한 지역 확인
            accessible_areas = self.get_accessible_areas(character_level)
            
            if self.symbol_type.get() == "arcane":
                symbol_data = self.arcane_symbols
                base_force = 30  # 1레벨 기본 포스
                force_per_level = 10
                max_level = 20
                
                for symbol in self.symbol_info.get('symbol', []):
                    symbol_name = symbol['symbol_name']
                    if symbol_name[8:] in ['소멸의 여로', '츄츄 아일랜드', '레헬른', '아르카나', '모라스', '에스페라']:
                        area_key = self.get_area_key(symbol_name[8:])
                        if area_key in accessible_areas:
                            symbol_level = symbol['symbol_level']
                            symbol_force = symbol['symbol_force']
                            current_symbols[area_key] = [symbol_level, symbol_force]
            else:
                symbol_data = self.authentic_symbols
                base_force = 10  # 1레벨 기본 포스
                force_per_level = 10
                max_level = 11
                
                for symbol in self.symbol_info.get('symbol', []):
                    symbol_name = symbol['symbol_name']
                    if symbol_name[8:] in ['세르니움', '아르크스', '오디움', '도원경', '아르테리아', '카르시온', '탈라하트']:
                        area_key = self.get_area_key(symbol_name[8:])
                        if area_key in accessible_areas:
                            symbol_level = symbol['symbol_level']
                            symbol_force = symbol['symbol_force']
                            current_symbols[area_key] = [symbol_level, symbol_force]
            
            target = self.target_force.get()

            if current_force >= target:
                messagebox.showinfo("알림", "이미 목표 포스에 도달했습니다!")
                return
            
            max_force = len(accessible_areas) * (220 if self.symbol_type.get() == "arcane" else 110)
            if target > max_force:
                messagebox.showwarning("경고", f"목표 포스가 최댓값({max_force})을 초과했습니다.")
                return
            
            # 필요 포스 수치 계산
            needed_force = target - current_force

            '''
            실제 인게임에서 지역 하나를 이동할 때 최소 필요 포스 수치 = 200

            지역 최소 포스 요구량
                아케인리버 : 30, 100, 190, 280, 440, 560, 670, 760, 850
                그란디스   : 30, 70, 130, 230, 330, 430, 630

            지역 간 최대 차이는 그란디스(어센틱)월드 - 카르시온(430) <-> 탈라하트(630)
            '''
            if  (target != max_force) and needed_force > 200:
                yn = messagebox.askyesno(
                    "계산량 경고",
                    f"필요 포스가 {needed_force}로 매우 큽니다.\n"
                    f"계산량이 많아 정확한 값이 안나올 수 있습니다.\n\n"
                    f"실행하시겠습니까?\n"
                    f"(권장: 목표 포스를 단계별로 나누어 계산)"
                )
                if not yn:
                    return
            
            # DP + 백트래킹으로 최적해 찾기
            best_solutions = self.dp_backtrack_optimization(
                current_symbols, accessible_areas, needed_force, 
                symbol_data, base_force, force_per_level, max_level
            )
            
            # 결과 출력
            result = self.format_results(best_solutions[:10], current_force, target)
            self.root.after(0, lambda: self.update_result(result))
            
        except Exception as e:
            self.root.after(0, lambda e=e: messagebox.showerror("오류", f"계산 실패: {str(e)}"))
        finally:
            self.root.after(0, self.progress.stop)

    ## DP + 백트래킹 최적화 알고리즘
    def dp_backtrack_optimization(self, current_symbols, accessible_areas, needed_force, 
                                symbol_data, base_force, force_per_level, max_level):
        
        print(f"=== 디버깅 정보 ===")
        print(f"accessible_areas: {accessible_areas}")
        print(f"current_symbols: {current_symbols}")
        print(f"needed_force: {needed_force}")
        print(f"max_level: {max_level}")
        print(f"base_force: {base_force}")
        print(f"force_per_level: {force_per_level}")
        
        # 각 심볼별 업그레이드 옵션 미리 계산
        upgrade_options = {}
        total_max_force = 0
        
        for area in accessible_areas:
            current_level = current_symbols.get(area, [0, 0])[0]
            options = []
            
            # 현재 레벨이 0이면 1레벨부터 시작
            start_level = max(current_level, 1)
            
            print(f"지역 {area}: 현재레벨={current_level}, 시작레벨={start_level}")
            
            for target_level in range(start_level, max_level + 1):
                if target_level > current_level:  # 업그레이드가 필요한 경우만
                    cost = self.calculate_upgrade_cost(area, current_level, target_level, symbol_data)
                    
                    if current_level == 0:
                        # 1레벨 : 기본포스 + 추가레벨 * 10
                        added_force = base_force + (target_level - 1) * force_per_level
                    else:
                        # 기존 레벨에서 업그레이드
                        added_force = (target_level - current_level) * force_per_level
                    
                    # 포스 당 메소 비율로 효율 계산
                    efficiency = added_force / cost if cost > 0 else float('inf')

                    options.append((target_level, cost, added_force, efficiency))
                    print(f"  레벨 {target_level}: 비용={cost//10000}만메소, 추가포스={added_force}")
            
            # 현재 지역에서 달성 가능한 최대 포스 계산
            if options:
                max_added_force = max(option[2] for option in options)
                total_max_force += max_added_force
            
            # 효율성 기준으로 정렬
            options.sort(key=lambda x: -x[3])
            upgrade_options[area] = options
        
        print(f"최대 추가 포스: {total_max_force}")
        
        if total_max_force < needed_force:
            print(f"경고: 필요 포스({needed_force})가 달성 가능한 최대 포스({total_max_force})를 초과합니다.")
            return []
        
        # 최소 힙으로 솔루션 관리
        solution_heap = []

        # 최대 저장할 솔루션 수
        # 200포스까지는 모든 결과를 계산하는 것이 목표로 넉넉하게 설정함.
        max_solution = 100000

        solution_counter = 0    # 고유 ID를 위한 카운터
        
        # 남은 지역들로 목표 달성이 가능한지 빠르게 확인
        def can_reach_target(current_force, remaining_areas):
            if current_force >= needed_force:
                return True
            
            max_possible_force = current_force
            for area in remaining_areas:
                if area in upgrade_options and upgrade_options[area]:
                    # 각 지역의 최대 추가 포스
                    max_added_force = max(option[2] for option in upgrade_options[area])
                    max_possible_force += max_added_force

            return max_possible_force >= needed_force

        # 최적의 솔루션 탐색 - 백트래킹 알고리즘 사용
        '''
        백트래킹 알고리즘 (Backtracking)

          가능한 모든 조합을 탐색
          조건에 맞지 않는 경우 탐색 종료
        '''
        def backtrack(area_idx, current_force, current_cost, current_plan):
            nonlocal solution_counter

            # 목표 달성 시
            if current_force >= needed_force:
                # 최소 힙에 솔루션 추가 - 힙 자료구조 사용
                '''
                Heap

                  우선순위 큐를 구현하는 자료구조
                  최소 힙의 경우 항상 가장 작은 값을 루트에 유지
                '''
                heapq.heappush(solution_heap, (current_cost, solution_counter, current_force, current_plan.copy()))
                solution_counter += 1

                # 최대 솔루션 수 유지
                if len(solution_heap) >= max_solution:
                    heapq.heappop(solution_heap)

                return False    # 목표 달성 시 더이상 탐색하지 않음
            
            # 모든 지역을 확인했으면 종료
            if area_idx >= len(accessible_areas):
                return False
            
            '''
            가지치기 알고리즘 (Pruning)

              백트래킹의 과도한 연산을 가지치기를 통해 불필요한 경로를 미리 차단
              연산량이 줄어들어 성능 향상 기대 가능
            '''
            # 휴리스틱 가지치기 - 남은 지역으로 목표 달성이 불가능하면 중단
            remaining_areas = accessible_areas[area_idx:]
            if not can_reach_target(current_force, remaining_areas):
                return False
            
            # 비용 기반 가지치기 - 현재 비용이 이미 찾은 해보다 비싸면 중단
            if solution_heap and len(solution_heap) >= 100:  # 충분한 솔루션이 있을 때만 가지치기
                # 힙의 상위 10개 솔루션의 평균 비용보다 현재 비용이 크면 중단
                top_costs = [solution_heap[i][0] for i in range(min(10, len(solution_heap)))]
                avg_top_cost = sum(top_costs) / len(top_costs)
                if current_cost > avg_top_cost * 1.2:  # 20% 여유를 둠
                    return False
            
            area = accessible_areas[area_idx]
            
            # 현재 지역을 업그레이드하지 않는 경우
            backtrack(area_idx + 1, current_force, current_cost, current_plan)
            
            # 현재 지역을 업그레이드하는 경우
            for target_level, cost, added_force, efficiency in upgrade_options[area]:
                new_force = current_force + added_force
                new_cost = current_cost + cost

                # 비용 기반 조기 가지치기
                if solution_heap and len(solution_heap) >= 50:
                    top_costs = [solution_heap[i][0] for i in range(min(5, len(solution_heap)))]
                    if top_costs and new_cost > max(top_costs) * 1.5:
                        continue
                
                # 상태 업데이트
                current_level = current_symbols.get(area, [0, 0])[0]
                current_plan[area] = (current_level, target_level, cost)
                
                # 재귀 호출
                backtrack(area_idx + 1, new_force, new_cost, current_plan)
                
                # 백트래킹
                del current_plan[area]
            
            return False
        
        # 백트래킹 시작
        backtrack(0, 0, 0, {})
        
        # 힙에서 솔루션을 정렬된 리스트로 변환
        sorted_solutions = []
        
        if not solution_heap:
            print("솔루션을 찾지 못했습니다.")
            return []

        # 힙에서 모든 솔루션 추출
        while solution_heap:
            heap_item = heapq.heappop(solution_heap)
            if len(heap_item) == 4:  # (비용, 고유ID, 포스, 계획)
                cost, _, force, plan = heap_item
                sorted_solutions.append((plan, cost, force))
            else:
                print(f"예상치 못한 힙 아이템 구조: {heap_item}")
                continue
        
        print(f"찾은 솔루션 개수: {len(sorted_solutions)}")
        return sorted_solutions

    ## 심볼 업그레이드 비용 계산 - 동적 계획법 알고리즘 사용
    '''
    DP (메모이제이션에 가까움)
      
      반복되는 계산을 캐시에 저장하여 효율적으로 문제를 해결
      반복 계산은 캐시데이터에서 가져와 다음 계산에서 활용
    '''
    def calculate_upgrade_cost(self, area, current_level, target_level, symbol_data):
        # 메모이제이션을 위한 캐시
        if not hasattr(self, '_cost_cache'):
            self._cost_cache = {}
        
        cache_key = (area, current_level, target_level)
        if cache_key in self._cost_cache:
            return self._cost_cache[cache_key]
        
        total_cost = 0
        for level in range(current_level + 1, target_level + 1):
            if level in symbol_data[area]:
                total_cost += symbol_data[area][level]
        
        result = total_cost * 10000
        self._cost_cache[cache_key] = result
        return result


    ## 캐릭터 레벨에 따른 접근 가능 지역 반환
    def get_accessible_areas(self, character_level):
        accessible = []
        
        if self.symbol_type.get() == "arcane":
            for level_req in [200, 210, 220, 225, 230, 235]:
                if character_level >= level_req:
                    accessible.append(self.level_access[level_req])
        else:
            for level_req in [260, 265, 270, 275, 280, 285, 290]:
                if character_level >= level_req:
                    accessible.append(self.level_access[level_req])
        
        return accessible
    

    ## 심볼명을 지역 키로 변환
    def get_area_key(self, symbol_name):
        name_mapping = {
            '소멸의 여로': 'vanishing_journey',
            '츄츄 아일랜드': 'chu_chu_island',
            '레헬른': 'lachelein',
            '아르카나': 'arcana',
            '모라스': 'morass',
            '에스페라': 'esfera',
            '세르니움': 'cernium',
            '아르크스': 'arcus_island',
            '오디움': 'odium',
            '도원경': 'shangri_la',
            '아르테리아': 'arteria',
            '카르시온': 'carcion',
            '탈라하트': 'tallahart'
        }
        return name_mapping.get(symbol_name, symbol_name)
    

    ## 결과 Formatting
    def format_results(self, solutions, current_force, target_force):
        if not solutions:
            messagebox.showerror("오류", "목표 포스에 도달할 수 있는 조합이 없습니다.")
            return
        
        result = f"현재 포스: {current_force}\n"
        result += f"목표 포스: {target_force}\n"
        result += f"필요 포스: {target_force - current_force}\n\n"
        result += "=== 최적화 결과 (비용 기준 오름차순) ===\n\n"
        
        area_names = {
            'vanishing_journey': '소멸의 여로',
            'chu_chu_island': '츄츄 아일랜드',
            'lachelein': '레헬른',
            'arcana': '아르카나',
            'morass': '모라스',
            'esfera': '에스페라',
            'cernium': '세르니움',
            'arcus_island': '아르크스',
            'odium': '오디움',
            'shangri_la': '도원경',
            'arteria': '아르테리아',
            'carcion': '카르시온',
            'tallahart': '탈라하트'
        }
        
        for i, (upgrade_plan, total_cost, added_force) in enumerate(solutions[:5], 1):
            result += f"[방법 {i}] 총 비용: {total_cost:,} 메소, 추가 포스: +{added_force}\n"
            
            for area, (current, target, cost) in upgrade_plan.items():
                area_name = area_names.get(area, area)
                result += f"  {area_name}: Lv.{current} → Lv.{target} (비용: {cost:,} 메소)\n"
            
            result += "\n"
        
        return result
    

    ## 결과 텍스트 업데이트
    def update_result(self, result):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, str(result))


## 메인 실행 함수
def main():
    root = tk.Tk()
    app = MapleSymbolOptimizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()