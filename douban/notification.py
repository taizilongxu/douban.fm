#!/usr/bin/env python
# encoding: utf-8
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

def send_notification(title=None, content=None, cover_file=None):
    '''发送桌面通知'''
    if PLATFORM == 'Linux':
        send_Linux_notify(title, content, cover_file)
    elif PLATFORM == 'Darwin':
        send_OS_X_notify(title, content, cover_file)

def send_Linux_notify(title, content, img_path):
    '''发送Linux桌面通知'''
    subprocess.call(['notify-send', '-a', 'Douban.fm', '-t', '5000', '--hint=int:transient:1', '-i', img_path, title, content])

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
    notification.setTitle_(title.decode('utf-8'))
    notification.setSubtitle_(content.decode('utf-8'))

    notification.setInformativeText_('')
    notification.setUserInfo_({})
    image = NSImage.alloc().initWithContentsOfFile_(img_path)
    # notification.setContentImage_(image)
    notification.set_identityImage_(image)
    notification.setDeliveryDate_(
            NSDate.dateWithTimeInterval_sinceDate_(0, NSDate.date())
    )
    NSUserNotificationCenter.defaultUserNotificationCenter().\
        scheduleNotification_(notification)

def main():
    send_notification(title='1', content='1')

if __name__ == '__main__':
    main()
