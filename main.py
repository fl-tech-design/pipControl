import json
import subprocess

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager

Builder.load_file("kv_files/main.kv")
Builder.load_file("kv_files/scr_main.kv")
Builder.load_file("kv_files/scr_sett.kv")
Builder.load_file('kv_files/pop_help.kv')

def load_inst_pack_list():
    with open("temp_files/installed_packs.txt", "r") as f:
        next(f)
        next(f)
        temp_packet_list = f.readlines()
    return temp_packet_list

class LinkLabel(Label):
    def on_ref_press(self, instance):
        print(f"Link clicked! Value: {instance}")  # Hier können Sie Ihre Funktion aufrufen
        #command = ['pip', "install", "--upgrade", instance]
        #output = subprocess.check_output(command)


class HelpPopup(Popup):
    popup_message = StringProperty('')  # The text to display in the popup message

    def __init__(self, popup_message, **kwargs):
        super().__init__(**kwargs)
        self.popup_message = popup_message




class ScrMain(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.args_scr_one = None
        self.list_packages = load_inst_pack_list()
        self.selected_package = ""

    def upd_scr_main(self, *args):
        self.args_scr_one = args
        self.set_lab_paket_name()
        self.ids.lab_actions.text = app.act_lab_txt["actions"][app.act_lang]
        self.ids.but_sett.text = app.act_lab_txt["settings"][app.act_lang]

    def set_lab_paket_name(self):
        packet_list = load_inst_pack_list()
        p_split = packet_list[0].split()
        self.ids.lab_output.text = f'[ref={p_split[0]}]{p_split[0]}[/ref]'

    def get_installed_pips(self):
        command = ['pip', "list"]
        output = subprocess.check_output(command)
        print("output: ", output)
        if output.strip():
            with open('temp_files/installed_packs.txt', 'w') as f:
                f.write(output.decode('utf-8'))
        else:
            with open('temp_files/installed_packs.txt', 'w') as f:
                f.write("Es gibt keine veralteten Pakete.")
        print(output.decode("utf-8"))
        self.set_installed_packs()

    def set_installed_packs(self):
        li_packs = load_inst_pack_list()
        p_names, p_versions = [], []
        p_dict = {}
        for element in li_packs:
            full_package = element.split()
            p_names.append(full_package[0])
            p_versions.append(full_package[1])
        print(p_names)
        print(p_versions)

        packets_dict = {"p_name": p_names, "p_vers": p_versions}

        # Liste für neue Daten

        app.json_data["app_data"]["installed_packs"] = packets_dict
        with open("app_data.json", "w") as f:
            json.dump(app.json_data, f)

    def get_outdated_pips(self):
        command = ['pip', "list", "--outdated"]
        output = subprocess.check_output(command)
        if output.strip():
            with open('temp_files/outdated_packs.txt', 'w') as f:
                f.write(output.decode('utf-8'))
        else:
            with open('temp_files/outdated_packs.txt', 'w') as f:
                f.write("Es gibt keine veralteten Pakete.")
        print(output.decode("utf-8"))


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
        self.scr_man, self.scr_main, self.scr_sett = (None,) * 3
        self.get_json_data()
        self.app_data = self.json_data["app_data"]
        self.act_lang = self.app_data["act_lang"]
        self.act_lab_txt = self.json_data["lab_txt"]

    def build(self):
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

    def get_json_data(self):
        with open("app_data.json", "r") as f:
            a_data = json.load(f)
        self.json_data = a_data
        print(self.json_data)
        self.app_data = self.json_data["app_data"]
        self.act_lang = self.app_data["act_lang"]
        self.act_lab_txt = self.json_data["lab_txt"]

    def change_scr(self, trans, new_scr):
        self.scr_man.transition.direction = trans
        self.scr_man.current = new_scr

    def change_lang(self, new_lang):
        with open("app_data.json", "r") as f:
            data = json.load(f)
        data["app_data"]["act_lang"] = new_lang
        with open("app_data.json", "w") as f:
            json.dump(data, f)
        self.get_json_data()

    def show_help(self, popup_msg):
        popup = HelpPopup(popup_message=popup_msg)
        popup.open()


if __name__ == '__main__':
    app = MainApp()

    app.run()
