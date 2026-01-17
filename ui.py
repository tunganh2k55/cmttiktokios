import tkinter as tk
from tkinter import ttk
import threading


class TikTokTDSUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TikTok TDS Manager")
        self.root.geometry("1100x500")
        
        # Biến lưu giá trị nhập
        self.total_threads = None
        self.concurrent_threads = None
        self.input_ready = threading.Event()
        
        # Ẩn cửa sổ chính ban đầu
        self.root.withdraw()
        
        # Tạo bảng với cột mới
        self.tree = ttk.Treeview(
            self.root, 
            columns=("localIP", "access_token", "userTikTok", "jobProgress", "xuThem", "status"), 
            show="headings", 
            height=20
        )
        
        # Đặt tiêu đề cột
        self.tree.heading("localIP", text="Local IP")
        self.tree.heading("access_token", text="Access Token")
        self.tree.heading("userTikTok", text="User TikTok")
        self.tree.heading("jobProgress", text="Job Progress")
        self.tree.heading("xuThem", text="Xu thêm")
        self.tree.heading("status", text="Status")
        
        # Đặt độ rộng cột và căn giữa
        self.tree.column("localIP", width=150, anchor="center")
        self.tree.column("access_token", width=200, anchor="center")
        self.tree.column("userTikTok", width=150, anchor="center")
        self.tree.column("jobProgress", width=150, anchor="center")
        self.tree.column("xuThem", width=120, anchor="center")
        self.tree.column("status", width=300, anchor="center")
        
        # Căn giữa cho các cột dữ liệu
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        
        # Thêm scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Đặt vị trí
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Lưu trữ item_id để cập nhật theo localip
        self.item_ids = {}  # Dict: {localip: item_id}
        self.lock = threading.Lock()  # Lock để thread-safe
    
    def add_row(self, localip, access_token, userTikTok, status="Đang khởi tạo...", jobProgress="0/0", xuThem=0):
        """Thêm một dòng mới vào bảng"""
        # Rút gọn access_token nếu quá dài
        display_token = access_token[:40] + "..." if len(access_token) > 40 else access_token
        
        with self.lock:
            item_id = self.tree.insert(
                "", 
                "end", 
                values=(localip, display_token, userTikTok, jobProgress, xuThem, status)
            )
            self.item_ids[localip] = item_id
            self.root.update()
        return item_id
    
    def update_status(self, localip, new_status):
        """Cập nhật status của dòng theo localip"""
        with self.lock:
            item_id = self.item_ids.get(localip)
            if item_id:
                current_values = list(self.tree.item(item_id, "values"))
                if len(current_values) == 6:
                    current_values[5] = new_status
                    self.tree.item(item_id, values=tuple(current_values))
                    self.root.update()
    
    def update_job_progress(self, localip, jobcache_done, job_success_paid):
        """Cập nhật số job đã làm và job nhận được tiền theo localip"""
        with self.lock:
            item_id = self.item_ids.get(localip)
            if item_id:
                current_values = list(self.tree.item(item_id, "values"))
                if len(current_values) == 6:
                    current_values[3] = f"{jobcache_done}/{job_success_paid}"
                    self.tree.item(item_id, values=tuple(current_values))
                    self.root.update()
    
    def update_xu_them(self, localip, xu_them):
        """Cập nhật xu thêm của dòng theo localip"""
        with self.lock:
            item_id = self.item_ids.get(localip)
            if item_id:
                current_values = list(self.tree.item(item_id, "values"))
                if len(current_values) == 6:
                    current_values[4] = xu_them
                    self.tree.item(item_id, values=tuple(current_values))
                    self.root.update()
    
    def run(self):
        """Chạy UI"""
        self.root.mainloop()
    
    def close(self):
        """Đóng UI"""
        self.root.quit()
        self.root.destroy()
    
    def show_input_dialog(self):
        """Hiển thị dialog nhập số thiết bị và số luồng đồng thời"""
        # Tạo dialog độc lập
        dialog = tk.Toplevel(self.root)
        dialog.title("Cấu hình")
        dialog.geometry("400x220")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()  # Modal dialog
        
        # Hiển thị root window để dialog có thể hiển thị
        self.root.deiconify()
        self.root.update()
        
        # Đặt dialog ở giữa màn hình
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Frame chứa các input
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill="both", expand=True)
        
        # Label và input cho số thiết bị
        ttk.Label(frame, text="Số thiết bị chạy:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=10)
        total_threads_var = tk.StringVar(value="1")
        total_entry = ttk.Entry(frame, textvariable=total_threads_var, width=20, font=("Arial", 10))
        total_entry.grid(row=0, column=1, padx=10, pady=10)
        total_entry.focus()
        
        # Label và input cho số luồng đồng thời
        ttk.Label(frame, text="Số luồng đồng thời:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=10)
        concurrent_threads_var = tk.StringVar(value="1")
        concurrent_entry = ttk.Entry(frame, textvariable=concurrent_threads_var, width=20, font=("Arial", 10))
        concurrent_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Label thông báo lỗi
        error_label = ttk.Label(frame, text="", foreground="red", font=("Arial", 9))
        error_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        def validate_and_close():
            """Validate và đóng dialog"""
            try:
                total = int(total_threads_var.get())
                concurrent = int(concurrent_threads_var.get())
                
                if total <= 0 or concurrent <= 0:
                    error_label.config(text="Số phải lớn hơn 0!")
                    return
                
                if concurrent > total:
                    concurrent = total
                    concurrent_threads_var.set(str(concurrent))
                
                self.total_threads = total
                self.concurrent_threads = concurrent
                self.input_ready.set()
                dialog.destroy()
                # Hiển thị lại cửa sổ chính sau khi dialog đóng
                self.root.deiconify()
                
            except ValueError:
                error_label.config(text="Vui lòng nhập số hợp lệ!")
        
        # Nút OK
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ok_button = ttk.Button(button_frame, text="Bắt đầu", command=validate_and_close, width=15)
        ok_button.pack(side="left", padx=5)
        
        def cancel_action():
            """Hủy và thoát"""
            self.total_threads = None
            self.concurrent_threads = None
            self.input_ready.set()
            dialog.destroy()
            self.root.quit()
        
        cancel_button = ttk.Button(button_frame, text="Hủy", command=cancel_action, width=15)
        cancel_button.pack(side="left", padx=5)
        
        # Bind Enter key
        total_entry.bind("<Return>", lambda e: concurrent_entry.focus())
        concurrent_entry.bind("<Return>", lambda e: validate_and_close())
        
        # Đợi dialog đóng
        dialog.wait_window()
    
