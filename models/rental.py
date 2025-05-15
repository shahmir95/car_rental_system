import json
import os
from models.car import Car
from datetime import datetime

class RentalManager:
    """Class to manage all rentals in the system"""
    
    @classmethod
    def load_rentals(cls):
        if not os.path.exists("data"):
            os.makedirs("data")
            
        if not os.path.exists("data/rentals.json") or os.stat("data/rentals.json").st_size == 0:
            return {}
        
        try:
            with open("data/rentals.json", "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading rentals: {e}")
            return {}
    
    @classmethod
    def save_rentals(cls, rentals):
        if not os.path.exists("data"):
            os.makedirs("data")
            
        try:
            with open("data/rentals.json", "w") as f:
                json.dump(rentals, f, indent=4)
        except Exception as e:
            print(f"Error saving rentals: {e}")
    
    @classmethod
    def add_rental(cls, username, rental):
        """Add a rental record to the global rental database"""
        rentals = cls.load_rentals()
        
        if username not in rentals:
            rentals[username] = []
            
        rentals[username].append(rental)
        cls.save_rentals(rentals)
    
    @classmethod
    def update_rental_status(cls, username, car_id, status, return_date=None, fine_amount=0):
        """Update rental status in the global rental database"""
        rentals = cls.load_rentals()
        
        if username not in rentals:
            print(f"No rentals found for user {username}")
            return False
            
        for rental in rentals[username]:
            if rental["car_id"] == car_id and rental["status"] == "active":
                rental["status"] = status
                if return_date:
                    rental["return_date"] = return_date
                if fine_amount > 0:
                    rental["fine_amount"] = fine_amount
                cls.save_rentals(rentals)
                return True
                
        return False
    
    @classmethod
    def view_active_rentals(cls):
        """Admin function to view all active rentals"""
        rentals = cls.load_rentals()
        
        active_count = 0
        print("\n=== ACTIVE RENTALS ===")
        
        for username, user_rentals in rentals.items():
            for rental in user_rentals:
                if rental["status"] == "active":
                    active_count += 1
                    car = Car.get_car_by_id(rental["car_id"])
                    car_info = f"{car.brand} {car.model}" if car else "Unknown Car"
                    
                    print(f"\nCustomer: {username}")
                    print(f"Car: {car_info} (ID: {rental['car_id']})")
                    print(f"Rental Period: {rental['start_date']} to {rental['end_date']}")
                    print(f"Total Cost: ${rental['total_cost']:.2f}")
        
        if active_count == 0:
            print("No active rentals found.")
    
    @classmethod
    def view_customer_rentals(cls):
        """Admin function to view all customers with their current rentals"""
        rentals = cls.load_rentals()
        
        if not rentals:
            print("No rental records found in the system.")
            return
        
        print("\n=== CUSTOMERS WITH RENTALS ===")
        for username, user_rentals in rentals.items():
            active_rentals = [r for r in user_rentals if r["status"] == "active"]
            completed_rentals = [r for r in user_rentals if r["status"] == "completed"]
            
            print(f"\nCustomer: {username}")
            print(f"Active Rentals: {len(active_rentals)}")
            print(f"Completed Rentals: {len(completed_rentals)}")
            
            if active_rentals:
                print("Current Rentals:")
                for rental in active_rentals:
                    car = Car.get_car_by_id(rental["car_id"])
                    car_info = f"{car.brand} {car.model}" if car else "Unknown Car"
                    print(f"  - {car_info} (ID: {rental['car_id']}) until {rental['end_date']}")
    
    @classmethod
    def view_customer_rental_history(cls, username):
        """Admin function to view rental history for a specific customer"""
        rentals = cls.load_rentals()
        
        if username not in rentals:
            print(f"No rental records found for customer '{username}'.")
            return
            
        user_rentals = rentals[username]
        
        print(f"\n=== RENTAL HISTORY FOR {username.upper()} ===")
        for rental in user_rentals:
            car = Car.get_car_by_id(rental["car_id"])
            car_info = f"{car.brand} {car.model}" if car else "Unknown Car"
            
            print(f"\nCar: {car_info} (ID: {rental['car_id']})")
            print(f"Period: {rental['start_date']} to {rental['end_date']} ({rental['days']} days)")
            print(f"Cost: ${rental['total_cost']:.2f}")
            print(f"Status: {rental['status'].capitalize()}")
            
            if rental['status'] == "completed":
                print(f"Return Date: {rental['return_date']}")
                if rental.get('fine_amount', 0) > 0:
                    print(f"Late Return Fine: ${rental['fine_amount']:.2f}")
    
    @classmethod
    def display_fine_policy(cls):
        """Display the rental fine policy to customers"""
        print("\n=== RENTAL POLICY ===")
        print("1. Cars can be rented on a daily basis")
        print("2. Payment is made at the time of booking")
        print("3. One customer can only rent one car at a time")
        print("4. Late returns will incur a fee of 150% of the daily rate for each day late")
        print("5. Early returns will not be refunded")
        print("6. All rentals must be returned in the same condition")
        print("="*45)
