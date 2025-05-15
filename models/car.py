import json
import os

class Car:
    def __init__(self, car_id, brand, model, seating_capacity, rental_price, available=True):
        self.car_id = car_id
        self.brand = brand
        self.model = model
        self.seating_capacity = seating_capacity
        self.rental_price = rental_price  # per day
        self.available = available

    def __str__(self):
        status = "Available" if self.available else "Currently Rented"
        return f"ID: {self.car_id} | {self.brand} {self.model} | Seats: {self.seating_capacity} | Price: ${self.rental_price}/day | Status: {status}"

    @classmethod
    def load_cars(cls):
        if not os.path.exists("data"):
            os.makedirs("data")
            
        if not os.path.exists("data/cars.json") or os.stat("data/cars.json").st_size == 0:
            return []
        
        try:
            with open("data/cars.json", "r") as f:
                car_data = json.load(f)
                return [cls(**car) for car in car_data]
        except Exception as e:
            print(f"Error loading cars: {e}")
            return []

    @classmethod
    def save_cars(cls, cars):
        if not os.path.exists("data"):
            os.makedirs("data")
            
        try:
            with open("data/cars.json", "w") as f:
                cars_dict = [car.__dict__ for car in cars]
                json.dump(cars_dict, f, indent=4)
        except Exception as e:
            print(f"Error saving cars: {e}")

    @classmethod
    def get_car_by_id(cls, car_id):
        cars = cls.load_cars()
        for car in cars:
            if car.car_id == car_id:
                return car
        return None

    @classmethod
    def display_all_cars(cls):
        cars = cls.load_cars()
        if not cars:
            print("No cars available in the system.")
            return
        
        print("\n=== ALL CARS ===")
        for car in cars:
            print(car)

    @classmethod
    def display_available_cars(cls):
        cars = cls.load_cars()
        available_cars = [car for car in cars if car.available]
        
        if not available_cars:
            print("No cars available for rent at the moment.")
            return
        
        print("\n=== AVAILABLE CARS ===")
        for car in available_cars:
            print(car)

    @classmethod
    def update_car_availability(cls, car_id, available):
        cars = cls.load_cars()
        for car in cars:
            if car.car_id == car_id:
                car.available = available
                cls.save_cars(cars)
                return True
        return False
