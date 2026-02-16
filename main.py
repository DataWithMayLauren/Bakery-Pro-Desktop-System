import customtkinter as ctk
import pandas as pd
import os
import json
import shutil
from datetime import datetime
import tkinter.messagebox as mbox
from PIL import Image

class BakeryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- BRAND & THEME ---
        self.bakery_name = "MayLauren's Artisan Bakeshop"
        self.version = "Enterprise v3.0 (Stable + Pre-Order)"
        self.header_blue = "#1565C0"    
        self.bg_light_blue = "#E3F2FD"  
        self.primary_pink = "#D47088"   
        self.accent_navy = "#0D47A1"    
        
        self.font_main = ("Segoe UI", 14)           
        self.font_button = ("Segoe UI", 13, "bold") 
        self.font_header = ("Segoe UI", 20, "bold") 
        self.font_title = ("Segoe UI", 32, "bold")  
        
        # --- IMAGE LOADING ---
        self.logo_path = "logo.png" 
        self.logo_img = None
        try:
            if os.path.exists(self.logo_path):
                raw_img = Image.open(self.logo_path)
                self.logo_img = ctk.CTkImage(light_image=raw_img, dark_image=raw_img, size=(70, 70))
        except: pass

        self.title(f"{self.bakery_name} | {self.version}")
        self.geometry("1400x900") 
        self.configure(fg_color=self.bg_light_blue)

        self.recipe_file = "recipes.json"
        self.preorder_file = "pre_orders.csv"
        
        self.init_csv_files()
        self.run_auto_backup() # Run backup on startup
        self.setup_ui()

    def init_csv_files(self):
        files = {
            "bakery_inventory.csv": ["Product", "Price", "Stock"],
            "sales_records.csv": ["Date", "Product", "Qty", "Total"],
            "ingredients.csv": ["Ingredient", "Qty", "Cost"],
            "pre_orders.csv": ["Date", "Item", "Qty", "Total"] # Ledger Format: Date, Item, Qty, Total
        }
        for file, cols in files.items():
            if not os.path.exists(file):
                pd.DataFrame(columns=cols).to_csv(file, index=False)
        if not os.path.exists(self.recipe_file):
            with open(self.recipe_file, 'w') as f: json.dump({}, f)

    def run_auto_backup(self):
        """Creates a timestamped backup of all database files"""
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        current_backup_path = os.path.join(backup_dir, timestamp)
        os.makedirs(current_backup_path)

        files_to_back = ["bakery_inventory.csv", "sales_records.csv", "ingredients.csv", "pre_orders.csv", "recipes.json"]
        for f in files_to_back:
            if os.path.exists(f):
                shutil.copy(f, os.path.join(current_backup_path, f))

    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color=self.header_blue, height=100, corner_radius=0)
        header.pack(fill="x", side="top")
        h_center = ctk.CTkFrame(header, fg_color="transparent")
        h_center.pack(expand=True)
        if self.logo_img:
            ctk.CTkLabel(h_center, image=self.logo_img, text="").pack(side="left", padx=15)
        else:
            ctk.CTkLabel(h_center, text="🥖", font=("Segoe UI", 45)).pack(side="left", padx=15)
        ctk.CTkLabel(h_center, text=self.bakery_name.upper(), font=self.font_title, text_color="white").pack(side="left")

        nav_bar = ctk.CTkFrame(self, fg_color="white", height=100, corner_radius=15)
        nav_bar.pack(side="bottom", fill="x", padx=20, pady=20)
        btn_container = ctk.CTkFrame(nav_bar, fg_color="transparent")
        btn_container.pack(expand=True)

        btns = [
            ("+ Product", self.primary_pink, self.open_add_product),
            ("📅 + Pre-Order", self.primary_pink, self.open_pre_order_window), # NEW FEATURE
            ("🍳 Recipe", self.primary_pink, self.open_recipe_manager),
            ("+ Material", "#5C6BC0", self.open_add_ingredient),
            ("💸 Admin", "#E57373", self.open_admin_expense),
            ("💹 Costing", "#4CAF50", self.calculate_product_costing),
            ("📜 Ledger", "#5D4037", self.generate_monthly_report),
            ("💾 Backup", "#78909C", lambda: [self.run_auto_backup(), mbox.showinfo("Backup", "Manual Backup Created!")])
        ]
        for i, (t, c, cmd) in enumerate(btns):
            ctk.CTkButton(btn_container, text=t, fg_color=c, text_color="white", 
                          font=self.font_button, width=125, height=45, command=cmd).grid(row=0, column=i, padx=5)

        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(pady=20, fill="x", padx=20)
        self.top_frame.grid_columnconfigure((0, 4), weight=1) 

        self.main_grid = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        self.main_grid.pack(expand=True, fill="both", padx=20, pady=10)
        self.col_inv = self.create_column(self.main_grid, "MENU & STOCK", 0)
        self.col_sales = self.create_column(self.main_grid, "POINT OF SALE", 1)
        self.col_restock = self.create_column(self.main_grid, "RAW MATERIALS", 2)
        self.refresh_all_data()

    def create_column(self, master, title, col):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.grid(row=0, column=col, sticky="nsew", padx=15, pady=15)
        master.grid_columnconfigure(col, weight=1)
        master.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=title, font=self.font_header, text_color=self.accent_navy).pack(pady=10)
        scroll = ctk.CTkScrollableFrame(frame, fg_color="#F0F7FF", corner_radius=15)
        scroll.pack(fill="both", expand=True)
        return scroll

    def create_stat_card(self, master, title, val, text_c, col_pos):
        card = ctk.CTkFrame(master, fg_color="white", corner_radius=20, border_width=2, border_color="#BBD6F2")
        card.grid(row=0, column=col_pos, padx=15, sticky="nsew")
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 16), text_color="gray").pack(pady=(20, 0), padx=30)
        ctk.CTkLabel(card, text=val, font=("Segoe UI", 38, "bold"), text_color=text_c).pack(pady=(5, 20), padx=30)
        return card

    # ==========================================
    # NEW FEATURE: PRE-ORDER LOGIC
    # ==========================================
    def open_pre_order_window(self):
        pop = ctk.CTkToplevel(self); pop.geometry("400x500"); pop.attributes("-topmost", True)
        pop.title("Add Pre-Order")
        ctk.CTkLabel(pop, text="Log New Reservation", font=self.font_header).pack(pady=20)
        
        cust = ctk.CTkEntry(pop, placeholder_text="Customer Name", width=250); cust.pack(pady=10)
        
        df_p = pd.read_csv("bakery_inventory.csv")
        prod_list = df_p["Product"].tolist() if not df_p.empty else ["No Products"]
        item_opt = ctk.CTkOptionMenu(pop, values=prod_list, width=250, fg_color=self.header_blue); item_opt.pack(pady=10)
        
        qty = ctk.CTkEntry(pop, placeholder_text="Quantity", width=250); qty.pack(pady=10)
        pickup_date = ctk.CTkEntry(pop, placeholder_text="Pickup Date (YYYY-MM-DD)", width=250)
        pickup_date.insert(0, datetime.now().strftime("%Y-%m-%d")); pickup_date.pack(pady=10)

        def save():
            # Ledger Format: Date, Item, Qty, Total
            new_entry = pd.DataFrame([{
                "Date": pickup_date.get(),
                "Item": f"RESERVE: {cust.get()} ({item_opt.get()})",
                "Qty": qty.get(),
                "Total": "PENDING"
            }])
            new_entry.to_csv(self.preorder_file, mode='a', index=False, header=not os.path.exists(self.preorder_file))
            mbox.showinfo("Success", "Pre-order added to Ledger!")
            pop.destroy(); self.refresh_all_data()

        ctk.CTkButton(pop, text="Confirm Reservation", fg_color=self.primary_pink, command=save, height=45).pack(pady=30)

    # ==========================================
    # REFRESH LOGIC (INCLUDES PRE-ORDER DISPLAY)
    # ==========================================
    def refresh_all_data(self):
        self.refresh_top_stats()
        self.refresh_inventory_list()
        self.setup_sales_section()
        self.refresh_ingredients_list()
        self.display_preorders()

    def display_preorders(self):
        """Displays recent pre-orders safely with fixed labels"""
        if os.path.exists(self.preorder_file):
            try:
                df_pre = pd.read_csv(self.preorder_file)
                if not df_pre.empty:
                    # Show only the last 8 orders to keep it clean
                    recent_pre = df_pre.tail(8) 
                    for _, r in recent_pre.iterrows():
                        row = ctk.CTkFrame(self.col_sales, fg_color="#FFF9C4", corner_radius=8)
                        row.pack(fill="x", pady=2, padx=10)
                        
                        d = r.get('Date', 'N/A')
                        i = r.get('Item', 'Unknown')
                        q = r.get('Qty', '0')
                        
                        # Added a small 'Print' icon next to each one for visual style
                        ctk.CTkLabel(row, text=f"📅 {d} | {i} (x{q})", font=("Segoe UI", 11, "bold")).pack(pady=5, padx=10, side="left")
                else:
                    ctk.CTkLabel(self.col_sales, text="(No pending orders)", font=self.font_main, text_color="gray").pack()
            except Exception as e:
                print(f"Pre-order error: {e}")

    # [REMAINING ORIGINAL STABLE LOGIC]
    def calculate_product_costing(self):
        try:
            df_i = pd.read_csv("ingredients.csv"); df_p = pd.read_csv("bakery_inventory.csv")
            with open(self.recipe_file, 'r') as recipe_data: recs = json.load(recipe_data)
            def get_num(val):
                n = ''.join(c for c in str(val) if c.isdigit() or c == '.')
                return float(n) if n and float(n) > 0 else 1.0
            ing_map = {str(r['Ingredient']): float(r['Cost']) / get_num(r['Qty']) for _, r in df_i.iterrows()}
            prod_price_map = {str(r['Product']): float(r['Price']) for _, r in df_p.iterrows()}
            path = "Detailed_Costing_Analysis.txt"
            with open(path, "w", encoding="utf-8") as out:
                out.write(f"{self.bakery_name.upper()} - COSTING ANALYSIS\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n" + "="*60 + "\n\n")
                for prod, ings in recs.items():
                    out.write(f"PRODUCT: {prod.upper()}\n" + "-"*30)
                    unit_total = sum(amt * ing_map.get(ing, 0) for ing, amt in ings.items())
                    sell = prod_price_map.get(prod, 0); profit = sell - unit_total; margin = (profit / sell * 100) if sell > 0 else 0
                    out.write(f"\nPROD COST: ₱{unit_total:>8.2f} | SELL PRICE: ₱{sell:>8.2f}\nPROFIT:    ₱{profit:>8.2f} | MARGIN:      {margin:>8.2f}%\nSTATUS: {'[✓] HEALTHY' if margin >= 30 else '[!] LOW MARGIN'}\n\n" + "="*60 + "\n\n")
            os.startfile(path)
        except Exception as e: mbox.showerror("Costing Error", f"Error: {e}")

    def generate_monthly_report(self):
        """Generates Ledger using 'Item' column instead of 'Product' to fix the error"""
        try:
            df_s = pd.read_csv("sales_records.csv")
            df_i = pd.read_csv("ingredients.csv")
            df_s['Date'] = pd.to_datetime(df_s['Date'], errors='coerce')
            now = datetime.now()
            
            sales_cur = df_s[df_s['Date'].dt.month == now.month]
            total_rev = sales_cur['Total'].sum()
            total_mat = pd.to_numeric(df_i[~df_i['Ingredient'].str.contains(r"\[ADMIN\]", na=False)]['Cost'], errors='coerce').sum()
            total_adm = pd.to_numeric(df_i[df_i['Ingredient'].str.contains(r"\[ADMIN\]", na=False)]['Cost'], errors='coerce').sum()
            
            fname = f"Ledger_{now.strftime('%B_%Y')}.txt"
            with open(fname, "w", encoding="utf-8") as report:
                report.write(f"{self.bakery_name.upper()}\nOFFICIAL LEDGER - {now.strftime('%B %Y')}\n" + "="*60 + "\n")
                report.write(f"{'Date':<12} | {'Item':<20} | {'Qty':<6} | {'Total':<12}\n" + "-"*60 + "\n")
                
                for _, r in sales_cur.iterrows():
                    # This fallback looks for 'Item' or 'Product' to prevent crashes
                    item_name = r.get('Item', r.get('Product', 'Unknown'))
                    report.write(f"{r['Date'].strftime('%Y-%m-%d'):<12} | {str(item_name)[:19]:<20} | {r['Qty']:<6} | ₱{r['Total']:<12,.2f}\n")
                
                report.write("\n" + "="*60 + "\nSUMMARY:\n" + "-"*30 + "\n")
                report.write(f"Total Revenue:         ₱{total_rev:>15,.2f}\nTotal Material Costs: (₱{total_mat:>14,.2f})\nTotal Admin Expenses: (₱{total_adm:>14,.2f})\n" + "-"*30 + f"\nNET PROFIT:            ₱{(total_rev - total_mat - total_adm):>15,.2f}\n")
            
            os.startfile(fname)
        except Exception as e: 
            mbox.showerror("Ledger Error", f"Problem with column names or data: {e}")

    def setup_sales_section(self):
        """POS Section - Clears and rebuilds the middle column with Print and List features"""
        # 1. Clear the column to prevent double-headers
        for widget in self.col_sales.winfo_children(): 
            widget.destroy()
            
        # 2. NEW ORDER BOX (Point of Sale)
        box = ctk.CTkFrame(self.col_sales, fg_color="white", corner_radius=15)
        box.pack(pady=15, padx=15, fill="x")
        ctk.CTkLabel(box, text="New Order", font=self.font_header).pack(pady=10)
        
        # Load inventory for dropdown
        df_p = pd.read_csv("bakery_inventory.csv")
        prod_list = df_p["Product"].tolist() if not df_p.empty else ["No Items"]
        
        self.sale_opt = ctk.CTkOptionMenu(box, values=prod_list, font=self.font_main, fg_color=self.header_blue)
        self.sale_opt.pack(pady=5)
        
        self.sale_qty = ctk.CTkEntry(box, placeholder_text="Enter Quantity", font=self.font_main, height=35)
        self.sale_qty.pack(pady=5, padx=20)
        
        ctk.CTkButton(box, text="FINALIZE SALE", fg_color=self.primary_pink, font=self.font_button, height=40, command=self.process_order).pack(pady=15)

        # 3. PRODUCTION PRINT BUTTON (New Addition)
        # This button triggers the date-range filter we created
        print_btn = ctk.CTkButton(self.col_sales, 
                                 text="🖨️ PRINT PRODUCTION SHEET", 
                                 fg_color="#4CAF50", 
                                 text_color="white",
                                 font=self.font_button, 
                                 height=45,
                                 command=self.print_preorders_range)
        print_btn.pack(pady=10, padx=20, fill="x")

        # 4. PRE-ORDER LIST SECTION
        ctk.CTkLabel(self.col_sales, text="PENDING PRE-ORDERS", font=self.font_header, text_color=self.accent_navy).pack(pady=(15, 5))
        
        # Internal scroll frame for the list to keep it neat
        self.preorder_list_frame = ctk.CTkFrame(self.col_sales, fg_color="transparent")
        self.preorder_list_frame.pack(fill="both", expand=True)
        
        self.display_preorders()

    def setup_sales_section(self):
        """POS Section with Welcome Msg, Customer Name, and Print Feature"""
        for widget in self.col_sales.winfo_children(): 
            widget.destroy()
            
        # 1. WELCOME HEADER
        welcome_frame = ctk.CTkFrame(self.col_sales, fg_color="transparent")
        welcome_frame.pack(pady=(10, 0))
        ctk.CTkLabel(welcome_frame, text=f"Welcome back to {self.bakery_name}!", 
                     font=("Segoe UI", 16, "bold"), text_color=self.accent_navy).pack()
        ctk.CTkLabel(welcome_frame, text=datetime.now().strftime("%A, %B %d"), 
                     font=("Segoe UI", 12), text_color="gray").pack()

        # 2. NEW ORDER BOX
        box = ctk.CTkFrame(self.col_sales, fg_color="white", corner_radius=15)
        box.pack(pady=15, padx=15, fill="x")
        ctk.CTkLabel(box, text="Create New Order", font=self.font_header).pack(pady=10)
        
        # --- NEW: CUSTOMER NAME FIELD ---
        self.cust_name_ent = ctk.CTkEntry(box, placeholder_text="Customer Name", 
                                          font=self.font_main, height=35)
        self.cust_name_ent.pack(pady=5, padx=20, fill="x")
        
        # Product Dropdown
        try:
            df_p = pd.read_csv("bakery_inventory.csv")
            prod_list = df_p["Product"].tolist() if not df_p.empty else ["No Items"]
        except:
            prod_list = ["No Items"]
        
        self.sale_opt = ctk.CTkOptionMenu(box, values=prod_list, font=self.font_main, fg_color=self.header_blue)
        self.sale_opt.pack(pady=5)
        
        self.sale_qty = ctk.CTkEntry(box, placeholder_text="Quantity", font=self.font_main, height=35)
        self.sale_qty.pack(pady=5, padx=20)
        
        ctk.CTkButton(box, text="FINALIZE SALE", fg_color=self.primary_pink, 
                      font=self.font_button, height=45, command=self.process_order).pack(pady=15)

        # 3. PRINT BUTTON
        ctk.CTkButton(self.col_sales, text="🖨️ PRINT PRODUCTION SHEET", 
                      fg_color="#4CAF50", text_color="white", font=self.font_button, 
                      height=45, command=self.print_preorders_range).pack(pady=10, padx=20, fill="x")

        # 4. PRE-ORDER LIST
        ctk.CTkLabel(self.col_sales, text="PENDING PRE-ORDERS", font=self.font_header, text_color=self.accent_navy).pack(pady=(15, 5))
        self.preorder_list_frame = ctk.CTkFrame(self.col_sales, fg_color="transparent")
        self.preorder_list_frame.pack(fill="both", expand=True)
        self.display_preorders()

    def display_preorders(self):
        """Displays the list of pre-orders safely"""
        for widget in self.preorder_list_frame.winfo_children():
            widget.destroy()
        if os.path.exists(self.preorder_file):
            try:
                df_pre = pd.read_csv(self.preorder_file)
                if not df_pre.empty:
                    for _, r in df_pre.tail(10).iterrows():
                        row = ctk.CTkFrame(self.preorder_list_frame, fg_color="#FFF9C4", corner_radius=8)
                        row.pack(fill="x", pady=2, padx=10)
                        d, i, q = r.get('Date', 'N/A'), r.get('Item', 'Unknown'), r.get('Qty', '0')
                        ctk.CTkLabel(row, text=f"📅 {d} | {i} (x{q})", font=("Segoe UI", 11, "bold"), text_color="#5D4037").pack(pady=8, padx=10, side="left")
                else:
                    ctk.CTkLabel(self.preorder_list_frame, text="(No pending orders)", font=self.font_main, text_color="gray").pack(pady=20)
            except: pass

    def print_preorders_range(self):
        """Pop-up window for Date Range printing"""
        pop = ctk.CTkToplevel(self)
        pop.geometry("400x400")
        pop.title("Print Production Sheet")
        pop.attributes("-topmost", True)
        ctk.CTkLabel(pop, text="Filter Production Date", font=self.font_header).pack(pady=20)
        
        s_ent = ctk.CTkEntry(pop, placeholder_text="Start (YYYY-MM-DD)", width=250)
        s_ent.pack(pady=5); s_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        e_ent = ctk.CTkEntry(pop, placeholder_text="End (YYYY-MM-DD)", width=250)
        e_ent.pack(pady=5); e_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))

        def execute_print():
            try:
                sd, ed = s_ent.get(), e_ent.get()
                df = pd.read_csv(self.preorder_file)
                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
                filt = df.loc[(df['Date'] >= sd) & (df['Date'] <= ed)]
                if filt.empty: return mbox.showwarning("Empty", "No orders in range")
                
                fname = f"Production_{sd}.txt"
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(f"PRODUCTION LIST: {sd} to {ed}\n" + "="*40 + "\n")
                    for _, r in filt.iterrows():
                        f.write(f"{r['Date']} | {str(r.get('Item'))[:20]:<20} | x{r.get('Qty')}\n")
                os.startfile(fname, "print")
                pop.destroy()
            except Exception as ex: mbox.showerror("Error", str(ex))

        ctk.CTkButton(pop, text="CONFIRM PRINT", command=execute_print, fg_color=self.header_blue).pack(pady=20)

    def refresh_top_stats(self):
        for widget in self.top_frame.winfo_children(): 
            if isinstance(widget, ctk.CTkFrame): widget.destroy()
        try:
            # Load Data
            df_s = pd.read_csv("sales_records.csv")
            df_i = pd.read_csv("ingredients.csv")
            
            # Convert Dates
            df_s['Date'] = pd.to_datetime(df_s['Date'], errors='coerce')
            now = datetime.now()
            
            # Calculations
            today_sales = df_s[df_s['Date'].dt.date == now.date()]['Total'].sum()
            month_sales = df_s[df_s['Date'].dt.month == now.month]['Total'].sum()
            
            # Total Expenses (Materials + Admin)
            month_exp = pd.to_numeric(df_i['Cost'], errors='coerce').sum()
            
            # Profit
            month_profit = month_sales - month_exp

            # Display Cards
            self.create_stat_card(self.top_frame, "Today's Sales", f"₱{today_sales:,.2f}", "#2E7D32", 0)
            self.create_stat_card(self.top_frame, "Month's Sales", f"₱{month_sales:,.2f}", self.header_blue, 1)
            self.create_stat_card(self.top_frame, "Month's Expenses", f"₱{month_exp:,.2f}", "#C62828", 2)
            self.create_stat_card(self.top_frame, "Month's Profit", f"₱{month_profit:,.2f}", "#D47088", 3)
            
        except Exception as e:
            print(f"Stats Error: {e}")

    def refresh_inventory_list(self):
        for widget in self.col_inv.winfo_children(): widget.destroy()
        df = pd.read_csv("bakery_inventory.csv")
        for _, r in df.iterrows():
            # --- RESTORED LOW STOCK LOGIC ---
            is_low = int(r['Stock']) < 10
            row = ctk.CTkFrame(self.col_inv, fg_color=("#FFF5F5" if is_low else "white"), corner_radius=10, border_width=(1 if is_low else 0), border_color="red")
            row.pack(fill="x", pady=4, padx=5)
            ctk.CTkLabel(row, text=f"{r['Product']} | ₱{r['Price']} (Stock: {r['Stock']})" + (" ⚠️" if is_low else ""), font=("Segoe UI", 14, ("bold" if is_low else "normal")), text_color=("#C62828" if is_low else "black")).pack(side="left", padx=15, pady=8)
            # --------------------------------
            ctk.CTkButton(row, text="🗑️", width=35, height=30, fg_color="#FFEBEE", text_color="red", command=lambda n=r['Product']: self.delete_product(n)).pack(side="right", padx=10)

    def refresh_ingredients_list(self):
        """Refreshes the Raw Materials column with Qty and Low Stock Alerts"""
        for widget in self.col_restock.winfo_children(): 
            widget.destroy()
            
        df = pd.read_csv("ingredients.csv")
        for _, r in df.iterrows():
            if "[ADMIN]" in str(r['Ingredient']): continue
            
            # --- STOCK LOGIC ---
            try: 
                val_str = ''.join(c for c in str(r['Qty']) if c.isdigit() or c == '-')
                val = float(val_str) if val_str else 0
            except: val = 0
                
            is_low = val < 10 
            
            # --- UI ROW ---
            row = ctk.CTkFrame(self.col_restock, fg_color=("#FFF5F5" if is_low else "white"), corner_radius=10)
            row.pack(fill="x", pady=4, padx=5)
            
            # Labels Name and Qty (Fixed the missing Qty section)
            ctk.CTkLabel(row, text=f"{r['Ingredient']}: {r['Qty']}" + (" 🚨" if is_low else ""), 
                         font=("Segoe UI", 14, ("bold" if is_low else "normal")), 
                         text_color=("#C62828" if is_low else "black")).pack(side="left", padx=15, pady=8)
            
            ctk.CTkButton(row, text="🗑️", width=35, height=30, fg_color="#FFEBEE", text_color="red", 
                          command=lambda n=r['Ingredient']: self.delete_ing(n)).pack(side="right", padx=10)

    def process_order(self):
        try:
            df_p = pd.read_csv("bakery_inventory.csv"); df_i = pd.read_csv("ingredients.csv")
            prod, qty = self.sale_opt.get(), int(self.sale_qty.get()); idx = df_p.index[df_p['Product'] == prod][0]
            if df_p.at[idx, 'Stock'] >= qty:
                df_p.at[idx, 'Stock'] -= qty
                with open(self.recipe_file, 'r') as f: recs = json.load(f)
                if prod in recs:
                    for ing, amt in recs[prod].items():
                        if ing in df_i['Ingredient'].values:
                            i_idx = df_i.index[df_i['Ingredient'] == ing][0]
                            n_str = ''.join(c for c in str(df_i.at[i_idx, 'Qty']) if c.isdigit() or c == '.')
                            df_i.at[i_idx, 'Qty'] = round(float(n_str or 0) - (amt * qty), 3)
                df_p.to_csv("bakery_inventory.csv", index=False); df_i.to_csv("ingredients.csv", index=False)
                pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Product": prod, "Qty": qty, "Total": (df_p.at[idx, 'Price'] * qty)}]).to_csv("sales_records.csv", mode="a", index=False, header=False)
                self.refresh_all_data(); self.sale_qty.delete(0, 'end')
            else: mbox.showwarning("Stock Alert", "Insufficient stock!")
        except: mbox.showerror("Error", "Invalid entry!")

    def open_add_product(self):
        pop = ctk.CTkToplevel(self); pop.geometry("400x450"); pop.attributes("-topmost", True)
        ctk.CTkLabel(pop, text="Add New Item", font=self.font_header).pack(pady=20)
        n = ctk.CTkEntry(pop, placeholder_text="Product Name", font=self.font_main); n.pack(pady=10)
        p = ctk.CTkEntry(pop, placeholder_text="Price (₱)", font=self.font_main); p.pack(pady=10)
        s = ctk.CTkEntry(pop, placeholder_text="Initial Stock", font=self.font_main); s.pack(pady=10)
        def save():
            df = pd.read_csv("bakery_inventory.csv"); pd.concat([df, pd.DataFrame([{"Product": n.get(), "Price": float(p.get()), "Stock": int(s.get())}])]).to_csv("bakery_inventory.csv", index=False)
            pop.destroy(); self.refresh_all_data()
        ctk.CTkButton(pop, text="Add to Menu", font=self.font_button, command=save, fg_color=self.header_blue, height=45).pack(pady=30)

    def open_admin_expense(self):
        pop = ctk.CTkToplevel(self); pop.geometry("400x350"); pop.attributes("-topmost", True)
        ctk.CTkLabel(pop, text="Log Admin Expense", font=self.font_header).pack(pady=20)
        d = ctk.CTkEntry(pop, placeholder_text="Description", font=self.font_main); d.pack(pady=10)
        a = ctk.CTkEntry(pop, placeholder_text="Amount (₱)", font=self.font_main); a.pack(pady=10)
        def save():
            df = pd.read_csv("ingredients.csv"); pd.concat([df, pd.DataFrame([{"Ingredient": f"[ADMIN] {d.get()}", "Qty": "1", "Cost": float(a.get())}])]).to_csv("ingredients.csv", index=False)
            pop.destroy(); self.refresh_all_data()
        ctk.CTkButton(pop, text="Log Expense", font=self.font_button, command=save, fg_color="#E57373", height=45).pack(pady=30)

    def open_add_ingredient(self):
        pop = ctk.CTkToplevel(self)
        pop.geometry("400x500")
        pop.attributes("-topmost", True)
        pop.title("Material Manager")
        
        ctk.CTkLabel(pop, text="Register or Restock Material", font=self.font_header).pack(pady=20)
        
        n = ctk.CTkEntry(pop, placeholder_text="Ingredient Name", font=self.font_main, width=250)
        n.pack(pady=10)
        q = ctk.CTkEntry(pop, placeholder_text="Qty to Add", font=self.font_main, width=250)
        q.pack(pady=10)
        c = ctk.CTkEntry(pop, placeholder_text="Additional Cost (₱)", font=self.font_main, width=250)
        c.pack(pady=10)

        def save():
            try:
                name, add_qty, add_cost = n.get().strip(), float(q.get()), float(c.get())
                df = pd.read_csv("ingredients.csv")
                
                if name in df['Ingredient'].values:
                    idx = df.index[df['Ingredient'] == name][0]
                    # Update existing stock (fixes negative values like your Flour: -4990)
                    df.at[idx, 'Qty'] = float(df.at[idx, 'Qty']) + add_qty
                    df.at[idx, 'Cost'] = float(df.at[idx, 'Cost']) + add_cost
                else:
                    # Create new entry
                    df = pd.concat([df, pd.DataFrame([{"Ingredient": name, "Qty": add_qty, "Cost": add_cost}])])
                
                df.to_csv("ingredients.csv", index=False)
                pop.destroy()
                self.refresh_all_data()
            except:
                mbox.showerror("Error", "Enter valid numbers for Qty and Cost")

        ctk.CTkButton(pop, text="Confirm Update", font=self.font_button, command=save, fg_color=self.header_blue, height=45).pack(pady=30)

    def open_recipe_manager(self):
        pop = ctk.CTkToplevel(self); pop.geometry("450x450"); pop.attributes("-topmost", True)
        ctk.CTkLabel(pop, text="Recipe Linker", font=self.font_header).pack(pady=20)
        df_p = pd.read_csv("bakery_inventory.csv"); df_i = pd.read_csv("ingredients.csv")
        p_o = ctk.CTkOptionMenu(pop, values=df_p["Product"].tolist() if not df_p.empty else ["None"], font=self.font_main, fg_color=self.header_blue); p_o.pack(pady=10)
        i_o = ctk.CTkOptionMenu(pop, values=[i for i in df_i["Ingredient"].tolist() if "[ADMIN]" not in i], font=self.font_main, fg_color=self.header_blue); i_o.pack(pady=10)
        a_e = ctk.CTkEntry(pop, placeholder_text="Usage per piece", font=self.font_main); a_e.pack(pady=10)
        def save():
            with open(self.recipe_file, 'r') as f: r = json.load(f)
            r.setdefault(p_o.get(), {})[i_o.get()] = float(a_e.get())
            with open(self.recipe_file, 'w') as f: json.dump(r, f); pop.destroy()
        ctk.CTkButton(pop, text="Link to Recipe", font=self.font_button, command=save, fg_color=self.header_blue, height=45).pack(pady=25)

    def delete_product(self, name):
        if mbox.askyesno("Delete", f"Remove {name}?"):
            df = pd.read_csv("bakery_inventory.csv"); df[df['Product'] != name].to_csv("bakery_inventory.csv", index=False); self.refresh_all_data()

    def delete_ing(self, name):
        if mbox.askyesno("Delete", f"Remove {name}?"):
            df = pd.read_csv("ingredients.csv"); df[df['Ingredient'] != name].to_csv("ingredients.csv", index=False); self.refresh_all_data()

if __name__ == "__main__":
    app = BakeryApp(); app.mainloop()
