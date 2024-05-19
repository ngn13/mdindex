#!/bin/python3

"""
mdindex | markdown index generator script
Written by ngn (https://ngn.tf) (2024)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from sys import argv
import string

class Header:
    def __init__(self, level: int, content: str) -> None:
        self.content = content
        self.level = level
        self.children = []

    def get_title(self) -> str:
        title = self.content
        title = title.lower()
        title = title.replace(" ", "-")

        valid = string.ascii_lowercase+string.digits+"-"
        for c in title:
            if c in list(valid):
                continue
            title = title.replace(c, "")
        return title

    def __str__(self) -> str:
        indent = "\t"*(self.level-1)
        res = f"{indent}- [{self.content}]({'#'+self.get_title()})\n"
        for c in self.children:
            res += str(c)
        return res

    def add(self, child) -> None:
        if len(self.children) == 0:
            self.children.append(child)
            return

        if self.children[len(self.children)-1].level <= child.level:
            self.children.append(child)
            return

        self.children[len(self.children)-1].add(child)


class Mdindex:
    def __init__(self, data: str) -> None:
        self.begin_mark = "<!-- INDEX BEGIN -->"
        self.end_mark = "<!-- INDEX END -->"

        self.headers = []
        self.lock = False
        self.data = data

    def clean(self) -> None:
        lines = self.data.split("\n")
        clean = ""
        prev = ""

        for i in range(len(lines)):

            if self.begin_mark in lines[i]:
                self.lock = True
                continue

            if self.end_mark in lines[i]:
                prev = lines[i]
                continue

            if self.end_mark in prev:
                self.lock = False
                prev = lines[i]
                if len(lines[i]) == 0:
                    continue

            if not self.lock:
                if i == len(lines)-1:
                    clean += lines[i]
                else:
                    clean += lines[i]+"\n"

        self.lock = False
        self.data = clean


    def get_content(self, line: str) -> list:
        header = ""
        counter = 0

        while True:
            if not line.startswith(header+"#"):
                break
            header += "#"
            counter += 1

        if counter == 0:
            return []
        return [counter, line[len(header)+1:]]

    def checkline(self, line: str) -> Header:
        res = self.get_content(line)
        if len(res) != 2:
            raise Exception("not a header")
        header = Header(res[0], res[1])
        return header

    def gen(self) -> str:
        self.clean()

        for l in self.data.split("\n"):
            if "```" in l:
                self.lock = not self.lock
            if self.lock:
                continue
            try:
                header = self.checkline(l)
            except:
                continue

            if len(self.headers) == 0:
                self.headers.append(header)
                continue

            if header.level >= self.headers[len(self.headers)-1].level:
                self.headers.append(header)
                continue

            self.headers[len(self.headers)-1].add(header)

        gen = "<!-- INDEX BEGIN -->\n\n"
        for h in self.headers:
            gen += str(h)
        gen += "\n<!-- INDEX END -->\n\n"

        data = gen+self.data
        return data

if __name__ == "__main__":
    if len(argv) < 2:
        print(f"usage: {argv[0]} <file>")
        exit(1)

    try:
        f = open(argv[1], "r")
        data = f.read()
        f.close()
    except Exception as e:
        print(f"failed open the file: {e}")
        exit(1)

    try:
        mdindex = Mdindex(data)
        data = mdindex.gen()
    except Exception as e:
        print(f"failed to generate index list: {e}")
        exit(1)

    try:
        f = open(argv[1], "w")
        f.write(data)
        f.close()
    except Exception as e:
        print(f"failed to write to the file: {e}")
        exit(1)

    print("done")
    exit(0)
