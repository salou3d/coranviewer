#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '2.2.1'

import json
from os.path import join, exists
from os import listdir
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ListProperty, StringProperty, \
        NumericProperty, BooleanProperty, AliasProperty, DictProperty, ObjectProperty
from kivy.modules import keybinding
from kivy.core.window import Window
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.lang import Builder

#
class CoranDirectoryModalView(ModalView):

    text_input = ObjectProperty(None)
    coran_directory = StringProperty(None)

    def save(self, path, selection):
        with open(self.coran_directory, "w") as stream:
            stream.write( join( path, selection ))

#
class CoranDirectoryWidget(Widget):

    text_input = ObjectProperty(None)
    coran_directory = StringProperty(None)

    def open_view(self):
        cdmv = CoranDirectoryModalView(coran_directory=self.coran_directory)
        cdmv.open()

#
class CoranViewerWidget(Widget):

    coran_directory_path = StringProperty()
    pages = ListProperty()
    current_page = StringProperty()

    def __init__(self, **kwargs):
        super(CoranViewerWidget, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def get_count(self):
        return len(self.pages)

    def get_current_page(self):
        return self.current_page

    def set_current_page(self, page):
        self.current_page = page

    def get_page_path(self):
        return join( self.coran_directory_path, self.current_page)

    def get_page_number(self):
        return self.current_page.replace(".jpg", "")

    def get_label_text(self):
        return "/ {}".format(self.get_count())

    def disable_next(self):
        return self.pages.index(self.current_page) == len(self.pages) - 1

    def disable_previous(self):
        return self.pages.index(self.current_page) == 0

    def next_page(self):
        idx = self.pages.index(self.current_page) + 1
        if idx >= len(self.pages):
            idx = 0
        self.set_current_page( self.pages[idx] )
        self.ids.curr_page.source = join(self.coran_directory_path, self.current_page)
        self.ids.page_number.text = self.get_page_number()
        self.ids.b_next.disabled =  self.disable_next()
        self.ids.b_prev.disabled =  self.disable_previous()

    def previous_page(self):
        idx = self.pages.index(self.current_page) - 1
        self.set_current_page( self.pages[idx] )
        self.ids.curr_page.source = join(self.coran_directory_path, self.current_page)
        self.ids.page_number.text = self.get_page_number()
        self.ids.b_next.disabled =  self.disable_next()
        self.ids.b_prev.disabled =  self.disable_previous()

    def go_page(self, page):
        if len(page) < 3:
            new_p = ("0" * (3 - len(page))) + page + ".jpg"
        else:
            new_p = page + ".jpg"

        if new_p in self.pages:
            self.set_current_page(new_p)
            self.ids.curr_page.source = join(self.coran_directory_path, self.current_page)
            self.ids.page_number.text = self.get_page_number()
            self.ids.b_next.disabled =  self.disable_next()
            self.ids.b_prev.disabled =  self.disable_previous()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):

        if keycode[1] == 'left':
            self.previous_page()
        elif keycode[1] == 'right':
            self.next_page()
        elif keycode[1] == 'escape':
            keyboard.release()

        return True

#
class CoranViewer(App):

    coran_directory_path = StringProperty()
    current_page = StringProperty()

    def build(self):

        if not self.check_directory():
            self.title = "Choose a directory containning 'jpg' images of Coran"
            return CoranDirectoryWidget(coran_directory=self.coran_directory)
        else:
            self.coran_directory_path = self.get_coran_directory_path()

        pages = sorted( listdir( self.coran_directory_path ) )

        if self.check_last():
            self.current_page = self.get_last_page()
        else:
            self.current_page = pages[0]

        if not self.current_page:
            self.current_page = pages[0]

        self.title = "Coran Muhammadi Viewer"
        Window.maximize()
        return CoranViewerWidget(
            coran_directory_path=self.coran_directory_path,
            pages=pages,
            current_page=self.current_page )

    def check_last(self):
        return exists(self.last_page)

    def check_directory(self):
        return exists(self.coran_directory)

    def get_coran_directory_path(self):
        cdp = ""
        with open(self.coran_directory, "r") as fin:
            for line in fin:
                if line:
                    cdp = line.strip()
                    break
        return cdp

    def get_last_page(self):
        lpage = ""
        with open(self.last_page, "r") as fin:
            for line in fin:
                if line:
                    lpage = line.strip()
                    break
        return lpage

    def write_last_page(self):
        with open(self.last_page, "w") as fout:
            fout.write( self.current_page )

    def get_current_page(self):
        return self.current_page

    def on_stop(self):
        if self.current_page:
            self.write_last_page()

    @property
    def last_page(self):
        # last page or recent page
        return join(self.user_data_dir, 'last_page.txt')
    @property
    def coran_directory(self):
        return join(self.user_data_dir, 'coran_directory.txt')

if __name__ == '__main__':
    cv = CoranViewer()
    cv.run()
