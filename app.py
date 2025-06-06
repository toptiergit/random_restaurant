from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime
import json
import random
import os

app = Flask(__name__)

# โหลดและจัดการข้อมูลร้านอาหาร
class RestaurantManager:
    def __init__(self):
        self.load_restaurants()
        self.load_history()
        self.load_locations()
        
    def load_restaurants(self):
        if os.path.exists('restaurants.json'):
            with open('restaurants.json', 'r', encoding='utf-8') as f:
                self.restaurant_categories = json.load(f)
        else:
            self.restaurant_categories = self.get_default_restaurants()
            self.save_restaurants()
            
    def load_history(self):
        if os.path.exists('restaurant_history.json'):
            with open('restaurant_history.json', 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def load_locations(self):
        if os.path.exists('restaurant_locations.json'):
            with open('restaurant_locations.json', 'r', encoding='utf-8') as f:
                self.locations = json.load(f)
        else:
            self.locations = self.get_default_locations()
            self.save_locations()

    def save_restaurants(self):
        with open('restaurants.json', 'w', encoding='utf-8') as f:
            json.dump(self.restaurant_categories, f, ensure_ascii=False, indent=2)

    def save_history(self):
        with open('restaurant_history.json', 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def save_locations(self):
        with open('restaurant_locations.json', 'w', encoding='utf-8') as f:
            json.dump(self.locations, f, ensure_ascii=False, indent=2)
            
    def get_default_restaurants(self):
        return {
            "อาหารอีสาน": ["ส้มตำบุยายใบ"],
            "อาหารตามสั่ง": ["ร้านป้าสัมพันธ์", "ครัวริมบึง", "ครัวลีลา"],
            "ก๋วยเตี๋ยว": ["ร้านสิบล้อ", "ก๋วยเตี๋ยวทองเเพร", "เย็นตาโฟ"],
            "อาหารใต้": ["ข้าวราดเเกงปักใต้"],
            "อาหารญี่ปุ่น": ["ร้านญี่ปุ่น"],
            "สเต็ก": ["ฮักสเต็ก"],
            "อาหารทั่วไป": ["ริมบ้านชานเมือง", "Black moon"]
        }

    def get_default_locations(self):
        return {
            "ตำเเซบเเต๊ด*โคกไม้เเดง": {"lat": 16.44, "lon": 102.83},
            "ส้มตำเจ๊ปุ๊ก *บุยายใบ": {"lat": 16.45, "lon": 102.84},
            "ส้มตำเจ๊นิว*ท่าประชุม": {"lat": 16.46, "lon": 102.85},
            "อีสานเด้อ": {"lat": 16.47, "lon": 102.86},
            "ตำมั่ว IP7": {"lat": 16.48, "lon": 102.87},
            "ร้านป้าสัมพันธ์": {"lat": 16.49, "lon": 102.88},
            "บ้านสวนริมสระ": {"lat": 16.50, "lon": 102.89},
            "เป็ดพันปี": {"lat": 16.51, "lon": 102.90},
            "ร้านสิบล้อ": {"lat": 16.52, "lon": 102.91},
            "ก๋วยเตี๋ยวทองเเพร": {"lat": 16.53, "lon": 102.92},
            "เย็นตาโฟ": {"lat": 16.54, "lon": 102.93},
            "ก๋วยเตี๋ยวพริกจี่": {"lat": 16.55, "lon": 102.94},
            "ข้าวราดเเกงปักใต้": {"lat": 16.56, "lon": 102.95},
            "ร้านญี่ปุ่น": {"lat": 16.57, "lon": 102.96},
            "ฮักสเต็ก": {"lat": 16.58, "lon": 102.97},
            "ครัวลีลา": {"lat": 16.59, "lon": 102.98},
            "ริมบ้านชานเมือง": {"lat": 16.60, "lon": 102.99},
            "Black moon": {"lat": 16.61, "lon": 103.0}
        }

    def get_location(self, name):
        return self.locations.get(name)

# สร้าง instance ของ RestaurantManager
manager = RestaurantManager()

@app.route('/')
def index():
    return render_template('index.html', 
                         categories=manager.restaurant_categories,
                         history=manager.history[:5])

@app.route('/random', methods=['POST'])
def random_restaurant():
    category = request.form.get('category', 'ทั้งหมด')
    
    if category == 'ทั้งหมด':
        available_restaurants = [r for restaurants in manager.restaurant_categories.values() 
                               for r in restaurants]
    else:
        available_restaurants = manager.restaurant_categories.get(category, [])
        
    if not available_restaurants:
        return jsonify({'error': 'ไม่พบร้านอาหารในหมวดหมู่ที่เลือก'})
        
    # กรองร้านที่เพิ่งถูกเลือก
    filtered_restaurants = [r for r in available_restaurants 
                          if not manager.history or r != manager.history[0]['restaurant']]
    
    if not filtered_restaurants:
        filtered_restaurants = available_restaurants
        
    selected = random.choice(filtered_restaurants)
    
    # บันทึกประวัติ
    history_entry = {
        'restaurant': selected,
        'category': next(cat for cat, restaurants in manager.restaurant_categories.items() 
                        if selected in restaurants),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    manager.history.insert(0, history_entry)
    if len(manager.history) > 5:
        manager.history.pop()
    manager.save_history()
    
    return jsonify(history_entry)

@app.route('/manage')
def manage():
    # นับจำนวนร้านในแต่ละประเภท
    restaurant_counts = {category: len(restaurants) 
                        for category, restaurants in manager.restaurant_categories.items()}
    
    return render_template('manage.html', 
                         categories=manager.restaurant_categories.keys(),
                         restaurants=manager.restaurant_categories,
                         restaurant_counts=restaurant_counts)

@app.route('/add', methods=['POST'])
def add_restaurant():
    name = request.form.get('name')
    category = request.form.get('category')
    
    if name and category:
        # ถ้ายังไม่มีหมวดหมู่นี้ ให้สร้างใหม่
        if category not in manager.restaurant_categories:
            manager.restaurant_categories[category] = []
        
        # เพิ่มร้านอาหารถ้ายังไม่มีในหมวดหมู่
        if name not in manager.restaurant_categories[category]:
            manager.restaurant_categories[category].append(name)
            manager.save_restaurants()
    
    return redirect(url_for('manage'))

@app.route('/delete', methods=['POST'])
def delete_restaurant():
    name = request.form.get('name')
    category = request.form.get('category')  # เพิ่ม category ในการลบ
    
    if name and category:
        if category in manager.restaurant_categories:
            if name in manager.restaurant_categories[category]:
                manager.restaurant_categories[category].remove(name)
                # ถ้าไม่มีร้านอาหารในหมวดหมู่แล้ว ให้ลบหมวดหมู่ออก
                if not manager.restaurant_categories[category]:
                    del manager.restaurant_categories[category]
                manager.save_restaurants()
    
    return redirect(url_for('manage'))

@app.route('/add_category', methods=['POST'])
def add_category():
    category = request.form.get('category')
    
    if category:
        # ตรวจสอบว่าประเภทนี้มีอยู่แล้วหรือไม่
        if category not in manager.restaurant_categories:
            manager.restaurant_categories[category] = []
            manager.save_restaurants()
    
    return redirect(url_for('manage'))

@app.route('/delete_category', methods=['POST'])
def delete_category():
    category = request.form.get('category')
    
    if category:
        # ลบประเภทอาหารและร้านอาหารทั้งหมดในประเภทนั้น
        if category in manager.restaurant_categories:
            del manager.restaurant_categories[category]
            manager.save_restaurants()
    
    return redirect(url_for('manage'))


@app.route('/location')
def location_point():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'no restaurant provided'}), 400
    location = manager.get_location(name)
    if location:
        return jsonify({'restaurant': name, 'location': location})
    return jsonify({'error': 'ไม่พบข้อมูลพิกัด'}), 404

if __name__ == '__main__':
    # เปลี่ยนจาก debug mode เป็น production mode
    app.run() 