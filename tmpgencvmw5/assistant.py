# coding: utf-8
import configparser
import autoit

# window
WINDOW_START = "[CLASS:TStart_MainForm]"
WINDOW_MAIN = "[CLASS:TMainForm]"
WINDOW_OPEN = "[CLASS:#32770]"
WINDOW_MESSAGE = "[CLASS:TMessageForm]"
WINDOW_EDIT = "[CLASS:TClipEditForm]"
# button
BUTTON_NEW_PROJECT = "[CLASS:TRLStyleButton; INSTANCE:2]"
BUTTON_ADD_FILE = "[CLASS:TRLStyleButton; INSTANCE:16]"
BUTTON_OPEN = "[CLASS:Button; INSTANCE:1]"
BUTTON_OK = "[CLASS:TRLStyleButton; INSTANCE:27]"
# form
FORM_PATH = "[CLASS:ToolbarWindow32; INSTANCE:2]"
FORM_FILE = "[CLASS:Edit; INSTANCE:1]"
FORM_CLIP_NAME = "[CLASS:TRLEdit_InplaceEdit; INSTANCE:4]"

CONFIG_FILE = './config.ini'


class Assistant:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE, encoding='utf-8')

    def launch_application(self):
        if not autoit.win_exists(WINDOW_START):
            autoit.run(self.config.get('exe', 'tmpgencvmw'))
            autoit.win_wait_active(WINDOW_START)
        autoit.win_activate(WINDOW_START)

    def open_new_project(self):
        autoit.control_click(WINDOW_START, BUTTON_NEW_PROJECT)
        autoit.win_wait_active(WINDOW_MAIN)

    def add_file(self, resource):
        # Open an add file window
        autoit.win_wait_active(WINDOW_MAIN)
        autoit.control_click(WINDOW_MAIN, BUTTON_ADD_FILE)

        # Open a file
        autoit.win_wait_active(WINDOW_OPEN)
        autoit.control_set_text(WINDOW_OPEN, FORM_FILE, resource.ts_file)
        autoit.control_click(WINDOW_OPEN, BUTTON_OPEN)

        # .............
        # Choose a clip
        # .............

        # Fill a clip name
        autoit.win_wait_active(WINDOW_EDIT)
        autoit.control_set_text(WINDOW_EDIT, FORM_CLIP_NAME, resource.name)
        autoit.control_click(WINDOW_EDIT, BUTTON_OK)

    def add_files(self, resources):
        self.launch_application()
        self.open_new_project()
        map(self.add_file, resources)
