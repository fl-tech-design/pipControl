import json
import os
import subprocess

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen, ScreenManager

Builder.load_file("kv_files/main.kv")
Builder.load_file("kv_files/scr_main.kv")
Builder.load_file("kv_files/scr_sett.kv")
Builder.load_file('kv_files/pop_help.kv')

debug_stat = 0


def create_temp_files():
    print("create_temp_files called:")
    temp_folder = "temp_files"
    file_names = ["installed_packs.txt", "outdated_packs.txt", 'output.txt']

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    file1 = os.path.join(temp_folder, file_names[0])
    if not os.path.exists(file1):
        with open(file1, "w") as f:
            f.write("")

    file2 = os.path.join(temp_folder, file_names[1])
    if not os.path.exists(file2):
        with open(file2, "w") as f:
            f.write("")

    file3 = os.path.join(temp_folder, file_names[2])
    if not os.path.exists(file3):
        with open(file3, "w") as f:
            f.write("")


def ret_temp_pack_file(file_name):
    if file_name == "outdated":
        f_name = "temp_files/outdated_packs.txt"
    else:
        f_name = "temp_files/installed_packs.txt"
    with open(f_name, "r") as f:
        temp_packet_list = f.readlines()
    if debug_stat:
        print("Packagelist from ret_temp_pack_file: ", temp_packet_list)
    return temp_packet_list


def upgrade_pack(package_name):
    com = ["pip", "install", "--upgrade", package_name]
    subprocess.run(com)


class Table(RelativeLayout):
    def create_table(self, file_name, s):
        data_list = []
        data = ret_temp_pack_file(file_name)
        for item in data:
            d_split = item.split()
            data_list.append(d_split)
        if debug_stat:
            print("data_list from create_table: ", data_list)
            print("file_name from outside: ", file_name)

        # Erstellen der Label-Widgets mit dynamischen Namen
        self.add_widget(Label(text='Package:', height="15sp", size_hint_y=None))
        self.add_widget(Label(text='Version:'))
        self.add_widget(Label(text='Latest:'))
        self.add_widget(Label(text='Type'))

        for row in data_list:
            if debug_stat:
                print("for_loop start: ", row)
            label = LinkLabel(text=f"[ref={row[0]}][color=#3465A4]{row[0]}[/color][/ref]",
                              markup=True)
            self.add_widget(label)
            self.add_widget(Label(text=row[1]))
            self.add_widget(Label(text=""))
            self.add_widget(Label(text=""))


class LinkLabel(Label):
    def on_ref_press(self, instance):
        app.act_package = instance
        app.show_popup(f"möchten sie das paket {instance} upgraden?", "inst")

    def on_hover(self, hover):
        if hover:
            self.text = 'Ich werde gehovered!'
        else:
            self.text = 'Ich werde nicht gehovered...'


class InfoPopup(Popup):
    popup_message = StringProperty('')  # The text to display in the popup message

    def __init__(self, popup_message, **kwargs):
        super().__init__(**kwargs)
        self.popup_message = popup_message

    def but_yes_func(self):
        if debug_stat:
            print("but_yes_func called...")
        upgrade_pack(app.act_package)


class ScrMain(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.len_packet_list = None
        self.packet_list = None
        self.args_scr_one = None
        self.selected_package = ""
        self.table = Table()

    def upd_scr_main(self, *args):
        self.args_scr_one = args

        self.ids.lab_actions_title.text = app.act_lab_txt["actions"][app.act_lang] + ":"
        self.ids.lab_output_title.text = app.act_lab_txt["output"][app.act_lang] + ":"
        self.ids.lab_list_installed.text = app.act_lab_txt["list installed packets"][app.act_lang]
        self.ids.lab_list_outdated.text = app.act_lab_txt["list outdated packets"][app.act_lang]
        self.ids.but_show_inst_packs.text = app.act_lab_txt["show packs"][app.act_lang]
        self.ids.but_show_outd_packs.text = app.act_lab_txt["show packs"][app.act_lang]
        self.ids.but_sett.text = app.act_lab_txt["settings"][app.act_lang]

    def but_package_func(self, pip_cmd):
        self.get_pips(pip_cmd)
        self.table.create_table(pip_cmd, 1)

    def get_pips(self, pip_cmd):
        try:
            if pip_cmd == "outdated":
                command = ['pip', 'list', '--outdated']
                f_name = 'outdated_packs.txt'
            else:
                command = ['pip', 'list']
                f_name = 'installed_packs.txt'
            output = subprocess.check_output(command)
            output_str = output.decode('utf-8')
            lines = output_str.split('\n')[2:]
            output_str = '\n'.join(lines)
            if output_str == "":
                output_str = "Alle Pakete aktuell"
            with open(os.path.join('temp_files', f_name), 'w') as f:
                f.write(output_str)
        except subprocess.CalledProcessError as e:
            # Fehlermeldung speichern
            with open(os.path.join('temp_files', 'error.txt'), 'w') as f:
                f.write(str(e))


class ScrSett(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.args_scr_sett = None

    def upd_scr_sett(self, *args):
        self.args_scr_sett = args
        self.ids.tit_sett.text = app.act_lab_txt["settings"][app.act_lang]
        self.ids.tit_language.text = app.act_lab_txt["language"][app.act_lang]
        self.ids.but_french.text = app.act_lab_txt["french"][app.act_lang]
        self.ids.but_german.text = app.act_lab_txt["german"][app.act_lang]
        self.ids.but_greek.text = app.act_lab_txt["greek"][app.act_lang]
        self.ids.but_italian.text = app.act_lab_txt["italian"][app.act_lang]
        self.ids.but_spanish.text = app.act_lab_txt["spanish"][app.act_lang]
        self.ids.but_english.text = app.act_lab_txt["english"][app.act_lang]
        self.ids.but_back.text = app.act_lab_txt["back"][app.act_lang]


class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("iinit start")
        create_temp_files()
        self.act_package = ""
        self.app_config = {}
        self.load_app_config()
        self.app_data = self.json_data["app_data"]
        self.act_lang = self.app_data["act_lang"]
        self.act_lab_txt = self.json_data["lab_txt"]

        self.scr_man, self.scr_main, self.scr_sett = (None,) * 3

        self.act_b_col_n = self.app_data["colors"][self.app_data["act_col_n"]]
        self.act_b_col_d = self.app_data["colors"][self.app_data["act_col_d"]]

    def build(self):
        print("build start")
        self.title = "pip Control"
        self.scr_man = ScreenManager()

        self.scr_main = ScrMain()
        screen = Screen(name="scr_main")
        screen.add_widget(self.scr_main)
        self.scr_man.add_widget(screen)
        Clock.schedule_interval(self.scr_main.upd_scr_main, 0.2)

        self.scr_sett = ScrSett()
        screen = Screen(name="scr_sett")
        screen.add_widget(self.scr_sett)
        self.scr_man.add_widget(screen)
        Clock.schedule_interval(self.scr_sett.upd_scr_sett, 0.2)

        return self.scr_man

    def load_app_config(self):
        with open("app_config.json", "r") as f:
            a_data = json.load(f)
        self.json_data = a_data
        self.app_data = self.json_data["app_data"]
        self.act_lang = self.app_data["act_lang"]
        self.act_lab_txt = self.json_data["lab_txt"]
        self.act_b_col_n = self.app_data["colors"][self.app_data["act_col_n"]]
        self.act_b_col_d = self.app_data["colors"][self.app_data["act_col_d"]]

    def change_scr(self, trans, new_scr):
        self.scr_man.transition.direction = trans
        self.scr_man.current = new_scr

    def change_lang(self, new_lang):
        with open("app_config.json", "r") as f:
            data = json.load(f)
        data["app_data"]["act_lang"] = new_lang
        with open("app_config.json", "w") as f:
            json.dump(data, f)
        self.load_app_config()

    def show_popup(self, popup_msg, tit="h"):
        popup = InfoPopup(popup_message=popup_msg)
        if tit == "h":
            popup.title = self.act_lab_txt["help"][self.act_lang]
        elif tit == "inst":
            popup.title = "Installation"
        else:
            popup.title = self.act_lab_txt["information"][self.act_lang]

        popup.open()


if __name__ == '__main__':
    app = MainApp()
    app.run()
