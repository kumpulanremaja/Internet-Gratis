#-*-coding:utf8;-*-
#qpy:console
#qpy:2
"""
This is an example file which tell you how to use QPython to develop android app.
It use the SL4A feature

@Author: River
@Date: 2012-12-31
"""
import androidhelper
droid = androidhelper.Android()
line = droid.dialogGetInput()
s = "Hello, %s" % (line.result,)
droid.makeToast(s)
