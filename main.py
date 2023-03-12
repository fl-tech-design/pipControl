import subprocess

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager


class ScrMain(Screen):
    pass


class ScrSett(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class MainApp(App):
    def build(self):
        return WindowManager()

    @staticmethod
    def check_pip_outdated():
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


if __name__ == '__main__':
    app = MainApp()
    app.run()
