import json
import os
from datetime import datetime
from models.car import Car

class Customer:
    def __init__(self, username, password, first_name, last_name, balance=0.0, rentals=None):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.balance = float(balance)
        self.rentals = rentals if rentals else []
        
    def __add__(self, amount):
        """Operator overloading for adding balance"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
        print(f"Balance updated. New balance: ${self.balance:.2f}")
        return self
        
    def rent_car(self, car_id, start_date, end_date):
        """Rent a car if it's available and user has sufficient balance"""
        from models.rental import RentalManager
        
        # Check if user already has an active rental
        for rental in self.rentals:
            if rental.get("status") == "active":
                print("You cannot reserve more than one car at a time.")
                return False
        
        # Get the car
        car = Car.get_car_by_id(car_id)
        if not car:
            print(f"Car with ID {car_id} not found.")
            return False
            
        if not car.available:
            print(f"Car with ID {car_id} is not available for rent.")
            return False
            
        # Calculate rental cost
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days = (end - start).days + 1
            
            if days <= 0:
                print("End date must be after start date.")
                return False
                
            total_cost = days * car.rental_price
            
            if self.balance < total_cost:
                print(f"Insufficient balance. Required: ${total_cost:.2f}, Available: ${self.balance:.2f}")
                return False
                
            # Deduct balance and update car availability
            self.balance -= total_cost
            Car.update_car_availability(car_id, False)
            
            # Create rental record
            rental = {
                "car_id": car_id,
                "start_date": start_date,
                "end_date": end_date,
                "days": days,
                "total_cost": total_cost,
                "status": "active",
                "return_date": None,
                "fine_amount": 0
            }
            
            self.rentals.append(rental)
            
            # Update global rental records
            RentalManager.add_rental(self.username, rental)
            
            # Save customer data
            self._update_customer_data()
            
            print(f"Car rented successfully for ${total_cost:.2f}. Enjoy your trip!")
            return True
            
        except ValueError as e:
            print(f"Error processing dates: {e}")
            return False
    
    def return_car(self, car_id, return_date):
        """Return a rented car and calculate any late fees"""
        from models.rental import RentalManager
        
        # Find the active rental for this car
        active_rental = None
        rental_index = -1
        
        for i, rental in enumerate(self.rentals):
            if rental.get("car_id") == car_id and rental.get("status") == "active":
                active_rental = rental
                rental_index = i
                break
                
        if not active_rental:
            print(f"You don't have an active rental for car ID {car_id}.")
            return False
            
        try:
            # Parse dates
            end_date = datetime.strptime(active_rental["end_date"], "%Y-%m-%d")
            actual_return = datetime.strptime(return_date, "%Y-%m-%d")
            
            # Calculate any fine for late return
            fine = 0
            if actual_return > end_date:
                days_late = (actual_return - end_date).days
                car = Car.get_car_by_id(car_id)
                fine = days_late * (car.rental_price * 1.5)  # 150% of regular price as fine
                print(f"Late return by {days_late} days. Fine: ${fine:.2f}")
                
                # Update customer balance
                self.balance -= fine
                
            # Update rental record
            self.rentals[rental_index]["status"] = "completed"
            self.rentals[rental_index]["return_date"] = return_date
            self.rentals[rental_index]["fine_amount"] = fine
            
            # Update car availability
            Car.update_car_availability(car_id, True)
            
            # Update global rental records
            RentalManager.update_rental_status(self.username, car_id, "completed", return_date, fine)
            
            # Save customer data
            self._update_customer_data()
            
            print(f"Car returned successfully. Thank you!")
            if fine > 0:
                print(f"Late fee of ${fine:.2f} has been charged to your account.")
            return True
            
        except ValueError as e:
            print(f"Error processing return date: {e}")
            return False
    
    def view_rental_history(self):
        """Display the rental history for this customer"""
        if not self.rentals:
            print("You don't have any rental history.")
            return
            
        print("\n=== YOUR RENTAL HISTORY ===")
        for rental in self.rentals:
            car = Car.get_car_by_id(rental["car_id"])
            car_info = f"{car.brand} {car.model}" if car else "Unknown Car"
            
            print(f"\nCar: {car_info} (ID: {rental['car_id']})")
            print(f"Period: {rental['start_date']} to {rental['end_date']} ({rental['days']} days)")
            print(f"Cost: ${rental['total_cost']:.2f}")
            print(f"Status: {rental['status'].capitalize()}")
            
            if rental['status'] == "completed":
                print(f"Return Date: {rental['return_date']}")
                if rental['fine_amount'] > 0:
                    print(f"Late Return Fine: ${rental['fine_amount']:.2f}")
    
    def view_profile(self):
        """Display customer profile information"""
        print("\n=== YOUR PROFILE ===")
        print(f"Name: {self.first_name} {self.last_name}")
        print(f"Username: {self.username}")
        print(f"Current Balance: ${self.balance:.2f}")
        
        # Count active rentals
        active_rentals = sum(1 for rental in self.rentals if rental.get("status") == "active")
        if active_rentals > 0:
            print(f"Active Rentals: {active_rentals}")
        else:
            print("You have no active rentals.")
    
    def _update_customer_data(self):
        """Update customer data in the users.json file"""
        if not os.path.exists("data"):
            os.makedirs("data")
        
        try:
            if os.path.exists("data/users.json"):
                with open("data/users.json", "r") as f:
                    users = json.load(f)
            else:
                users = []
                
            # Find and update user
            for user in users:
                if user["username"] == self.username:
                    user["balance"] = self.balance
                    user["rentals"] = self.rentals
                    break
            
            with open("data/users.json", "w") as f:
                json.dump(users, f, indent=4)
                
        except Exception as e:
            print(f"Error updating customer data: {e}")
