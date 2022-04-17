import kivy
kivy.require('2.0.0')

from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
from kivy.app import App
from kivy.uix.label import Label
from kivy import kivy_data_dir
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty, ObjectProperty, NumericProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.button import Button
import os
import json

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

class ProductList(RecycleView):
    def get_selected(self):
        ''' Returns list of selected nodes dicts '''
        return [self.data[idx] for idx in self.layout_manager.selected_nodes]


class ListItem(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(ListItem, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(ListItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected

class ProductButton(Button):
    price = NumericProperty()

class LoginWindow(Screen):
    pass


class TablesWindow(Screen):
    def __init__(self, **kwargs):
        super().__init__()

    def removeTables(self, *args):
        for child in [child for child in self.ids['tables_layout'].children]:
            self.ids['tables_layout'].remove_widget(child)

    

class CheckoutWindow(Screen):
    pass

class TableWindow(Screen):
    container = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__()

    def add_products(self):
        app = App.get_running_app()
        for p in app.products:
            btn = ProductButton(text=p['name'], price=p['price'])
            self.container.add_widget(btn)
        for p in app.tables[int(app.selected_table) - 1]['products']:
            app.root.get_screen('table').ids['final_product_list'].data.append(p)

    def remove_products(self, *args):
        app = App.get_running_app()
        for child in [child for child in self.container.children]:
            self.container.remove_widget(child)
        app.root.get_screen('table').ids['final_product_list'].data = []
        app.root.get_screen('table').ids['temp_product_list'].data = []


class WindowManager(ScreenManager):
    pass

class MyPOS(App):
    def build(self):
        self.admin_password = "123"
        self.password = ""
        self.selected_table = "0"
        self.temp_products_index = 0
        self.final_products_index = 0
        self.tables = [{"id": i, "total": 0, "name": "Table: " + str(i), "products": []} for i in range(1, 15)]
        self.products = []

        with open('products.json', 'r') as j:
            self.products = json.loads(j.read())

        return WindowManager()

    def addTables(self):
        app = App.get_running_app()
        for t in self.tables:
            btn = Button(text=str(t['id']))
            btn.bind(on_release=self.tableButtonHandler)
            self.root.get_screen('tables').ids['tables_layout'].add_widget(btn)
        exit_btn = Button(text="Exit")
        exit_btn.bind(on_release=self.exitButtonHandler)
        self.root.get_screen('tables').ids['tables_layout'].add_widget(exit_btn)

    def tableButtonHandler(self, instance):
        self.setSelectedTable(instance.text)
        self.root.current = "table"
        self.root.get_screen("tables").manager.transition.direction = "left"

    def exitButtonHandler(self, instance):
        self.root.current = "login"
        self.root.get_screen("tables").manager.transition.direction = "right"

    def updatePasswordInput(self):
        self.root.get_screen('login').ids['password_input'].text = self.password

    def setSelectedTable(self, table):
        self.selected_table = table
        self.root.get_screen('table').ids['table_label'].text = "Table: " + table

    def updateTableTotal(self, table, products):
        self.tables[int(table) - 1]["total"] = 0
        for i in products:
            self.tables[int(table) - 1]["total"] += float(i['item_price'])
        self.root.get_screen('checkout').ids['total_label'].text = "{:.2f}".format(round(self.tables[int(table) - 1]["total"], 2))
        
    def setTableProducts(self, table, products):
        self.tables[int(table) - 1]['products'] = products

    def getTableTotal(self):
        return self.tables[int(self.selected_table) - 1]["total"]

    def getChange(self):
        total = self.tables[int(self.selected_table) - 1]["total"]
        payment = float(self.root.get_screen('checkout').ids['payment_input'].text)
        change =  "{:.2f}".format(round(payment - total, 2))
        self.root.get_screen('checkout').ids['change_label'].text = change

    def finishTable(self, table):
        self.root.get_screen('table').ids['final_product_list'].data = []
        self.root.get_screen('table').ids['temp_product_list'].data = []
        self.tables[int(table) - 1]['total'] = 0
        self.tables[int(table) - 1]['products'] = []

if __name__ == '__main__':
    MyPOS().run()