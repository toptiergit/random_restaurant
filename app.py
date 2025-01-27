from flask import Flask, render_template, jsonify, request
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
            
    def save_restaurants(self):
        with open('restaurants.json', 'w', encoding='utf-8') as f:
            json.dump(self.restaurant_categories, f, ensure_ascii=False, indent=2)
            
    def save_history(self):
        with open('restaurant_history.json', 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
            
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
    return render_template('manage.html', 
                         categories=manager.restaurant_categories)

@app.route('/api/restaurant', methods=['POST'])
def add_restaurant():
    data = request.get_json()
    category = data.get('category')
    restaurant = data.get('restaurant')
    
    if category not in manager.restaurant_categories:
        manager.restaurant_categories[category] = []
    
    if restaurant not in manager.restaurant_categories[category]:
        manager.restaurant_categories[category].append(restaurant)
        manager.save_restaurants()
        return jsonify({'success': True})
    
    return jsonify({'error': 'ร้านอาหารนี้มีอยู่แล้ว'})

@app.route('/api/restaurant', methods=['DELETE'])
def delete_restaurant():
    data = request.get_json()
    category = data.get('category')
    restaurant = data.get('restaurant')
    
    if (category in manager.restaurant_categories and 
        restaurant in manager.restaurant_categories[category]):
        manager.restaurant_categories[category].remove(restaurant)
        if not manager.restaurant_categories[category]:
            del manager.restaurant_categories[category]
        manager.save_restaurants()
        return jsonify({'success': True})
    
    return jsonify({'error': 'ไม่พบร้านอาหารที่ต้องการลบ'})

if __name__ == '__main__':
    # เปลี่ยนจาก debug mode เป็น production mode
    app.run() 