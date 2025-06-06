import random
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os

# จัดกลุ่มร้านอาหารตามประเภท
restaurant_categories = {
    "อาหารอีสาน": ["ส้มตำบุยายใบ"],
    "อาหารตามสั่ง": ["ร้านป้าสัมพันธ์", "ครัวริมบึง", "ครัวลีลา"],
    "ก๋วยเตี๋ยว": ["ร้านสิบล้อ", "ก๋วยเตี๋ยวทองเเพร", "เย็นตาโฟ"],
    "อาหารใต้": ["ข้าวราดเเกงปักใต้"],
    "อาหารญี่ปุ่น": ["ร้านญี่ปุ่น"],
    "สเต็ก": ["ฮักสเต็ก"],
    "อาหารทั่วไป": ["ริมบ้านชานเมือง", "Black moon"]
}

# สร้าง list ทุกร้าน
all_restaurants = [restaurant for restaurants in restaurant_categories.values() for restaurant in restaurants]

# กำหนดไฟล์เก็บประวัติ
HISTORY_FILE = "restaurant_history.json"
RESTAURANTS_FILE = "restaurants.json"
MAX_HISTORY = 5

class RestaurantManager:
    def __init__(self):
        # โหลดข้อมูลร้านอาหาร
        self.load_restaurants()
        
    def load_restaurants(self):
        """โหลดข้อมูลร้านอาหารจากไฟล์"""
        if os.path.exists(RESTAURANTS_FILE):
            try:
                with open(RESTAURANTS_FILE, 'r', encoding='utf-8') as f:
                    self.restaurant_categories = json.load(f)
            except:
                self.restaurant_categories = self.get_default_restaurants()
        else:
            self.restaurant_categories = self.get_default_restaurants()
        
        # อัพเดท all_restaurants
        self.update_all_restaurants()
        
    def get_default_restaurants(self):
        """ข้อมูลร้านอาหารเริ่มต้น"""
        return {
            "อาหารอีสาน": ["ส้มตำบุยายใบ"],
            "อาหารตามสั่ง": ["ร้านป้าสัมพันธ์", "ครัวริมบึง", "ครัวลีลา"],
            "ก๋วยเตี๋ยว": ["ร้านสิบล้อ", "ก๋วยเตี๋ยวทองเเพร", "เย็นตาโฟ"],
            "อาหารใต้": ["ข้าวราดเเกงปักใต้"],
            "อาหารญี่ปุ่น": ["ร้านญี่ปุ่น"],
            "สเต็ก": ["ฮักสเต็ก"],
            "อาหารทั่วไป": ["ริมบ้านชานเมือง", "Black moon"]
        }
    
    def save_restaurants(self):
        """บันทึกข้อมูลร้านอาหารลงไฟล์"""
        with open(RESTAURANTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.restaurant_categories, f, ensure_ascii=False, indent=2)
    
    def update_all_restaurants(self):
        """อัพเดทรายการร้านอาหารทั้งหมด"""
        self.all_restaurants = [restaurant for restaurants in self.restaurant_categories.values() 
                              for restaurant in restaurants]

class RestaurantManagerUI:
    def __init__(self, parent, restaurant_manager):
        self.window = tk.Toplevel(parent)
        self.window.title("จัดการร้านอาหาร")
        self.window.geometry("600x500")
        self.manager = restaurant_manager
        self.setup_ui()
        
    def setup_ui(self):
        frame = ttk.Frame(self.window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ส่วนเพิ่มประเภทอาหาร
        category_frame = ttk.LabelFrame(frame, text="เพิ่มประเภทอาหารใหม่", padding="10")
        category_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        self.new_category = ttk.Entry(category_frame)
        self.new_category.grid(row=0, column=0, padx=5)
        ttk.Button(category_frame, text="เพิ่มประเภท", 
                  command=self.add_category).grid(row=0, column=1)
        
        # ส่วนเพิ่มร้านอาหาร
        restaurant_frame = ttk.LabelFrame(frame, text="เพิ่มร้านอาหาร", padding="10")
        restaurant_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        self.selected_category = ttk.Combobox(restaurant_frame, 
                                            values=list(self.manager.restaurant_categories.keys()))
        self.selected_category.grid(row=0, column=0, padx=5)
        self.selected_category.set("เลือกประเภทอาหาร")
        
        self.new_restaurant = ttk.Entry(restaurant_frame)
        self.new_restaurant.grid(row=0, column=1, padx=5)
        
        ttk.Button(restaurant_frame, text="เพิ่มร้าน", 
                  command=self.add_restaurant).grid(row=0, column=2)
        
        # แสดงรายการร้านอาหาร
        list_frame = ttk.LabelFrame(frame, text="รายการร้านอาหาร", padding="10")
        list_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        self.restaurant_tree = ttk.Treeview(list_frame, columns=("category", "restaurant"), 
                                          show="headings")
        self.restaurant_tree.heading("category", text="ประเภท")
        self.restaurant_tree.heading("restaurant", text="ชื่อร้าน")
        self.restaurant_tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # ปุ่มลบร้านอาหาร
        ttk.Button(list_frame, text="ลบรายการที่เลือก", 
                  command=self.delete_selected).grid(row=1, column=0, pady=5)
        
        self.update_restaurant_list()
        
    def add_category(self):
        category = self.new_category.get().strip()
        if category:
            if category not in self.manager.restaurant_categories:
                self.manager.restaurant_categories[category] = []
                self.manager.save_restaurants()
                self.selected_category['values'] = list(self.manager.restaurant_categories.keys())
                self.new_category.delete(0, tk.END)
                self.update_restaurant_list()
            else:
                messagebox.showwarning("แจ้งเตือน", "มีประเภทอาหารนี้อยู่แล้ว")
                
    def add_restaurant(self):
        category = self.selected_category.get()
        restaurant = self.new_restaurant.get().strip()
        
        if category and restaurant and category in self.manager.restaurant_categories:
            if restaurant not in self.manager.restaurant_categories[category]:
                self.manager.restaurant_categories[category].append(restaurant)
                self.manager.save_restaurants()
                self.manager.update_all_restaurants()
                self.new_restaurant.delete(0, tk.END)
                self.update_restaurant_list()
            else:
                messagebox.showwarning("แจ้งเตือน", "มีร้านอาหารนี้อยู่แล้ว")
                
    def delete_selected(self):
        selected_item = self.restaurant_tree.selection()
        if selected_item:
            item = self.restaurant_tree.item(selected_item[0])
            category = item['values'][0]
            restaurant = item['values'][1]
            
            if messagebox.askyesno("ยืนยัน", f"ต้องการลบร้าน {restaurant} หรือไม่?"):
                self.manager.restaurant_categories[category].remove(restaurant)
                if not self.manager.restaurant_categories[category]:  # ถ้าไม่มีร้านในประเภทนี้แล้ว
                    del self.manager.restaurant_categories[category]
                    self.selected_category['values'] = list(self.manager.restaurant_categories.keys())
                
                self.manager.save_restaurants()
                self.manager.update_all_restaurants()
                self.update_restaurant_list()
                
    def update_restaurant_list(self):
        for item in self.restaurant_tree.get_children():
            self.restaurant_tree.delete(item)
            
        for category, restaurants in self.manager.restaurant_categories.items():
            for restaurant in restaurants:
                self.restaurant_tree.insert("", tk.END, values=(category, restaurant))

class RestaurantRandomizer:
    def __init__(self):
        self.window = tk.Tk()
        self.selected_category = tk.StringVar()
        self.restaurant_manager = RestaurantManager()
        self.history = self.load_history()
        self.setup_ui()
        
    def load_history(self):
        """โหลดประวัติจากไฟล์"""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self):
        """บันทึกประวัติลงไฟล์"""
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def setup_ui(self):
        self.window.title("สุ่มร้านอาหาร")
        self.window.geometry("500x400")

        frame = ttk.Frame(self.window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Combobox สำหรับเลือกประเภทอาหาร
        ttk.Label(frame, text="เลือกประเภทอาหาร:").grid(row=0, column=0, pady=5)
        categories = ["ทั้งหมด"] + list(restaurant_categories.keys())
        category_combo = ttk.Combobox(frame, textvariable=self.selected_category, values=categories)
        category_combo.grid(row=0, column=1, pady=5)
        category_combo.set("ทั้งหมด")

        # ปุ่มสุ่ม
        random_button = ttk.Button(frame, text="สุ่มร้านอาหาร", command=self.random_restaurant)
        random_button.grid(row=1, column=0, columnspan=2, pady=20)

        # ผลลัพธ์
        self.result_label = ttk.Label(frame, text="กดปุ่มเพื่อสุ่มร้านอาหาร", font=('TH Sarabun New', 16))
        self.result_label.grid(row=2, column=0, columnspan=2, pady=10)

        # ประวัติ
        history_frame = ttk.LabelFrame(frame, text="ประวัติการสุ่ม", padding="10")
        history_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        self.history_label = ttk.Label(history_frame, text="")
        self.history_label.grid(row=0, column=0)

        # จัดให้อยู่ตรงกลาง
        frame.grid_columnconfigure(1, weight=1)

        # เพิ่มปุ่มจัดการร้านอาหาร
        manage_button = ttk.Button(frame, text="จัดการร้านอาหาร", 
                                 command=self.open_manager)
        manage_button.grid(row=4, column=0, columnspan=2, pady=10)

        # อัพเดทประวัติตอนเริ่มโปรแกรม
        self.update_history_display()

    def update_history_display(self):
        """อัพเดทการแสดงประวัติ"""
        if not self.history:
            history_text = "ยังไม่มีประวัติการสุ่ม"
        else:
            history_text = "ร้านที่เคยสุ่มได้:\n" + "\n".join(
                f"{i+1}. {entry['restaurant']} ({entry['timestamp']})" 
                for i, entry in enumerate(self.history))
        self.history_label.config(text=history_text)

    def open_manager(self):
        RestaurantManagerUI(self.window, self.restaurant_manager)

    def random_restaurant(self):
        category = self.selected_category.get()
        
        if category == "ทั้งหมด":
            available_restaurants = self.restaurant_manager.all_restaurants
        else:
            available_restaurants = self.restaurant_manager.restaurant_categories[category]

        # กรองร้านที่เพิ่งถูกเลือกออก โดยตรวจสอบจากชื่อร้านในประวัติล่าสุด
        filtered_restaurants = [
            r for r in available_restaurants
            if not any(entry["restaurant"] == r for entry in self.history[:2])
        ]
        
        if not filtered_restaurants:
            filtered_restaurants = available_restaurants

        # สุ่มร้านและอัพเดทประวัติ
        selected = random.choice(filtered_restaurants)
        
        # เพิ่มเวลาที่สุ่มได้
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            "restaurant": selected,
            "timestamp": current_time,
            "category": next(cat for cat, restaurants in restaurant_categories.items() 
                           if selected in restaurants)
        }
        
        self.history.insert(0, history_entry)
        if len(self.history) > MAX_HISTORY:
            self.history.pop()

        # บันทึกประวัติลงไฟล์
        self.save_history()

        # แสดงผล
        self.result_label.config(
            text=f"วันนี้ไปกินที่: {selected}\n"
                 f"ประเภท: {history_entry['category']}\n"
                 f"เวลา: {current_time}")
        
        # อัพเดทการแสดงประวัติ
        history_text = "ร้านที่เคยสุ่มได้:\n" + "\n".join(
            f"{i+1}. {entry['restaurant']} ({entry['timestamp']})" 
            for i, entry in enumerate(self.history))
        self.history_label.config(text=history_text)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = RestaurantRandomizer()
    app.run() 