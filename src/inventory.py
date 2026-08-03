import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                              QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit,
                              QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
                              QGroupBox, QHeaderView, QFrame, QCheckBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from datetime import datetime
from database import db

class InventoryDialog(QDialog):
    def __init__(self, item_data=None, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        
        self.setWindowTitle("Add/Edit Inventory Item")
        self.setFixedSize(500, 600)
        
        self.setup_ui()
        
        if item_data:
            self.load_item_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Part Number
        self.part_number_input = QLineEdit()
        self.part_number_input.setPlaceholderText("Enter unique part number")
        self.part_number_input.setMaxLength(50)
        form_layout.addRow("Part Number:*", self.part_number_input)
        
        # Part Name
        self.part_name_input = QLineEdit()
        self.part_name_input.setPlaceholderText("Enter part name/description")
        self.part_name_input.setMaxLength(200)
        form_layout.addRow("Part Name:*", self.part_name_input)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            'Motors',
            'Sensors',
            'Meters',
            'Bearings',
            'Seals',
            'Valves',
            'Pipes',
            'Electrical',
            'Tools',
            'Consumables',
            'Other'
        ])
        self.category_combo.setEditable(True)
        form_layout.addRow("Category:*", self.category_combo)
        
        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(0, 10000)
        self.quantity_spin.setValue(0)
        form_layout.addRow("Quantity:*", self.quantity_spin)
        
        # Minimum Quantity
        self.min_quantity_spin = QSpinBox()
        self.min_quantity_spin.setRange(1, 100)
        self.min_quantity_spin.setValue(5)
        form_layout.addRow("Minimum Quantity:*", self.min_quantity_spin)
        
        # Unit Price
        self.unit_price_spin = QDoubleSpinBox()
        self.unit_price_spin.setRange(0.01, 10000.00)
        self.unit_price_spin.setDecimals(2)
        self.unit_price_spin.setPrefix("$")
        form_layout.addRow("Unit Price:", self.unit_price_spin)
        
        # Supplier
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("Enter supplier name")
        self.supplier_input.setMaxLength(100)
        form_layout.addRow("Supplier:", self.supplier_input)
        
        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter storage location")
        self.location_input.setMaxLength(100)
        form_layout.addRow("Storage Location:", self.location_input)
        
        # Restock Alert
        self.restock_check = QCheckBox("Enable restock alerts")
        self.restock_check.setChecked(True)
        form_layout.addRow("", self.restock_check)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_item_data(self):
        """Load existing item data into form"""
        self.part_number_input.setText(self.item_data.get('part_number', ''))
        self.part_name_input.setText(self.item_data.get('part_name', ''))
        
        category = self.item_data.get('category', '')
        index = self.category_combo.findText(category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        else:
            self.category_combo.setCurrentText(category)
        
        self.quantity_spin.setValue(self.item_data.get('quantity', 0))
        self.min_quantity_spin.setValue(self.item_data.get('min_quantity', 5))
        self.unit_price_spin.setValue(float(self.item_data.get('unit_price', 0)))
        self.supplier_input.setText(self.item_data.get('supplier', ''))
        self.location_input.setText(self.item_data.get('location', ''))
        self.restock_check.setChecked(True)  # Default to enabled
    
    def get_item_data(self):
        """Get form data as dictionary"""
        return {
            'part_number': self.part_number_input.text().strip().upper(),
            'part_name': self.part_name_input.text().strip(),
            'category': self.category_combo.currentText().strip(),
            'quantity': self.quantity_spin.value(),
            'min_quantity': self.min_quantity_spin.value(),
            'unit_price': self.unit_price_spin.value(),
            'supplier': self.supplier_input.text().strip(),
            'location': self.location_input.text().strip()
        }

class InventoryWidget(QWidget):
    inventory_updated = Signal()
    
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.inventory_items = []
        self.low_stock_items = []
        
        self.setup_ui()
        self.load_inventory()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Inventory Management")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1976D2;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add Item Button
        self.add_btn = QPushButton("➕ Add Item")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_btn.clicked.connect(self.add_item)
        header_layout.addWidget(self.add_btn)
        
        # Refresh Button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_inventory)
        header_layout.addWidget(self.refresh_btn)
        
        # Low Stock Alert Button
        self.alert_btn = QPushButton("⚠️ Low Stock")
        self.alert_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        self.alert_btn.clicked.connect(self.show_low_stock_alerts)
        header_layout.addWidget(self.alert_btn)
        
        layout.addLayout(header_layout)
        
        # Summary Cards
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)
        
        # Total Items Card
        self.total_card = self.create_summary_card("Total Items", "0", "#1976D2")
        summary_layout.addWidget(self.total_card)
        
        # Low Stock Card
        self.low_stock_card = self.create_summary_card("Low Stock Items", "0", "#F44336")
        summary_layout.addWidget(self.low_stock_card)
        
        # Total Value Card
        self.total_value_card = self.create_summary_card("Total Inventory Value", "$0.00", "#4CAF50")
        summary_layout.addWidget(self.total_value_card)
        
        # Categories Card
        self.categories_card = self.create_summary_card("Categories", "0", "#FF9800")
        summary_layout.addWidget(self.categories_card)
        
        layout.addLayout(summary_layout)
        
        # Search and Filter
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by part number, name, or supplier...")
        self.search_input.textChanged.connect(self.filter_inventory)
        search_layout.addWidget(self.search_input)
        
        # Category Filter
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", "all")
        self.category_filter.addItem("Motors", "Motors")
        self.category_filter.addItem("Sensors", "Sensors")
        self.category_filter.addItem("Meters", "Meters")
        self.category_filter.addItem("Bearings", "Bearings")
        self.category_filter.addItem("Seals", "Seals")
        self.category_filter.addItem("Valves", "Valves")
        self.category_filter.addItem("Pipes", "Pipes")
        self.category_filter.addItem("Electrical", "Electrical")
        self.category_filter.addItem("Tools", "Tools")
        self.category_filter.addItem("Consumables", "Consumables")
        self.category_filter.addItem("Other", "Other")
        self.category_filter.currentTextChanged.connect(self.filter_inventory)
        search_layout.addWidget(self.category_filter)
        
        # Stock Status Filter
        self.stock_filter = QComboBox()
        self.stock_filter.addItem("All Items", "all")
        self.stock_filter.addItem("In Stock", "in_stock")
        self.stock_filter.addItem("Low Stock", "low_stock")
        self.stock_filter.addItem("Out of Stock", "out_of_stock")
        self.stock_filter.currentTextChanged.connect(self.filter_inventory)
        search_layout.addWidget(self.stock_filter)
        
        layout.addLayout(search_layout)
        
        # Inventory Table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(12)
        self.inventory_table.setHorizontalHeaderLabels([
            "ID", "Part Number", "Part Name", "Category", "Quantity", 
            "Min Qty", "Status", "Unit Price", "Supplier", "Location", 
            "Last Restocked", "Actions"
        ])
        
        # Table styling
        self.inventory_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 10px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        # Configure table
        header = self.inventory_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.inventory_table)
        
        # Action Buttons
        action_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("✏️ Edit Item")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #E0E0E0;
                color: #9E9E9E;
            }
        """)
        self.edit_btn.clicked.connect(self.edit_item)
        self.edit_btn.setEnabled(False)
        
        self.adjust_stock_btn = QPushButton("📦 Adjust Stock")
        self.adjust_stock_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #E0E0E0;
                color: #9E9E9E;
            }
        """)
        self.adjust_stock_btn.clicked.connect(self.adjust_stock)
        self.adjust_stock_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("🗑️ Delete Item")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:disabled {
                background-color: #E0E0E0;
                color: #9E9E9E;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_item)
        self.delete_btn.setEnabled(False)
        
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.adjust_stock_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
        
        # Connect table selection
        self.inventory_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def create_summary_card(self, title, value, color):
        """Create a summary card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
                color: white;
            }}
        """)
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        title_label.setStyleSheet("color: white;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        value_label.setStyleSheet("color: white;")
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        card.setLayout(card_layout)
        return card
    
    def load_inventory(self):
        """Load inventory from database"""
        try:
            if db.connect():
                query = "SELECT * FROM inventory ORDER BY category, part_name"
                self.inventory_items = db.execute_query(query)
                db.close()
                
                self.populate_table()
                self.update_summary_cards()
                self.check_low_stock()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load inventory: {str(e)}")
    
    def populate_table(self):
        """Populate table with inventory data"""
        self.inventory_table.setRowCount(len(self.inventory_items))
        
        for row, item in enumerate(self.inventory_items):
            # ID
            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            
            # Part Number
            self.inventory_table.setItem(row, 1, QTableWidgetItem(item['part_number']))
            
            # Part Name
            self.inventory_table.setItem(row, 2, QTableWidgetItem(item['part_name']))
            
            # Category
            self.inventory_table.setItem(row, 3, QTableWidgetItem(item['category']))
            
            # Quantity
            quantity = item['quantity']
            quantity_item = QTableWidgetItem(str(quantity))
            
            # Color code quantity based on stock level
            min_quantity = item['min_quantity']
            if quantity <= 0:
                quantity_item.setBackground(QColor('#F44336'))  # Red
                quantity_item.setForeground(QColor('white'))
            elif quantity <= min_quantity:
                quantity_item.setBackground(QColor('#FF9800'))  # Orange
                quantity_item.setForeground(QColor('white'))
            else:
                quantity_item.setBackground(QColor('#4CAF50'))  # Green
                quantity_item.setForeground(QColor('white'))
            
            self.inventory_table.setItem(row, 4, quantity_item)
            
            # Minimum Quantity
            self.inventory_table.setItem(row, 5, QTableWidgetItem(str(min_quantity)))
            
            # Status with color coding
            if quantity <= 0:
                status = "OUT OF STOCK"
                status_color = '#F44336'
            elif quantity <= min_quantity:
                status = "LOW STOCK"
                status_color = '#FF9800'
            else:
                status = "IN STOCK"
                status_color = '#4CAF50'
            
            status_item = QTableWidgetItem(status)
            status_item.setBackground(QColor(status_color))
            status_item.setForeground(QColor('white'))
            self.inventory_table.setItem(row, 6, status_item)
            
            # Unit Price
            price = float(item.get('unit_price', 0))
            price_str = f"${price:.2f}"
            self.inventory_table.setItem(row, 7, QTableWidgetItem(price_str))
            
            # Supplier
            self.inventory_table.setItem(row, 8, QTableWidgetItem(item.get('supplier', '')))
            
            # Location
            self.inventory_table.setItem(row, 9, QTableWidgetItem(item.get('location', '')))
            
            # Last Restocked
            last_restocked = item.get('last_restocked')
            if last_restocked:
                last_restock_str = last_restocked.strftime('%Y-%m-%d')
            else:
                last_restock_str = 'N/A'
            self.inventory_table.setItem(row, 10, QTableWidgetItem(last_restock_str))
        
        self.inventory_table.resizeColumnsToContents()
    
    def update_summary_cards(self):
        """Update summary card values"""
        total_items = len(self.inventory_items)
        low_stock_count = sum(1 for item in self.inventory_items if item['quantity'] <= item['min_quantity'])
        total_value = sum(float(item.get('unit_price', 0)) * item['quantity'] for item in self.inventory_items)
        categories = len(set(item['category'] for item in self.inventory_items))
        
        # Update card values
        self.total_card.layout().itemAt(1).widget().setText(str(total_items))
        self.low_stock_card.layout().itemAt(1).widget().setText(str(low_stock_count))
        self.total_value_card.layout().itemAt(1).widget().setText(f"${total_value:,.2f}")
        self.categories_card.layout().itemAt(1).widget().setText(str(categories))
    
    def check_low_stock(self):
        """Check for low stock items and create alerts"""
        self.low_stock_items = [item for item in self.inventory_items if item['quantity'] <= item['min_quantity']]
        
        if self.low_stock_items:
            # Update alert button
            self.alert_btn.setText(f"⚠️ Low Stock ({len(self.low_stock_items)})")
            self.alert_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    animation: pulse 1s infinite;
                }
                QPushButton:hover {
                    background-color: #D32F2F;
                }
            """)
            
            # Create notifications
            self.create_low_stock_notifications()
    
    def create_low_stock_notifications(self):
        """Create notifications for low stock items"""
        try:
            if db.connect():
                for item in self.low_stock_items:
                    # Check if notification already exists
                    check_query = """
                        SELECT COUNT(*) as count FROM notifications 
                        WHERE title LIKE %s AND is_read = FALSE
                    """
                    result = db.execute_query(check_query, (f'%Stock Alert%{item["part_number"]}%',))
                    
                    if result and result[0]['count'] == 0:
                        # Create new notification
                        notification_query = """
                            INSERT INTO notifications (title, message, type, priority)
                            VALUES (%s, %s, %s, %s)
                        """
                        message = (f"Part: {item['part_name']} ({item['part_number']})\n"
                                 f"Current Stock: {item['quantity']}\n"
                                 f"Minimum Required: {item['min_quantity']}\n"
                                 f"Supplier: {item.get('supplier', 'Unknown')}")
                        
                        db.execute_update(notification_query,
                                        (f"Stock Alert: {item['part_number']}", 
                                         message, 'inventory', 'high'))
                
                db.close()
        except Exception as e:
            print(f"Failed to create low stock notifications: {e}")
    
    def filter_inventory(self):
        """Filter inventory based on search and category"""
        search_text = self.search_input.text().lower()
        category_filter = self.category_filter.currentData()
        stock_filter = self.stock_filter.currentData()
        
        for row in range(self.inventory_table.rowCount()):
            # Search filter
            part_number = self.inventory_table.item(row, 1).text().lower()
            part_name = self.inventory_table.item(row, 2).text().lower()
            supplier = self.inventory_table.item(row, 8).text().lower()
            
            search_match = (search_text in part_number or 
                          search_text in part_name or 
                          search_text in supplier)
            
            # Category filter
            category_match = True
            if category_filter != "all":
                category = self.inventory_table.item(row, 3).text()
                category_match = category == category_filter
            
            # Stock filter
            stock_match = True
            if stock_filter != "all":
                status = self.inventory_table.item(row, 6).text()
                if stock_filter == "in_stock":
                    stock_match = status == "IN STOCK"
                elif stock_filter == "low_stock":
                    stock_match = status == "LOW STOCK"
                elif stock_filter == "out_of_stock":
                    stock_match = status == "OUT OF STOCK"
            
            self.inventory_table.setRowHidden(row, not (search_match and category_match and stock_match))
    
    def on_selection_changed(self):
        """Enable/disable buttons based on selection"""
        has_selection = len(self.inventory_table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.adjust_stock_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def add_item(self):
        """Add new inventory item"""
        dialog = InventoryDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item_data = dialog.get_item_data()
            
            try:
                if db.connect():
                    query = """
                        INSERT INTO inventory (part_number, part_name, category, quantity,
                                             min_quantity, unit_price, supplier, location)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (
                        item_data['part_number'],
                        item_data['part_name'],
                        item_data['category'],
                        item_data['quantity'],
                        item_data['min_quantity'],
                        item_data['unit_price'],
                        item_data['supplier'],
                        item_data['location']
                    )
                    
                    if db.execute_update(query, params):
                        # Log the action
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'add_inventory',
                                         f"Added inventory item: {item_data['part_number']}", 'info'))
                        
                        QMessageBox.information(self, "Success", "Inventory item added successfully!")
                        self.load_inventory()
                        self.inventory_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to add inventory item.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add inventory item: {str(e)}")
    
    def edit_item(self):
        """Edit selected inventory item"""
        current_row = self.inventory_table.currentRow()
        if current_row < 0:
            return
        
        item_id = int(self.inventory_table.item(current_row, 0).text())
        item_data = next((item for item in self.inventory_items if item['id'] == item_id), None)
        
        if not item_data:
            return
        
        dialog = InventoryDialog(item_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_item_data()
            
            try:
                if db.connect():
                    query = """
                        UPDATE inventory 
                        SET part_number = %s, part_name = %s, category = %s, quantity = %s,
                            min_quantity = %s, unit_price = %s, supplier = %s, location = %s
                        WHERE id = %s
                    """
                    params = (
                        updated_data['part_number'],
                        updated_data['part_name'],
                        updated_data['category'],
                        updated_data['quantity'],
                        updated_data['min_quantity'],
                        updated_data['unit_price'],
                        updated_data['supplier'],
                        updated_data['location'],
                        item_id
                    )
                    
                    if db.execute_update(query, params):
                        # Log the action
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'edit_inventory',
                                         f"Updated inventory item: {updated_data['part_number']}", 'info'))
                        
                        QMessageBox.information(self, "Success", "Inventory item updated successfully!")
                        self.load_inventory()
                        self.inventory_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to update inventory item.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update inventory item: {str(e)}")
    
    def adjust_stock(self):
        """Adjust stock quantity for selected item"""
        current_row = self.inventory_table.currentRow()
        if current_row < 0:
            return
        
        item_id = int(self.inventory_table.item(current_row, 0).text())
        current_qty = int(self.inventory_table.item(current_row, 4).text())
        part_number = self.inventory_table.item(current_row, 1).text()
        
        # Simple input dialog for stock adjustment
        from PySide6.QtWidgets import QInputDialog
        
        new_qty, ok = QInputDialog.getInt(self, "Adjust Stock", 
                                        f"Adjust stock for {part_number}:",
                                        current_qty, 0, 10000, 1)
        
        if ok and new_qty != current_qty:
            try:
                if db.connect():
                    query = "UPDATE inventory SET quantity = %s, last_restocked = CURDATE() WHERE id = %s"
                    
                    if db.execute_update(query, (new_qty, item_id)):
                        # Log the action
                        adjustment = new_qty - current_qty
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'adjust_stock',
                                         f"Adjusted stock for {part_number}: {current_qty} → {new_qty} ({adjustment:+'d'})", 'info'))
                        
                        QMessageBox.information(self, "Success", "Stock adjusted successfully!")
                        self.load_inventory()
                        self.inventory_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to adjust stock.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to adjust stock: {str(e)}")
    
    def delete_item(self):
        """Delete selected inventory item"""
        current_row = self.inventory_table.currentRow()
        if current_row < 0:
            return
        
        item_id = int(self.inventory_table.item(current_row, 0).text())
        part_number = self.inventory_table.item(current_row, 1).text()
        part_name = self.inventory_table.item(current_row, 2).text()
        
        reply = QMessageBox.question(self, "Confirm Delete",
                                   f"Are you sure you want to delete '{part_name}' ({part_number})?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if db.connect():
                    query = "DELETE FROM inventory WHERE id = %s"
                    
                    if db.execute_update(query, (item_id,)):
                        # Log the action
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'delete_inventory',
                                         f"Deleted inventory item: {part_number}", 'warning'))
                        
                        QMessageBox.information(self, "Success", "Inventory item deleted successfully!")
                        self.load_inventory()
                        self.inventory_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to delete inventory item.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete inventory item: {str(e)}")
    
    def show_low_stock_alerts(self):
        """Show low stock alerts dialog"""
        if not self.low_stock_items:
            QMessageBox.information(self, "Stock Status", "No items are currently low on stock.")
            return
        
        alert_text = "The following items need restocking:\n\n"
        
        for item in self.low_stock_items:
            alert_text += (f"• {item['part_name']} ({item['part_number']})\n"
                          f"  Current Stock: {item['quantity']}\n"
                          f"  Minimum Required: {item['min_quantity']}\n"
                          f"  Supplier: {item.get('supplier', 'Unknown')}\n\n")
        
        QMessageBox.warning(self, "Low Stock Alert", alert_text)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Initialize database
    db.init_database()
    
    # Demo user data
    demo_user = {
        'id': 1,
        'name': 'Demo User'
    }
    
    inventory = InventoryWidget(demo_user)
    inventory.show()
    
    sys.exit(app.exec())