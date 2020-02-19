#!/usr/bin/env python
"""
how to run the script with a doubleclick? (work with Gnome)

> sudo apt install dconf-editor (if it is not installed.)
> dconf-editor
> org -> gnome -> nautilus -> preferences -> executable-text-activation
> use default value -> off
> other value -> launch

"""

from bs4 import BeautifulSoup
import requests

soup = BeautifulSoup(requests.get(r"https://lowcygier.pl/darmowe/").text,"html.parser")
y = {x.text:x.get('href') for x in soup.find_all("a") if  "darmo" in str(x)}
y = { x:y[x] for x in y.keys()  if ('Store' in x or 'GOG' in x or 'Steam' in x) and 'darmowy' not in x and 'Darmowy' not in x}
print(y.keys())


"""
screen = Tk()
text = Text(screen)
text.pack()
text.insert(END,r.json()['data']['file']['url']['short'] if r.json()["status"] == True else r.text)

def apress(): #copy
    pyperclip.copy(r.json()['data']['file']['url']['short'])

btn = Button(screen, text = 'copy', width = 5, command = apress) 
btn.pack()


mainloop() """
