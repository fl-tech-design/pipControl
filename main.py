import json
import os
import subprocess
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen, ScreenManager

debug_stat = 0


def load_kv_files():
    if debug_stat:
        print("load_kv_files() called...")
    Builder.load_file("kv_files/main.kv")
    Builder.load_file("kv_files/scr_main.kv")
    Builder.load_file("kv_files/scr_sett.kv")
    Builder.load_file('kv_files/pop_help.kv')
    Builder.load_file('config/colors.kv')
    Builder.load_file('config/components.kv')


def create_temp_files():
    if debug_stat:
        print("create_temp_files() called:")
    temp_folder = "temp_files"
    file_names = ["installed_packs.txt", "outdated_packs.txt", 'output.txt']

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    for file_name in file_names:
        file_path = os.path.join(temp_folder, file_name)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("")


def ret_temp_pack_file(file_name: str) -> [str]:
    """
    Reads a text file containing packet data from the 'temp_files' directory with the given file name,
    and returns a list of strings, where each string is a line in the file.

    Args:
    - file_name (str): The name of the file to be read, without the '.txt' extension.

    Returns:
    - temp_packet_list (List[str]): A list of strings representing the lines of the file.

    """

    f_name = f"temp_files/{file_name}_packs.txt"
    with open(f_name, "r") as f:
        temp_packet_list = f.readlines()
    if debug_stat:
        print(f_name)
        print("temp_packet_list from ret_temp_pack_file():\n", temp_packet_list)
    return temp_packet_list


def upgrade_pack(package_name):
    com = ["pip", "install", "--upgrade", package_name]
    subprocess.Popen(com)


class Table(RelativeLayout):
    def create_table(self, file_name):
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


class InfoPopup(Popup):
    popup_message = StringProperty('')  # The text to display in the popup message

    def __init__(self, popup_message, **kwargs):
        super().__init__(**kwargs)
        self.popup_message = popup_message

    @staticmethod
    def but_yes_func():
        if debug_stat:
            print("but_yes_func called...")
        upgrade_pack(app.act_package)


class ScrMain(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.args_scr_main = None
        self.table = Table()
        self.table.create_table("installed")

    def upd_scr_main(self, *args):
        self.args_scr_main = args
        self.ids.lab_actions_title.text = app.act_lab_txt["actions"][app.act_lang] + ":"
        self.ids.lab_output_title.text = app.act_lab_txt["output"][app.act_lang] + ":"
        self.ids.lab_list_installed.text = app.act_lab_txt["list installed packets"][app.act_lang]
        self.ids.lab_list_outdated.text = app.act_lab_txt["list outdated packets"][app.act_lang]
        self.ids.but_show_inst_packs.text = app.act_lab_txt["show packs"][app.act_lang]
        self.ids.but_show_outd_packs.text = app.act_lab_txt["show packs"][app.act_lang]
        self.ids.but_sett.text = app.act_lab_txt["settings"][app.act_lang]

    def but_package_func(self, pip_cmd):
        self.get_pips(pip_cmd)

    @staticmethod
    def get_pips(pip_cmd):
        """
        Get a list of installed or outdated pip packages.

        Args:
            pip_cmd (str, optional): Command to run. Can be either "outdated" to get outdated packages or
            "installed" to get installed packages. Defaults to "installed".

        Returns:
            None
        """

        try:
            if pip_cmd == "outdated":
                command = ['pip', 'list', '--outdated']
                filename = 'outdated_packs.txt'
            else:
                command = ['pip', 'list']
                filename = 'installed_packs.txt'
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                output_lines = result.stdout.strip().split('\n')[2:]  # die ersten beiden Zeilen entfernen
                output_str = '\n'.join(output_lines)

                if not output_str:
                    output_str = "Alle Pakete aktuell"
                with open(Path('temp_files') / filename, 'w') as f:
                    f.write(output_str)
            else:
                error_str = result.stderr.strip()
                with open(Path('temp_files') / 'error.txt', 'w') as f:
                    f.write(error_str)
        except subprocess.SubprocessError as e:
            with open(Path('temp_files') / 'error.txt', 'w') as f:
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
    """
     The main application class.

     This class inherits from the `kivy.app.App` class and implements the main functionality of the pip Control
     application. It contains methods for loading the application configuration and translation files, changing the
     current screen, changing the language of the application, and displaying popup windows. It also defines the `build`
     method, which creates and returns the root widget of the application.

     Attributes:
         act_package (str): The name of the currently selected package.
         app_config (dict): The application configuration loaded from the "config/app_config.json" file.
         app_data (dict): The application data loaded from the "config/app_config.json" file.
         act_lab_txt (dict): The translation strings loaded from the "config/translations.json" file.
         act_lang (str): The currently selected language code.
         scr_man (kivy.uix.screenmanager.ScreenManager): The screen manager object that manages the application screens.
         scr_main (ScrMain): The main screen object.
         scr_sett (ScrSett): The settings screen object.
         button_col_norm (tuple): The color tuple for normal buttons.
         button_col_down (tuple): The color tuple for pressed buttons.
         act_font_l (str): The name of the currently selected light font.
         act_font_d (str): The name of the currently selected dark font.

     Methods:
         __init__(self, **kwargs): Initializes the `MainApp` instance and sets its initial state.
         build(self) -> kivy.uix.screenmanager.ScreenManager: Builds and returns the root widget of the application.
         load_app_config(self) -> None: Loads the application configuration and translation files.
         change_screen(self, trans: str, new_scr_name: str) -> None: Changes the current screen displayed by the
                                                                                                    application.
         change_language(self, new_language: str) -> None: Changes the language of the application by updating the
                                                                                                 configuration file.
         show_popup(self, popup_msg: str, tit: str = "help") -> None: Displays a popup window with a message.
     """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("__init__() called...")
        create_temp_files()
        load_kv_files()
        self.act_package = ""
        self.app_config = {}
        self.app_data = {}
        self.act_lab_txt = {}
        self.load_app_config()
        self.act_lang = self.app_data["act_lang"]

        self.scr_man, self.scr_main, self.scr_sett = (None,) * 3

        self.button_col_norm = self.app_data["colors"][self.app_data["but_col_n"]]
        self.button_col_down = self.app_data["colors"][self.app_data["but_col_d"]]
        self.act_font_l = self.app_data["font_light"]
        self.act_font_d = self.app_data["font_dark"]

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
        """Loads the application configuration and translation files.

           Reads the contents of the "config/app_config.json" and "config/translations.json" files and stores them
           in the `app_data` and `act_lab_txt` instance variables, respectively. It also sets the `act_lang`,
           `button_col_norm`, and `button_col_down` instance variables based on the contents of `app_data`.

           Returns:
               None
           """
        with open("config/app_config.json", "r", encoding="utf-8") as file:
            a_data = json.load(file)
        with open("config/translations.json", "r", encoding="utf-8") as file:
            a_text = json.load(file)

        self.app_data = a_data
        self.act_lab_txt = a_text
        self.act_lang = self.app_data["act_lang"]
        self.button_col_norm = self.app_data["colors"][self.app_data["but_col_n"]]
        self.button_col_down = self.app_data["colors"][self.app_data["but_col_d"]]

    def change_screen(self, trans: str, new_scr_name: str) -> None:
        """
        Changes the current screen displayed by the application.

        :param trans: The transition direction for the screen change.
        :type trans: str
        :param new_scr_name: The name of the new screen to display.
        :type new_scr_name: str
        :return: None.
        :rtype: None
        """
        self.scr_man.transition.direction = trans
        self.scr_man.current = new_scr_name

    def change_language(self, new_language: str) -> None:
        """
        Changes the language of the application by updating the configuration file.

        :param new_language: The new language code to set the application to.
        :type new_language: str
        :return: None.
        :rtype: None
        """
        with open("config/app_config.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        data["act_lang"] = new_language
        with open("config/app_config.json", "w", encoding="utf-8") as file:
            json.dump(data, file)
        self.load_app_config()

    def show_popup(self, popup_msg: str, tit: str = "help") -> None:
        """
        Displays a popup window with a message.

        :param popup_msg: The message to be displayed in the popup window.
        :type popup_msg: str
        :param tit: The title of the popup window. The default value is 'help', which stands for Help.
                   If the title is 'install', an installation popup will be displayed.
                   If the title is not 'help' or 'install', an information popup will be displayed.
        :type tit: str
        :return: None.
        :rtype: None
        """
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
