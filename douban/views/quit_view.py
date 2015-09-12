
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
class Quit(Help):
    '''退出界面'''
    def __init__(self, win):
        self.win = win
        subprocess.check_call('clear', shell=True)
        self.screen_height, self.screen_width = self.linesnum()  # 屏幕显示行数
        self.display()
        self.run()

    def display(self):
        for i in range(self.screen_height):
            if i == self.screen_height / 2:
                print ' ' * ((self.screen_width - 18)/2) \
                    + red('Are you sure? (Y/n)'),
            else:
                print

    def run(self):
        '''界面执行程序'''
        c = getch.getch()
        if c == 'y' or c == 'Y' or ord(c) == 13:
            self.win.set_quit()
