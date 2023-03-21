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
    if f_name == "outdated":
        f_name = "temp_files/outdated_packs.txt"
    else:
        f_name = "temp_files/installed_packs.txt"

    with open(f_name, "r") as f:
        temp_packet_list = f.readlines()
    return temp_packet_list


def set_output_txt(pip_command):
    # clear output.txt file
    tab = "            "
    with open(os.path.join('temp_files', "output.txt"), 'w') as f:
        f.write(f"[b]Package:[/b]{tab * 2}[b]Version:[/b]{tab}[b]Latest:[/b]{tab}[b]Type:[/b]\n")
    p_list = load_pack_list(pip_command)
    for i in range(len(p_list)):
        li_split = p_list[i].split()
        if pip_command == "outdated":
            with open(os.path.join('temp_files', "output.txt"), 'a') as f:
                f.write(
                    f"[ref={li_split[0]}]{li_split[0]}:[/ref]{tab * 3}{li_split[1]}{tab}{li_split[2]}{tab}{li_split[3]}{tab}\n")


def load_output_text():
    with open(os.path.join('temp_files', "output.txt"), 'r') as f:
        output_text = f.read()
    return output_text


def upgrade_pack(package_name):
    com = ["pip", "install", "--upgrade", package_name]
    subprocess.run(com)
    



class LinkLabel(Label):
    def on_ref_press(self, instance):
        app.act_package = instance
        app.show_popup(f"möchten sie das paket {instance} upgraden?", "inst")


class InfoPopup(Popup):
    popup_message = StringProperty('')  # The text to display in the popup message

    def __init__(self, popup_message, **kwargs):
        super().__init__(**kwargs)
        self.popup_message = popup_message

    def but_yes_func(self):
        print("yes button called")
        print(app.act_package)
        upgrade_pack(app.act_package)

class ScrMain(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.len_packet_list = None
        self.packet_list = None
        self.args_scr_one = None
        self.selected_package = ""

    def upd_scr_main(self, *args):
        self.args_scr_one = args

        self.ids.lab_actions_title.text = app.act_lab_txt["actions"][app.act_lang] + ":"
        self.ids.lab_output_title.text = app.act_lab_txt["output"][app.act_lang] + ":"
        self.ids.lab_list_installed.text = app.act_lab_txt["list installed packets"][app.act_lang]
        self.ids.lab_list_outdated.text = app.act_lab_txt["list outdated packets"][app.act_lang]

        self.ids.but_show_inst_packs.text = app.act_lab_txt["show packs"][app.act_lang]
        self.ids.but_show_outd_packs.text = app.act_lab_txt["show packs"][app.act_lang]
        self.ids.but_sett.text = app.act_lab_txt["settings"][app.act_lang]

    def but_package_func(self, which_pip):
        self.get_pips(which_pip)
        self.create_packet_labels()

    @staticmethod
    def get_pips(pip_com):
        try:
            if pip_com == "outdated":
                command = ['pip', 'list', '--outdated']
                f_name = 'outdated_packs.txt'
            else:
                command = ['pip', 'list']
                f_name = 'installed_packs.txt'
            output = subprocess.check_output(command)
            output_str = output.decode('utf-8')
            lines = output_str.split('\n')[2:]
            output_str = '\n'.join(lines)

            with open(os.path.join('temp_files', f_name), 'w') as f:
                f.write(output_str)
            set_output_txt(pip_com)
        except subprocess.CalledProcessError as e:
            # Fehlermeldung speichern
            with open(os.path.join('temp_files', 'error.txt'), 'w') as f:
                f.write(str(e))

    def create_packet_labels(self):
        lab_texts = load_output_text()
        self.ids.lab_scroll_view.text = lab_texts


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
        self.load_json_data()
        self.app_data = self.json_data["app_data"]
        self.act_lang = self.app_data["act_lang"]
        self.act_lab_txt = self.json_data["lab_txt"]

        self.act_b_col_n = self.app_data["colors"][self.app_data["act_col_n"]]
        self.act_b_col_d = self.app_data["colors"][self.app_data["act_col_d"]]
        self.act_package = ""

    def build(self):
        self.title = " "
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

    def load_json_data(self):
        with open("app_data.json", "r") as f:
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
        with open("app_data.json", "r") as f:
            data = json.load(f)
        data["app_data"]["act_lang"] = new_lang
        with open("app_data.json", "w") as f:
            json.dump(data, f)
        self.load_json_data()

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
