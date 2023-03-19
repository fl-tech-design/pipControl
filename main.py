import json
import os
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


def load_pack_list(f_name):
    with open(f_name, "r") as f:
        temp_packet_list = f.readlines()
    return temp_packet_list


def ret_package_data(f_name, select_data):
    package_list = load_pack_list(f_name)
    p_list_split, p_name_list, p_vers_list = [], [], []

    i = 0
    for item in package_list:
        p_list_split.append(item.split())
        p_name_list.append(p_list_split[i][0])
        p_vers_list.append(p_list_split[i][1])
        i += 1
    if select_data == "name":
        return p_name_list
    if select_data == "vers":
        return p_vers_list


class LinkLabel(Label):
    def on_ref_press(self, instance):
        print(f"Link clicked! Value: {instance}")  # Hier können Sie Ihre Funktion aufrufen
        # command = ['pip', "install", "--upgrade", instance]
        # output = subprocess.check_output(command)


class HelpPopup(Popup):
    popup_message = StringProperty('')  # The text to display in the popup message

    def __init__(self, popup_message, **kwargs):
        super().__init__(**kwargs)
        self.popup_message = popup_message


class ScrMain(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.len_packet_list = None
        self.packet_list = None
        self.args_scr_one = None
        self.selected_package = ""

    def upd_scr_main(self, *args):
        self.args_scr_one = args

        self.ids.lab_actions.text = app.act_lab_txt["actions"][app.act_lang]
        self.ids.but_sett.text = app.act_lab_txt["settings"][app.act_lang]

    def create_packet_labels(self, package_data_list, pack_stat):
        lab_texts = package_data_list
        print(len(lab_texts))
        self.ids.box_pack_names.clear_widgets()
        for text in lab_texts:
            label_p_name = LinkLabel()
            if pack_stat == "outdated":
                label_p_name.markup = True
                label_p_name.text = f"[ref={text}][color=#0000ff]{text}[/color][/ref]"
            else:
                label_p_name.markup = False
                label_p_name.text = f"{text}"

            self.ids.box_pack_names.add_widget(label_p_name)

    def but_outdated_func(self):
        self.get_pips("outdated")
        p_name = ret_package_data("temp_files/outdated_packs.txt", "name")

        self.create_packet_labels(p_name, "outdated")

    def but_installed_func(self):
        self.get_pips("installed")
        p_name = ret_package_data("temp_files/installed_packs.txt", "name")
        p_vers = ret_package_data("temp_files/installed_packs.txt", "vers")
        self.create_packet_labels(p_name, "installed")

    def get_pips(self, which_pip):
        try:
            if which_pip == "outdated":
                command = ['pip', 'list', '--outdated']
                f_name = 'outdated_packs.txt'
                print("outdate")
            else:
                command = ['pip', 'list']
                f_name = 'installed_packs.txt'
                print("installle")
            output = subprocess.check_output(command)
            output_str = output.decode('utf-8')
            lines = output_str.split('\n')[2:]
            output_str = '\n'.join(lines)

            with open(os.path.join('temp_files', f_name), 'w') as f:
                f.write(output_str)

        except subprocess.CalledProcessError as e:
            # Fehlermeldung speichern
            with open(os.path.join('temp_files', 'error.txt'), 'w') as f:
                f.write(str(e))

    @staticmethod
    def get_outdated_pips():
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
        self.json_data = {}
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

    def show_popup(self, popup_msg, tit="h"):
        popup = HelpPopup(popup_message=popup_msg)
        if tit == "h":
            popup.title = self.act_lab_txt["help_2"][self.act_lang]
        else:
            popup.title = self.act_lab_txt["information"][self.act_lang]

        popup.open()


if __name__ == '__main__':
    app = MainApp()

    app.run()
