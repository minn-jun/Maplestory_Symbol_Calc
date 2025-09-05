import tkinter as tk
from app import MapleSymbolOptimizer

def main():
    """애플리케이션의 메인 실행 함수"""
    root = tk.Tk()
    app = MapleSymbolOptimizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()