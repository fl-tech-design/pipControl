import subprocess

from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager


class HyperlinkLabel(ButtonBehavior, Label):
    url = StringProperty()

    def on_release(self):
        if self.url:
            Window.open(self.url)


class ScrMain(Screen):
    pass


class ScrSett(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.li_package_name = []

    def build(self):
        return WindowManager()

    def check_pip_outdated(self):
        print("check outgradet")
        command = ['pip', 'list', '--outdated']
        output = subprocess.check_output(command)
        if output.strip():
            with open('old_packs.txt', 'w') as f:
                f.write(output.decode('utf-8'))
            print("veraltete Paket wurden in datei gespeichert")
        else:
            with open('old_packs.txt', 'w') as f:
                f.write("Es gibt keine veralteten Pakete.")
            print("Es gibt keine veralteten Pakete.")
        print(output.decode("utf-8"))
        self.get_outdated_package_name()

    def get_outdated_package_name(self):
        with open('outdated_packages.txt', 'r') as file:
            self.li_package_name = [line.split()[0] for line in file.readlines()[2:]]
        print(self.li_package_name)
    def link_clicked(self, link):
        if link == 'world':
            print('World clicked')

if __name__ == '__main__':
    app = MainApp()

    app.run()
