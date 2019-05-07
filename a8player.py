#-*-coding:utf8;-*-
#qpy:2
#qpy:kivy
"""
This is an example file which tell you how to use QPython to develop android app.
If get a video link address from a remote webpage and play it with the A8 Player to play. ( It needs the network )

@Author: River
@Date: 2012-10-22
"""

from jnius import cast
from jnius import autoclass
from jnius import JavaException
from android import AndroidBrowser
from urllib2 import urlopen

print "[A8 Player with qpython example]"

# get and parse video link
response = urlopen('http://qpython.com/samples/script_data.txt')
if response:
    content = response.read()
    import json
    data = json.loads(content)
    link = data['link']

    # get android object
    PythonActivity = autoclass('org.renpy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    Toast = autoclass('android.widget.Toast')


    # play the url
    intent = Intent()
    intent.setAction(Intent.ACTION_VIEW)
    intent.setClassName('com.hipipal.mna8', 'com.hipipal.mna8.PLAPlayerAct')
    intent.setDataAndType(Uri.parse(link), 'video/*')
    currentActivity = cast('android.app.Activity', PythonActivity.mActivity)

    try:
        s = "Play Video: %s..." % link
        print s

        currentActivity.startActivity(intent)
    except JavaException:
        s = "Need install A8 Player App first"
        print s

        browser = AndroidBrowser()
        browser.open("http://play.tubebook.net/a8-video-player.html")

    print "[A8 Player with qpython END]"

else:

    print "Maybe network error, could not get the parameters for play"
