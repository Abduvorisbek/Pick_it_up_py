from datetime import datetime, timedelta

from services.authentication import AuthenticationService
from services.order_service import OrderService
from models.shop import Shop
from models.restaurant import Restaurant
from models.product import Product
from models.meal import Meal
from models.promo_code import PromoCode


class PickItUp:
    def __init__(self):
        self.auth = AuthenticationService()
        self.order_service = OrderService()
        self.shops = [
            Shop("Tech Store", [
                Product("Wireless Mouse", 120000),
                Product("USB-C Cable", 45000),
                Product("Headphones", 250000),
            ]),
            Shop("Book House", [
                Product("Python Basics", 90000),
                Product("Notebook", 18000),
                Product("Pen Set", 25000),
            ]),
            Shop("Daily Market", [
                Product("Water 1L", 7000),
                Product("Chocolate", 15000),
                Product("Bread", 12000),
            ]),
        ]
        self.restaurants = [
            Restaurant("Osh Markazi", [
                Meal("Plov", 35000, "Uzbek food", 25),
                Meal("Shashlik", 18000, "Uzbek food", 20),
                Meal("Achichuk Salad", 12000, "Salad", 10),
            ]),
            Restaurant("Burger Point", [
                Meal("Classic Burger", 42000, "Fast food", 20),
                Meal("Cheeseburger", 48000, "Fast food", 25),
                Meal("French Fries", 20000, "Side dish", 12),
            ]),
            Restaurant("Pizza House", [
                Meal("Margherita Pizza", 65000, "Pizza", 30),
                Meal("Pepperoni Pizza", 78000, "Pizza", 35),
                Meal("Cola", 10000, "Drink", 2),
            ]),
        ]
        self.promocodes = [
            PromoCode("WELCOME10", 10, "10% off your order"),
            PromoCode("PICKIT20", 20, "20% off your order"),
        ]
        self.next_order_id = 1

    def start(self):
        while True:
            print("\n========== PICK IT UP ==========")
            print("1. Register")
            print("2. Customer Login")
            print("3. Admin Login")
            print("4. Exit")
            choice = input("Choose: ").strip()

            if choice == "1":
                self.register()
            elif choice == "2":
                customer = self.login()
                if customer:
                    self.main_menu(customer)
            elif choice == "3":
                admin = self.admin_login()
                if admin:
                    self.admin_panel(admin)
            elif choice == "4":
                print("Thanks for using Pick It Up. Goodbye!")
                break
            else:
                print("Invalid choice. Please choose from 1 to 4.")

    def register(self):
        print("\n--- Customer Registration ---")
        name = input("Your name: ").strip()
        username = input("Choose a username: ").strip()
        password = input("Choose a password: ").strip()
        if not name or not username or not password:
            print("All fields are required.")
        elif self.auth.register(name, username, password):
            print("Registration successful! You can now log in.")
        else:
            print("That username is already taken.")

    def login(self):
        print("\n--- Customer Login ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        customer = self.auth.login(username, password)
        if customer:
            print(f"Welcome back, {customer.name}!")
            return customer
        print("Incorrect username or password.")
        return None

    def admin_login(self):
        print("\n--- Admin Login ---")
        username = input("Admin username: ").strip()
        password = input("Admin password: ").strip()
        admin = self.auth.admin_login(username, password)
        if admin:
            print(f"Welcome, {admin.name}!")
            return admin
        print("Incorrect admin username or password.")
        return None

    def main_menu(self, customer):
        while True:
            print(f"\n========== MAIN MENU ({customer.name}) ==========")
            print("1. Shops")
            print("2. Restaurants")
            print("3. Orders")
            print("4. Support")
            print("5. Promo codes")
            print("6. Log out")
            choice = input("Choose: ").strip()
            if choice == "1":
                self.browse_places(customer, self.shops, "Shops")
            elif choice == "2":
                self.browse_places(customer, self.restaurants, "Restaurants")
            elif choice == "3":
                self.show_orders(customer)
            elif choice == "4":
                self.support(customer)
            elif choice == "5":
                self.promo_menu()
            elif choice == "6":
                print("You have been logged out.")
                break
            else:
                print("Invalid choice. Please choose from 1 to 6.")

    def browse_places(self, customer, places, heading):
        while True:
            print(f"\n--- {heading} ---")
            if not places:
                print("No places are currently available.")
            for index, place in enumerate(places, start=1):
                print(f"{index}. {place.name}")
            print("0. Back")
            choice = input("Choose a place: ").strip()
            if choice == "0":
                return
            if not choice.isdigit() or not 1 <= int(choice) <= len(places):
                print("Invalid choice.")
                continue
            self.shop_menu(customer, places[int(choice) - 1])

    def shop_menu(self, customer, place):
        while True:
            print(f"\n--- {place.name} ---")
            place.show_products()
            print("\n1. Add product to cart")
            print("2. View cart")
            print("3. Remove product from cart")
            print("4. Checkout")
            print("0. Back")
            choice = input("Choose: ").strip()

            if choice == "1":
                product_name = input("Enter product name: ").strip()
                product = place.find_product(product_name)
                if product:
                    quantity_text = input("Quantity: ").strip()
                    if quantity_text.isdigit() and int(quantity_text) > 0:
                        customer.cart.add(product, int(quantity_text))
                        print("Added to cart.")
                    else:
                        print("Quantity must be a positive whole number.")
                else:
                    print("Product not found.")
            elif choice == "2":
                customer.cart.show()
            elif choice == "3":
                product_name = input("Product name to remove: ").strip()
                if customer.cart.remove(product_name):
                    print("Product removed from cart.")
                else:
                    print("That product is not in your cart.")
            elif choice == "4":
                self.checkout(customer, place)
            elif choice == "0":
                return
            else:
                print("Invalid choice.")

    def checkout(self, customer, place):
        if customer.cart.is_empty():
            print("Your cart is empty.")
            return

        code = input("Promo code (press Enter to skip): ").strip().upper()
        promo = self.find_promo(code) if code else None
        if code and not promo:
            print("Invalid promo code. Checkout will continue without a discount.")

        preparation_minutes = self.order_service.estimate_preparation(customer.cart)
        print(f"\nEstimated preparation time: {preparation_minutes} minutes")
        print("1. Order now (ASAP)")
        print("2. Schedule for a specific time today")
        timing_choice = input("Choose: ").strip()

        scheduled_time = None
        if timing_choice == "2":
            while True:
                time_text = input(
                    "Enter ready time (example: 04:00 PM or 09:30 AM): "
                ).strip().upper()
                try:
                    requested_time = datetime.strptime(time_text, "%I:%M %p").time()
                    now = datetime.now()
                    scheduled_time = datetime.combine(now.date(), requested_time)
                    if scheduled_time <= now:
                        print("That time has already passed today. Enter a future time.")
                        scheduled_time = None
                        continue
                    earliest_ready = now + timedelta(minutes=preparation_minutes)
                    if scheduled_time < earliest_ready:
                        print(
                            "That time is too soon. Earliest ready time is "
                            f"{earliest_ready.strftime('%I:%M %p')}."
                        )
                        scheduled_time = None
                        continue
                    break
                except ValueError:
                    print("Invalid format. Use a time such as 04:00 PM or 09:30 AM.")
        elif timing_choice != "1":
            print("Invalid timing choice. Checkout cancelled.")
            return

        order = self.order_service.checkout(
            customer, place.name, self.next_order_id, promo, scheduled_time
        )
        if order:
            self.next_order_id += 1
            print(f"\nOrder #{order.order_id} placed successfully!")
            print(f"Final total: {order.total:,.0f} UZS")
            if order.order_type == "ASAP":
                print(
                    f"It should be ready in about {order.preparation_minutes} minutes, "
                    f"at {order.ready_at.strftime('%I:%M %p')}."
                )
            else:
                print(
                    "Your order is scheduled and should be ready at "
                    f"{order.ready_at.strftime('%I:%M %p')}."
                )

    def show_orders(self, customer):
        while True:
            active = [o for o in customer.orders if o.status == "Active"]
            old = [o for o in customer.orders if o.status != "Active"]
            print("\n--- Your Orders ---")
            print("\nACTIVE ORDERS:")
            if active:
                for order in active:
                    order.show()
            else:
                print("No active orders.")
            print("\nOLD ORDERS:")
            if old:
                for order in old:
                    order.show()
            else:
                print("No old orders.")
            print("\n1. Cancel an active order")
            print("0. Back")
            choice = input("Choose: ").strip()
            if choice == "0":
                return
            if choice == "1":
                order_id = input("Order ID to cancel: ").strip()
                if order_id.isdigit() and self.order_service.cancel(
                    customer, int(order_id)
                ):
                    print("Order cancelled.")
                else:
                    print("Active order not found.")
            else:
                print("Invalid choice.")

    def support(self, customer):
        print("\n--- Support ---")
        message = input("Describe your problem or feedback (blank to cancel): ").strip()
        if message:
            customer.reports.append(message)
            print("Your report has been submitted. Thank you!")
        else:
            print("Report cancelled.")

    def promo_menu(self):
        print("\n--- Promo Codes ---")
        for promo in self.promocodes:
            print(f"{promo.code} - {promo.discount}% off ({promo.description})")
        print("Enter a promo code during checkout to use it.")
        input("Press Enter to return...")

    def find_promo(self, code):
        for promo in self.promocodes:
            if promo.code == code:
                return promo
        return None

    # ---------------- ADMIN PANEL ----------------

    def admin_panel(self, admin):
        while True:
            print(f"\n========== ADMIN PANEL ({admin.name}) ==========")
            print("1. Manage Shops")
            print("2. Manage Restaurants")
            print("3. Manage Products and Meals")
            print("4. Manage Orders")
            print("5. View Customers")
            print("6. View Support Reports")
            print("7. Manage Promo Codes")
            print("8. Statistics")
            print("9. Log out")
            choice = input("Choose: ").strip()

            if choice == "1":
                self.manage_places(self.shops, "shop")
            elif choice == "2":
                self.manage_places(self.restaurants, "restaurant")
            elif choice == "3":
                self.manage_products()
            elif choice == "4":
                self.manage_orders()
            elif choice == "5":
                self.view_customers()
            elif choice == "6":
                self.view_reports()
            elif choice == "7":
                self.manage_promocodes()
            elif choice == "8":
                self.show_statistics()
            elif choice == "9":
                print("Admin logged out.")
                break
            else:
                print("Invalid choice.")

    def manage_places(self, places, place_type):
        while True:
            print(f"\n--- Manage {place_type.title()}s ---")
            for i, place in enumerate(places, start=1):
                print(f"{i}. {place.name}")
            print("1. Add")
            print("2. Remove")
            print("0. Back")
            choice = input("Choose: ").strip()
            if choice == "0":
                return
            if choice == "1":
                name = input(f"New {place_type} name: ").strip()
                if not name:
                    print("Name cannot be empty.")
                elif any(p.name.lower() == name.lower() for p in places):
                    print("That name already exists.")
                else:
                    new_place = Restaurant(name) if place_type == "restaurant" else Shop(name)
                    places.append(new_place)
                    print(f"{place_type.title()} added.")
            elif choice == "2":
                name = input(f"Exact {place_type} name to remove: ").strip().lower()
                found = next((p for p in places if p.name.lower() == name), None)
                if found:
                    places.remove(found)
                    print(f"{place_type.title()} removed.")
                else:
                    print("Not found.")
            else:
                print("Invalid choice.")

    def manage_products(self):
        while True:
            places = [("Shop", p) for p in self.shops] + [
                ("Restaurant", p) for p in self.restaurants
            ]
            print("\n--- Select a place ---")
            for i, (kind, place) in enumerate(places, start=1):
                print(f"{i}. {kind}: {place.name}")
            print("0. Back")
            choice = input("Choose: ").strip()
            if choice == "0":
                return
            if not choice.isdigit() or not 1 <= int(choice) <= len(places):
                print("Invalid choice.")
                continue

            kind, place = places[int(choice) - 1]
            while True:
                print(f"\n--- Products: {place.name} ---")
                place.show_products()
                print("1. Add product")
                print("2. Change product price")
                print("3. Remove product")
                print("0. Back")
                action = input("Choose: ").strip()
                if action == "0":
                    break
                if action == "1":
                    name = input("Product name: ").strip()
                    price_text = input("Price in UZS: ").strip()
                    if not name or not price_text.replace(".", "", 1).isdigit():
                        print("Enter a name and valid positive price.")
                        continue
                    price = float(price_text)
                    if price <= 0 or place.find_product(name):
                        print("Price must be positive and product name must be unique here.")
                        continue
                    if kind == "Restaurant":
                        category = input("Meal category: ").strip() or "Other"
                        prep_text = input("Preparation minutes (default 15): ").strip()
                        prep = int(prep_text) if prep_text.isdigit() and int(prep_text) > 0 else 15
                        place.products.append(Meal(name, price, category, prep))
                    else:
                        prep_text = input("Preparation minutes (default 10): ").strip()
                        prep = int(prep_text) if prep_text.isdigit() and int(prep_text) > 0 else 10
                        place.products.append(Product(name, price, prep))
                    print("Product added.")
                elif action == "2":
                    name = input("Product name: ").strip()
                    product = place.find_product(name)
                    if not product:
                        print("Product not found.")
                        continue
                    price_text = input("New price in UZS: ").strip()
                    if price_text.replace(".", "", 1).isdigit() and float(price_text) > 0:
                        product.price = float(price_text)
                        print("Price updated.")
                    else:
                        print("Enter a valid positive price.")
                elif action == "3":
                    name = input("Product name to remove: ").strip()
                    product = place.find_product(name)
                    if product:
                        place.products.remove(product)
                        print("Product removed.")
                    else:
                        print("Product not found.")
                else:
                    print("Invalid choice.")

    def all_orders(self):
        orders = []
        for customer in self.auth.accounts.values():
            orders.extend(customer.orders)
        return orders

    def manage_orders(self):
        orders = self.all_orders()
        print("\n--- All Customer Orders ---")
        if not orders:
            print("No orders yet.")
            return
        for order in orders:
            print(f"Customer: {order.customer_username}")
            order.show()
        order_id_text = input(
            "Enter an active order ID to cancel (or press Enter to go back): "
        ).strip()
        if order_id_text:
            if order_id_text.isdigit():
                for customer in self.auth.accounts.values():
                    if self.order_service.cancel(customer, int(order_id_text)):
                        print("Order cancelled by admin.")
                        return
            print("Active order not found.")

    def view_customers(self):
        print("\n--- Registered Customers ---")
        if not self.auth.accounts:
            print("No registered customers.")
        for customer in self.auth.accounts.values():
            print(
                f"{customer.name} | Username: {customer.username} | "
                f"Orders: {len(customer.orders)}"
            )

    def view_reports(self):
        print("\n--- Customer Support Reports ---")
        found = False
        for customer in self.auth.accounts.values():
            for report in customer.reports:
                found = True
                print(f"{customer.username}: {report}")
        if not found:
            print("No support reports.")

    def manage_promocodes(self):
        while True:
            print("\n--- Promo Codes ---")
            for promo in self.promocodes:
                print(f"{promo.code}: {promo.discount}% - {promo.description}")
            print("1. Add promo code")
            print("2. Remove promo code")
            print("0. Back")
            choice = input("Choose: ").strip()
            if choice == "0":
                return
            if choice == "1":
                code = input("New code: ").strip().upper()
                discount_text = input("Discount percentage (1-100): ").strip()
                description = input("Description: ").strip()
                if (not code or self.find_promo(code) or
                    not discount_text.isdigit() or
                    not 1 <= int(discount_text) <= 100):
                    print("Invalid or duplicate code/discount.")
                else:
                    self.promocodes.append(
                        PromoCode(code, int(discount_text), description or "Discount")
                    )
                    print("Promo code added.")
            elif choice == "2":
                code = input("Code to remove: ").strip().upper()
                promo = self.find_promo(code)
                if promo:
                    self.promocodes.remove(promo)
                    print("Promo code removed.")
                else:
                    print("Promo code not found.")
            else:
                print("Invalid choice.")

    def show_statistics(self):
        customers = list(self.auth.accounts.values())
        orders = self.all_orders()
        active = sum(1 for order in orders if order.status == "Active")
        cancelled = sum(1 for order in orders if order.status == "Cancelled")
        revenue = sum(
            order.total for order in orders if order.status != "Cancelled"
        )
        print("\n--- Platform Statistics ---")
        print(f"Customers: {len(customers)}")
        print(f"Shops: {len(self.shops)}")
        print(f"Restaurants: {len(self.restaurants)}")
        print(f"Total orders: {len(orders)}")
        print(f"Active orders: {active}")
        print(f"Cancelled orders: {cancelled}")
        print(f"Recorded revenue: {revenue:,.0f} UZS")


if __name__ == "__main__":
    app = PickItUp()
    app.start()
