#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk
import requests
import random
import urllib.request
import xml.etree.ElementTree as ET
import tempfile
import os


class WaifuDownloader(Gtk.Application):

    def __init__(self):
        super().__init__(application_id="org.nyarch.waifu")

        self.posts = []
        self.current_url = None

    def do_activate(self):

        self.window = Gtk.Application(application=self)
        self.window = Gtk.ApplicationWindow(application=self)

        self.window.set_title("Nyarch Catgirl Style Downloader")
        self.window.set_default_size(1600, 1000)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        # 상단 컨트롤
        topbar = Gtk.Box(spacing=5)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("tag example: hololive")
        topbar.append(self.entry)

        search_btn = Gtk.Button(label="Search")
        search_btn.connect("clicked", self.search)
        topbar.append(search_btn)

        next_btn = Gtk.Button(label="Next")
        next_btn.connect("clicked", self.next_image)
        topbar.append(next_btn)

        download_btn = Gtk.Button(label="Download")
        download_btn.connect("clicked", self.download)
        topbar.append(download_btn)

        main.append(topbar)

        # 스크롤 영역
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        # 핵심: 자동 크기 조절 이미지
        self.picture = Gtk.Picture()

        # 창 크기에 맞게 자동 스케일
        self.picture.set_content_fit(Gtk.ContentFit.CONTAIN)

        scroll.set_child(self.picture)

        main.append(scroll)

        self.status = Gtk.Label(label="")
        main.append(self.status)

        self.window.set_child(main)
        self.window.present()

    def search(self, button):

        tag = self.entry.get_text().strip()

        if not tag:
            self.status.set_text("Enter tag")
            return

        url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&tags={tag}&limit=100"

        try:

            r = requests.get(url, timeout=15)
            root = ET.fromstring(r.text)

            self.posts = root.findall("post")

            if not self.posts:
                self.status.set_text("No images found")
                return

            self.status.set_text(f"{len(self.posts)} images found")

            self.next_image(None)

        except Exception as e:

            self.status.set_text(f"Error: {e}")

    def next_image(self, button):

        if not self.posts:
            self.status.set_text("Search first")
            return

        post = random.choice(self.posts)

        self.current_url = post.attrib["file_url"]

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")

        urllib.request.urlretrieve(self.current_url, tmp.name)

        # 이미지 표시 (창 크기에 자동 맞춤)
        self.picture.set_filename(tmp.name)

        self.status.set_text("Image loaded")

    def download(self, button):

        if not self.current_url:
            self.status.set_text("Load image first")
            return

        tag = self.entry.get_text().strip()

        folder = os.path.join(os.getcwd(), tag)
        os.makedirs(folder, exist_ok=True)

        filename = self.current_url.split("/")[-1]

        path = os.path.join(folder, filename)

        urllib.request.urlretrieve(self.current_url, path)

        self.status.set_text(f"Saved: {filename}")


app = WaifuDownloader()
app.run(None)

