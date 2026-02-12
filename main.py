import customtkinter as ctk
import pandas as pd
import os
import json
from datetime import datetime

class BakeryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bakery Management System Pro")
        self.geometry("1200x850")
        self.configure(fg_color="#FFD1DC") # Bakery Pink
        self.recipe_file = "recipes.json"
        
        # 1. Initialize Databases
        self.init_csv_files()
        
        # 2. Setup User Interface
        self.setup_ui()

    def init_csv_files(self):
        """Ensures all files exist and have correct headers"""
        files = {
            "bakery_inventory.csv": ["Product", "Price", "Stock"],
            "sales_records.csv": ["Date", "Product", "Qty", "Total"],
            "ingredients.csv": ["Ingredient", "Qty", "Cost"]
        }
        for file, cols in files.items():
            if not os.path.exists(file):
                pd.DataFrame(columns=cols).to_csv(file, index=False)
        
        # Initialize recipe storage
        if not os.path.exists(self.recipe_file):
            with open(self.recipe_file, 'w') as f:
                json.dump({}, f)

    def setup_ui(self):
        # Top Stats Section
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(pady=20, fill="x", padx=40)
        
        # Dashboard Layout
        self.main_grid = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.main_grid.pack(expand=True, fill="both", padx=40, pady=(0, 40))
        
        self.col_inv = self.create_column(self.main_grid, "Inventory & Recipes", 0)
        self.col_sales = self.create_column(self.main_grid, "Customer Orders", 1)
        self.col_restock = self.create_column(self.main_grid, "Ingredient Stock Status", 2)

        # Action Buttons Row
        self.setup_action_buttons()
        self.refresh_all_data()

    def create_column(self, master, title, col):
        frame = ctk.CTkFrame(master, fg_color="white", border_width=1, border_color="#EEEEEE")
        frame.grid(row=0, column=col, sticky="nsew", padx=10, pady=10)
        master.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(frame, text=title, font=("Arial", 16, "bold"), text_color="#5D3A3A").pack(pady=10)
        
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent", height=450)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        return scroll

    def setup_action_buttons(self):
        btn_row = ctk.CTkFrame(self.main_grid, fg_color="transparent")
        btn_row.grid(row=1, column=0, columnspan=3, pady=10)
        
        ctk.CTkButton(btn_row, text="+ New Product", fg_color="#D47088", command=self.open_add_product).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_row, text="🍳 Set Recipe", fg_color="#D47088", command=self.open_recipe_manager).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_row, text="+ New Ingredient", fg_color="#B55B70", command=self.open_add_ingredient).grid(row=0, column=2, padx=5)
        ctk.CTkButton(btn_row, text="🖨️ Print Report", fg_color="#5D3A3A", command=self.generate_printout).grid(row=0, column=3, padx=5)

    def refresh_all_data(self):
        self.refresh_top_stats()
        self.refresh_inventory_list()
        self.setup_sales_section()
        self.refresh_ingredients_list()

    def refresh_top_stats(self):
        for widget in self.top_frame.winfo_children(): widget.destroy()
        sales_txt, exp_txt = "₱0.00", "₱0.00"
        try:
            df_s = pd.read_csv("sales_records.csv")
            if not df_s.empty:
                df_s['Date'] = pd.to_datetime(df_s['Date'], format='mixed', errors='coerce')
                today_sales = df_s[df_s['Date'].dt.date == datetime.now().date()]['Total'].sum()
                sales_txt = f"₱{today_sales:,.2f}"
            
            df_i = pd.read_csv("ingredients.csv")
            if not df_i.empty:
                exp_txt = f"₱{pd.to_numeric(df_i['Cost'], errors='coerce').sum():,.2f}"
        except: pass
        self.create_stat_card(self.top_frame, "Today's Sales", sales_txt, "#E8F5E9").grid(row=0, column=0, padx=10)
        self.create_stat_card(self.top_frame, "Today's Expenses", exp_txt, "#FFEBEE").grid(row=0, column=1, padx=10)

    def create_stat_card(self, master, title, val, color):
        card = ctk.CTkFrame(master, fg_color=color, width=500, height=100, corner_radius=10)
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, font=("Arial", 14), text_color="black").pack(pady=(15,0))
        ctk.CTkLabel(card, text=val, font=("Arial", 28, "bold"), text_color="black").pack(pady=5)
        return card

    # --- INVENTORY & RECIPE LOGIC ---
    def refresh_inventory_list(self):
        for widget in self.col_inv.winfo_children(): widget.destroy()
        df = pd.read_csv("bakery_inventory.csv")
        for _, r in df.iterrows():
            row = ctk.CTkFrame(self.col_inv, fg_color="#F9F9F9", corner_radius=5)
            row.pack(fill="x", pady=2)
            txt = f"{r['Product']} - P{r['Price']} ({r['Stock']} left)"
            lbl_color = "#D32F2F" if r['Stock'] < 10 else "black"
            ctk.CTkLabel(row, text=txt, text_color=lbl_color, font=("Arial", 11)).pack(side="left", padx=5)
            ctk.CTkButton(row, text="🗑️", width=30, fg_color="#FF4C4C", command=lambda n=r['Product']: self.delete_product(n)).pack(side="right", padx=2)

    def open_recipe_manager(self):
        pop = ctk.CTkToplevel(self); pop.geometry("400x400"); pop.title("Set Recipe"); pop.attributes("-topmost", True)
        df_p = pd.read_csv("bakery_inventory.csv")
        df_i = pd.read_csv("ingredients.csv")
        ctk.CTkLabel(pop, text="Product:").pack(pady=5)
        p_opt = ctk.CTkOptionMenu(pop, values=df_p["Product"].tolist() if not df_p.empty else ["No Products"])
        p_opt.pack()
        ctk.CTkLabel(pop, text="Ingredient used per sale:").pack(pady=5)
        i_opt = ctk.CTkOptionMenu(pop, values=df_i["Ingredient"].tolist() if not df_i.empty else ["No Ingredients"])
        i_opt.pack()
        ctk.CTkLabel(pop, text="Amount (e.g., 0.05 for 50g):").pack(pady=5)
        amt = ctk.CTkEntry(pop); amt.pack()
        ctk.CTkButton(pop, text="Save Recipe", fg_color="#D47088", command=lambda: self.save_recipe(p_opt.get(), i_opt.get(), amt.get(), pop)).pack(pady=20)

    def save_recipe(self, product, ing, amount, win):
        if product == "No Products" or ing == "No Ingredients": return
        try:
            with open(self.recipe_file, 'r') as f: recipes = json.load(f)
            if product not in recipes: recipes[product] = {}
            recipes[product][ing] = float(amount)
            with open(self.recipe_file, 'w') as f: json.dump(recipes, f)
            win.destroy()
        except: pass

    # --- SALES & AUTO-DEDUCTION ---
    def setup_sales_section(self):
        for widget in self.col_sales.winfo_children(): widget.destroy()
        df = pd.read_csv("bakery_inventory.csv")
        if not df.empty:
            self.sale_opt = ctk.CTkOptionMenu(self.col_sales, values=df["Product"].tolist(), width=200, fg_color="#D47088")
            self.sale_opt.pack(pady=10)
            self.sale_qty = ctk.CTkEntry(self.col_sales, placeholder_text="Qty", width=100)
            self.sale_qty.pack(pady=10)
            ctk.CTkButton(self.col_sales, text="Confirm Sale", fg_color="#D47088", command=self.process_order).pack(pady=10)

    def process_order(self):
        try:
            df_p = pd.read_csv("bakery_inventory.csv")
            df_i = pd.read_csv("ingredients.csv")
            prod = self.sale_opt.get()
            qty = int(self.sale_qty.get())
            idx = df_p.index[df_p['Product'] == prod][0]
            
            if df_p.at[idx, 'Stock'] >= qty:
                # 1. Deduct Product Stock
                df_p.at[idx, 'Stock'] -= qty
                df_p.to_csv("bakery_inventory.csv", index=False)
                
                # 2. Recipe Ingredient Deduction
                with open(self.recipe_file, 'r') as f: recipes = json.load(f)
                if prod in recipes:
                    for ing_name, amt_per_unit in recipes[prod].items():
                        if ing_name in df_i['Ingredient'].values:
                            i_idx = df_i.index[df_i['Ingredient'] == ing_name][0]
                            curr_qty = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(df_i.at[i_idx, 'Qty']))))
                            df_i.at[i_idx, 'Qty'] = round(curr_qty - (amt_per_unit * qty), 2)
                    df_i.to_csv("ingredients.csv", index=False)
                
                # 3. Record Sales
                new_s = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Product": prod, "Qty": qty, "Total": float(df_p.at[idx, 'Price'] * qty)}])
                new_s.to_csv("sales_records.csv", mode="a", index=False, header=False)
                self.refresh_all_data()
        except: pass

    # --- INGREDIENTS & PRINTING ---
    def refresh_ingredients_list(self):
        for widget in self.col_restock.winfo_children(): widget.destroy()
        df = pd.read_csv("ingredients.csv")
        for _, r in df.iterrows():
            row = ctk.CTkFrame(self.col_restock, fg_color="#F9F9F9")
            row.pack(fill="x", pady=2)
            qty_val = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(r['Qty']))))
            is_low = qty_val <= 1.0
            display_txt = f"• {r['Ingredient']}: {r['Qty']}" + (" (LOW!)" if is_low else "")
            ctk.CTkLabel(row, text=display_txt, font=("Arial", 11, "bold" if is_low else "normal"), text_color="#D32F2F" if is_low else "black").pack(side="left", padx=5)
            ctk.CTkButton(row, text="🗑️", width=30, fg_color="#FF4C4C", command=lambda n=r['Ingredient']: self.delete_ing(n)).pack(side="right", padx=2)

    def generate_printout(self):
        """Generates report with UTF-8 support to handle Peso Sign"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"Report_{today_str}.txt"
        try:
            df_s = pd.read_csv("sales_records.csv")
            df_s['Date'] = pd.to_datetime(df_s['Date'], format='mixed')
            today_sales = df_s[df_s['Date'].dt.date == datetime.now().date()]
            df_i = pd.read_csv("ingredients.csv")
            total_rev = today_sales['Total'].sum()
            total_exp = pd.to_numeric(df_i['Cost'], errors='coerce').sum()
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"BAKERY BUSINESS REPORT: {today_str}\n" + "="*45 + "\n\n")
                f.write("SALES LOG:\n")
                if not today_sales.empty:
                    f.write(today_sales[['Product', 'Qty', 'Total']].to_string(index=False))
                else: f.write("No sales today.")
                f.write("\n\n" + "-"*45 + "\n")
                f.write(f"TOTAL REVENUE:   ₱{total_rev:,.2f}\n")
                f.write(f"TOTAL EXPENSES:  ₱{total_exp:,.2f}\n")
                f.write(f"NET PROFIT:      ₱{total_rev - total_exp:,.2f}\n")
                f.write("="*45 + "\nGenerated on: " + datetime.now().strftime('%H:%M:%S'))
            os.startfile(filename)
        except Exception as e: print(f"Report Error: {e}")

    # --- ADD DATA POPUPS ---
    def open_add_product(self):
        pop = ctk.CTkToplevel(self); pop.geometry("300x300"); pop.title("Add Product"); pop.attributes("-topmost", True)
        n = ctk.CTkEntry(pop, placeholder_text="Name"); n.pack(pady=10)
        p = ctk.CTkEntry(pop, placeholder_text="Price"); p.pack(pady=10)
        s = ctk.CTkEntry(pop, placeholder_text="Stock"); s.pack(pady=10)
        ctk.CTkButton(pop, text="Save", fg_color="#D47088", command=lambda: self.save_p(n.get(), p.get(), s.get(), pop)).pack(pady=20)

    def save_p(self, n, p, s, win):
        try:
            df = pd.read_csv("bakery_inventory.csv")
            new_r = pd.DataFrame([{"Product": n, "Price": float(p), "Stock": int(s)}])
            pd.concat([df, new_r]).to_csv("bakery_inventory.csv", index=False)
            win.destroy(); self.refresh_all_data()
        except: pass

    def open_add_ingredient(self):
        pop = ctk.CTkToplevel(self); pop.geometry("300x320"); pop.title("Add Ingredient"); pop.attributes("-topmost", True)
        n = ctk.CTkEntry(pop, placeholder_text="Item Name"); n.pack(pady=10)
        q = ctk.CTkEntry(pop, placeholder_text="Qty (e.g. 10.0)"); q.pack(pady=10)
        c = ctk.CTkEntry(pop, placeholder_text="Cost (Expense)"); c.pack(pady=10)
        ctk.CTkButton(pop, text="Log Expense", fg_color="#B55B70", command=lambda: self.save_i(n.get(), q.get(), c.get(), pop)).pack(pady=20)

    def save_i(self, n, q, c, win):
        try:
            df = pd.read_csv("ingredients.csv")
            new_r = pd.DataFrame([{"Ingredient": n, "Qty": q, "Cost": float(c)}])
            pd.concat([df, new_r]).to_csv("ingredients.csv", index=False)
            win.destroy(); self.refresh_all_data()
        except: pass

    def delete_product(self, name):
        df = pd.read_csv("bakery_inventory.csv"); df = df[df['Product'] != name]
        df.to_csv("bakery_inventory.csv", index=False); self.refresh_all_data()

    def delete_ing(self, name):
        df = pd.read_csv("ingredients.csv"); df = df[df['Ingredient'] != name]
        df.to_csv("ingredients.csv", index=False); self.refresh_all_data()

if __name__ == "__main__":
    app = BakeryApp(); app.mainloop()
