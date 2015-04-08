#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import platform
import subprocess

PLATFORM = platform.system()

if PLATFORM == 'Darwin':
    try:
        from Foundation import NSDate, NSUserNotification, NSUserNotificationCenter
        from AppKit import NSImage
        import objc
    except ImportError:
        pass


def send_notification(title="Douban.fm", content="", cover_file=None):
    '''发送桌面通知'''
    if PLATFORM == 'Linux':
        send_Linux_notify(title, content, cover_file)
    elif PLATFORM == 'Darwin':
        send_OS_X_notify(title, content, cover_file)


def send_Linux_notify(title, content, img_path):
    '''发送Linux桌面通知'''
    # Note: GNOME 下需要有任意的用户操作（鼠标、键盘等）才会自动隐藏通知
    command = [
        'notify-send',
        '-a', 'Douban.fm',  # 发送通知的应用名
        '-t', '5000',       # 自动隐藏的时间
        '--hint=int:transient:1',   # *建议* 桌面管理器不要保留通知
    ]
    if img_path is not None:
        command.extend(['-i', img_path])    # 图标
    subprocess.call(command + [title, content])


def send_OS_X_notify(title, content, img_path):
    '''发送Mac桌面通知'''
    def swizzle(cls, SEL, func):
        old_IMP = cls.instanceMethodForSelector_(SEL)

        def wrapper(self, *args, **kwargs):
            return func(self, old_IMP, *args, **kwargs)
        new_IMP = objc.selector(wrapper, selector=old_IMP.selector,
                                signature=old_IMP.signature)
        objc.classAddMethod(cls, SEL, new_IMP)

    def swizzled_bundleIdentifier(self, original):
        # Use iTunes icon for notification
        return 'com.apple.itunes'

    swizzle(objc.lookUpClass('NSBundle'),
            b'bundleIdentifier',
            swizzled_bundleIdentifier)
    notification = NSUserNotification.alloc().init()
    notification.setInformativeText_('')
    notification.setTitle_(title)
    notification.setSubtitle_(content)

    notification.setInformativeText_('')
    notification.setUserInfo_({})
    if img_path is not None:
        image = NSImage.alloc().initWithContentsOfFile_(img_path)
        # notification.setContentImage_(image)
        notification.set_identityImage_(image)
    notification.setDeliveryDate_(
            NSDate.dateWithTimeInterval_sinceDate_(0, NSDate.date())
    )
    NSUserNotificationCenter.defaultUserNotificationCenter().\
        scheduleNotification_(notification)


def main():
    send_notification(title='Test title', content='test content')

if __name__ == '__main__':
    main()
