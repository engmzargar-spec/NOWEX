"""
تست بار برای موتور معاملاتی
"""

from locust import HttpUser, task, between
import random

class TradingUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """هنگام شروع کاربر"""
        self.client.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test_token_123"
        }
    
    @task(3)
    def check_health(self):
        """بررسی سلامت سرویس"""
        self.client.get("/api/health")
    
    @task(2)
    def get_market_data(self):
        """دریافت داده‌های بازار"""
        instruments = ["XAUUSD", "XAGUSD", "USOIL", "NASDAQ"]
        instrument = random.choice(instruments)
        self.client.get(f"/api/market/{instrument}")
    
    @task(1)
    def place_order(self):
        """ثبت سفارش"""
        order_data = {
            "instrument": random.choice(["XAUUSD", "XAGUSD"]),
            "side": random.choice(["BUY", "SELL"]),
            "volume": random.uniform(0.01, 10.0),
            "price": random.uniform(1800, 1900),
            "order_type": "MARKET"
        }
        
        with self.client.post("/api/trading/order", 
                            json=order_data, 
                            catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Order failed: {response.status_code}")
    
    @task(1)
    def get_portfolio(self):
        """دریافت پورتفولیو"""
        self.client.get("/api/finance/portfolio")