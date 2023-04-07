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
from kivy.uix.screenmanager import Screen, ScreenManager

debug_stat = 0


def create_temp_files() -> None:
    """
    Creates a temporary directory named "temp_files" and three empty files inside it:
    "installed_packs.txt", "outdated_packs.txt", and "output.txt". If the directory or
    any of the files already exist, they will not be overwritten.

    Returns:
        None
    """
    temp_folder = "temp_files"
    file_names = ['output.txt']

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    for file_name in file_names:
        file_path = os.path.join(temp_folder, file_name)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("")


def set_app_data(data_key: str, data_value: str) -> None:
    """
    Updates the application configuration data in the app_config.json file.
    :param data_key: The key of the configuration data to update.
    :type data_key: str
    :param data_value: The new value to set for the configuration data.
    :type data_value: str
    :return: None
    """
    with open("config/app_config.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data[data_key] = data_value
    with open("config/app_config.json", "w", encoding="utf-8") as file:
        json.dump(data, file)
    AppConfig().load_app_config()


class AppConfig:
    def __init__(self):
        self.colors = {}
        self.app_data = {}
        self.act_lang = ""
        self.act_lab_txt = {}
        self.load_app_config()

    def load_app_config(self):
        """Loads the application configuration and translation files.

           Reads the contents of the "config/app_config.json" and "config/translations.json" files and stores them
           in the `app_data` and `act_lab_txt` instance variables, respectively. It also sets the `act_lang`,
           `button_col_norm`, and `button_col_down` instance variables based on the contents of `app_data`.

           Returns:
               None
           """
        with open("config/app_config.json", "r", encoding="utf-8") as data_file:
            a_data = json.load(data_file)
        with open("config/translations.json", "r", encoding="utf-8") as file:
            a_text = json.load(file)
        with open("config/colors.json", "r", encoding="utf-8") as col_file:
            self.colors = json.load(col_file)

        self.app_data = a_data
        self.act_lab_txt = a_text
        self.act_lang = self.app_data["act_lang"]

    def load_kv_files(self) -> None:
        """
            Loads all kv files from the 'kv_files' directory into the application.

            This function retrieves a list of kv files from the 'kv_files' directory using the get_data() function,
            and then loads each file using the Kivy Builder.load_file() method. This ensures that all kv files in
            the directory are loaded into the application, allowing them to be used in building the user interface.

            Returns:
                None
            """
        kv_file_list = self.app_data["kv_files"]
        for file in kv_file_list:
            Builder.load_file(file)

    def upgrade_pack(self, check_dependencies: bool = False) -> None:

        try:
            com = ["pip", "install", "--upgrade", self.app_data['act_pack']]
            if check_dependencies:
                com.append("--upgrade-strategy=eager")
            subprocess.check_call(com)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to upgrade package {self.app_data['act_pack']}") from e


class ButtonRoundedFilled:
    pass


class LabelLinked(Label):
    def on_ref_press(self, instance):
        set_app_data("act_pack", instance)
        app.show_popup_install(f"möchten sie das paket {instance} upgraden?")


class InfoPopup(Popup):
    """
       A Kivy Popup that displays an informational message.

       Attributes:
           popup_message (str): The text to display in the popup message.

       Methods:
           __init__(popup_message, **kwargs): Initializes the popup with the specified message.
           but_yes_func(): Placeholder method that is called when the "Yes" button is clicked.
       """
    popup_message = StringProperty('')  # The text to display in the popup message

    def __init__(self, popup_message, **kwargs):
        super().__init__(**kwargs)
        self.popup_message = popup_message
        self.act_lab_text = AppConfig().act_lab_txt


class PopupInstall(Popup):
    """
       A Kivy Popup that displays an informational message.

       Attributes:
           popup_message (str): The text to display in the popup message.

       Methods:
           __init__(popup_message, **kwargs): Initializes the popup with the specified message.
           but_yes_func(): Placeholder method that is called when the "Yes" button is clicked.
       """
    popup_message = StringProperty('')  # The text to display in the popup message

    def __init__(self, popup_message, **kwargs):
        super().__init__(**kwargs)
        self.popup_message = popup_message
        self.act_lab_text = AppConfig().act_lab_txt

    def but_func(self, cmd):
        if cmd == "yes":
            AppConfig().upgrade_pack()
            self.dismiss()
        else:
            self.dismiss()


def get_package_output_text():
    with open("temp_files/output.txt", "r", encoding="utf-8") as output_text_file:
        label_text = output_text_file.read()
    return label_text


class ScrMain(Screen):
    """
        A Kivy screen that displays the main interface of the app.

        Methods:
            upd_scr_main(*args): Updates the labels in the app's main interface.
            but_package_func(pip_cmd): Gets a list of installed or outdated pip packages.
            get_pips(pip_cmd): Helper method for but_package_func that runs a pip command and writes
            the output to a file.
        """

    def __init__(self, **kw):
        super().__init__(**kw)
        self.pip_comand = ""
        self.act_lab_txt = AppConfig().act_lab_txt
        self.act_lang = AppConfig().act_lang

    def upd_scr_main(self, *args):
        self.update_data()
        self.update_labels()
        self.ids.lab_output.text = get_package_output_text()
        if debug_stat:
            print(self.ids.box_scroll_view.size)
            print(self.ids.lab_output.height)
            print("args from upd_scr_main(): ", args)

    def update_data(self):
        self.act_lab_txt = AppConfig().act_lab_txt
        self.act_lang = AppConfig().act_lang

    def update_labels(self):
        self.ids.lab_actions_title.text = self.act_lab_txt["actions"][self.act_lang] + ":"
        self.ids.lab_output_title.text = self.act_lab_txt["output"][self.act_lang] + ":"
        self.ids.lab_list_installed.text = self.act_lab_txt["list installed packets"][self.act_lang]
        self.ids.lab_list_outdated.text = self.act_lab_txt["list outdated packets"][self.act_lang]
        self.ids.but_show_inst_packs.text = self.act_lab_txt["show packs"][self.act_lang]
        self.ids.but_show_outd_packs.text = self.act_lab_txt["show packs"][self.act_lang]
        self.ids.but_sett.text = self.act_lab_txt["settings"][self.act_lang]

    def but_pips_func(self, pip_cmd):
        self.get_pips(pip_cmd)

    def get_pips(self, pip_cmd):
        """
        Get a list of outdated pip packages. write the list to a txt file to show the scrollable text.

        Returns:
            None
        """
        self.pip_comand = pip_cmd
        command = ["pip", "list", pip_cmd]
        output_str = ""
        out_split_list = []
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if result.returncode == 0:
                output_lines = result.stdout.strip().split('\n')
                output_lines = output_lines[2:]
                for i in range(len(output_lines)):
                    out_split = output_lines[i].split()
                    if self.pip_comand == "--outdated":
                        out_str = f"[ref={out_split[0]}][color=#0000FF]{out_split[0]}[/color][/ref]    " \
                                  f"{out_split[1]}     {out_split[2]}    {out_split[3]}"
                    else:
                        out_str = f"{out_split[0]}    {out_split[1]}"
                    out_split_list.append(out_str)
                    output_str = '\n'.join(out_split_list)
                if not output_str:
                    output_str = "Alle Pakete aktuell"
                with open(Path("temp_files") / "output.txt", "w", encoding="utf-8") as tmp_file:
                    tmp_file.write(output_str)
            else:
                error_str = result.stderr.strip()
                with open(Path('temp_files') / 'error.txt', 'w', encoding="utf-8") as error_file:
                    error_file.write(error_str)
        except subprocess.SubprocessError as sub_error:
            with open(Path('temp_files') / 'error.txt', 'w', encoding="utf-8") as file_data:
                file_data.write(str(sub_error))
        Clock.schedule_once(app.scr_main.upd_scr_main)


class ScrSett(Screen):
    """
        A Kivy screen that displays and allows the user to update the app's settings.

        Attributes:
            args_scr_sett (tuple): The arguments passed to the screen.

        Methods:
            upd_scr_sett(*args): Updates all app_configs and label text in the app.
        """

    def __init__(self, **kw):
        super().__init__(**kw)
        self.args_scr_sett = None

    def upd_scr_sett(self, *args):
        """ updates all app_configs and label text in the app."""
        self.ids.tit_sett.text = AppConfig().act_lab_txt["settings"][AppConfig().act_lang]
        self.ids.tit_language.text = AppConfig().act_lab_txt["language"][AppConfig().act_lang]
        self.ids.but_french.text = AppConfig().act_lab_txt["french"][AppConfig().act_lang]
        self.ids.but_german.text = AppConfig().act_lab_txt["german"][AppConfig().act_lang]
        self.ids.but_greek.text = AppConfig().act_lab_txt["greek"][AppConfig().act_lang]
        self.ids.but_italian.text = AppConfig().act_lab_txt["italian"][AppConfig().act_lang]
        self.ids.but_spanish.text = AppConfig().act_lab_txt["spanish"][AppConfig().act_lang]
        self.ids.but_english.text = AppConfig().act_lab_txt["english"][AppConfig().act_lang]
        self.ids.but_back.text = AppConfig().act_lab_txt["back"][AppConfig().act_lang]
        if debug_stat:
            print(args)


class MainApp(App):
    """
     The main application class.

     This class inherits from the `kivy.app.App` class and implements the main functionality of the pip Control
     application. It contains methods for loading the application configuration and translation files, changing the
     current screen, changing the language of the application, and displaying popup windows. It also defines the `build`
     method, which creates and returns the root widget of the application.

     Attributes:
         scr_man (kivy.uix.screenmanager.ScreenManager): The screen manager object that manages the application screens.
         scr_main (ScrMain): The main screen object.
         scr_sett (ScrSett): The settings screen object.


     Methods:
         __init__(self, **kwargs): Initializes the `MainApp` instance and sets its initial state.
         build(self) -> kivy.uix.screenmanager.ScreenManager: Builds and returns the root widget of the application.
         load_app_config(self) -> None: Loads the application configuration and translation files.
         change_screen(self, trans: str, new_scr_name: str) -> None: Changes the current screen displayed by the
                                                                                                    application.
         change_language(self, new_language: str) -> None: Changes the language of the application by updating the
                                                                                                 configuration file.
         show_info_popup(self, popup_msg: str, tit: str = "help") -> None: Displays a popup window with a message.
     """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        create_temp_files()
        self.a_conf = AppConfig()
        self.a_conf.load_kv_files()
        self.scr_man, self.scr_main, self.scr_sett = (None,) * 3

    def build(self):
        self.title = "pip Control"
        self.scr_man = ScreenManager()

        self.scr_main = ScrMain()
        screen = Screen(name="scr_main")
        screen.add_widget(self.scr_main)
        self.scr_man.add_widget(screen)
        Clock.schedule_once(self.scr_main.upd_scr_main)

        self.scr_sett = ScrSett()
        screen = Screen(name="scr_sett")
        screen.add_widget(self.scr_sett)
        self.scr_man.add_widget(screen)
        Clock.schedule_once(self.scr_sett.upd_scr_sett)

        return self.scr_man

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

        Clock.schedule_once(self.scr_main.upd_scr_main)
        Clock.schedule_once(self.scr_sett.upd_scr_sett)

    @staticmethod
    def show_info_popup(popup_msg: str, tit: str = "help") -> None:
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
        if tit == "help":
            popup.title = AppConfig().act_lab_txt["help"][AppConfig().act_lang]

        else:
            popup.title = AppConfig().act_lab_txt["information"][AppConfig().act_lang]

        popup.open()

    @staticmethod
    def show_popup_install(popup_msg: str) -> None:
        """
        Displays a popup window with a message.

        :param popup_msg: The message to be displayed in the popup window.
        :type popup_msg: str

        :return: None.
        """
        popup = PopupInstall(popup_message=popup_msg)
        popup.title = AppConfig().act_lab_txt["install"][AppConfig().act_lang]

        popup.open()


if __name__ == '__main__':
    app = MainApp()
    app.run()
