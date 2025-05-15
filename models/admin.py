import json
import os
from models.car import Car

class Admin:
    def __init__(self, username, password, first_name, last_name):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
    
    @classmethod
    def load_admins(cls):
        if not os.path.exists("data"):
            os.makedirs("data")
            
        if not os.path.exists("data/admins.json") or os.stat("data/admins.json").st_size == 0:
            return []
        
        try:
            with open("data/admins.json", "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading admins: {e}")
            return []
    
    @classmethod
    def save_admin(cls, admin):
        if not os.path.exists("data"):
            os.makedirs("data")
            
        admins = cls.load_admins()
        
        # Check if username already exists
        for a in admins:
            if a["username"] == admin.username:
                print("Username already exists.")
                return False
        
        admins.append(admin.__dict__)
        
        try:
            with open("data/admins.json", "w") as f:
                json.dump(admins, f, indent=4)
            print("Admin registered successfully.")
            return True
        except Exception as e:
            print(f"Error saving admin: {e}")
            return False
    
    @staticmethod
    def add_car():
        """Add a new car to the system"""
        print("\n=== ADD NEW CAR ===")
        
        # Generate a unique car ID
        cars = Car.load_cars()
        if cars:
            # Find the highest existing ID and increment by 1
            try:
                max_id = max(int(car.car_id) for car in cars if car.car_id.isdigit())
                car_id = str(max_id + 1)
            except ValueError:
                car_id = "1001"  # Fallback if no numeric IDs
        else:
            car_id = "1001"  # Starting ID if no cars exist
        
        print(f"New Car ID: {car_id}")
        
        brand = input("Enter car brand: ")
        model = input("Enter car model: ")
        
        try:
            seating_capacity = int(input("Enter seating capacity: "))
            rental_price = float(input("Enter rental price per day: $"))
            
            if seating_capacity <= 0 or rental_price <= 0:
                print("Capacity and price must be positive numbers.")
                return
                
            new_car = Car(car_id, brand, model, seating_capacity, rental_price)
            
            cars.append(new_car)
            Car.save_cars(cars)
            
            print(f"Car added successfully: {brand} {model} (ID: {car_id})")
            
        except ValueError:
            print("Invalid input. Please enter numeric values for capacity and price.")
    
    @staticmethod
    def remove_car():
        """Remove a car from the system"""
        Car.display_all_cars()
        
        car_id = input("\nEnter ID of car to remove: ")
        
        cars = Car.load_cars()
        found = False
        
        for i, car in enumerate(cars):
            if car.car_id == car_id:
                # Check if the car is currently rented
                if not car.available:
                    print("Cannot remove a car that is currently rented.")
                    return
                
                car_info = f"{car.brand} {car.model}"
                cars.pop(i)
                Car.save_cars(cars)
                print(f"Car removed successfully: {car_info} (ID: {car_id})")
                found = True
                break
        
        if not found:
            print(f"Car with ID {car_id} not found.")
    
    @staticmethod
    def view_rentals():
        """View all current rentals in the system"""
        from models.rental import RentalManager
        
        print("\n=== RENTAL REPORTS ===")
        print("1. View all active rentals")
        print("2. View all customers with rentals")
        print("3. View rental history for specific customer")
        choice = input("Choose: ")
        
        if choice == '1':
            RentalManager.view_active_rentals()
        elif choice == '2':
            RentalManager.view_customer_rentals()
        elif choice == '3':
            username = input("Enter customer username: ")
            RentalManager.view_customer_rental_history(username)
        else:
            print("Invalid choice.")
