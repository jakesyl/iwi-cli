#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, socket, random, string, time, logging, threading, ConfigParser, feedparser, os, curses, curses.textpad, locale
from time import gmtime, strftime
global HOST, PORT, NICK, IDENT, REALNAME, CHAN, TIMEOUTTIME, PING, PLUGINFILE, MASTERS, counter, TrueMaster, NoticeMsgOnChannelJoin, NoticeMsgOnChannelJoinOn, HighLight, counter2, nw
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
counter = 0
counter2 = 0
locale.setlocale(locale.LC_ALL,"")
screen = curses.initscr()
pad = curses.newpad(24, 80)
pad.idlok(1)
pad.scrollok(1)
pad.nodelay(1)
pad.syncok(1)
pad.timeout(0)
curses.noecho()
pad_pos = 0
curses.curs_set(0)

def fetchSettings():
    config = ConfigParser.ConfigParser()
    config.read('configirc.ini')
    try:
        global HOST, PORT, NICK, IDENT, REALNAME, CHAN, TIMEOUTTIME, PING, PLUGINFILE, MASTERS, counter, TrueMaster, NoticeMsgOnChannelJoin, NoticeMsgOnChannelJoinOn, HighLight
        HOST = config.get('Server', 'Server')
        PORT = int(config.get('Server', 'Port'))
        CHAN = config.get('Server', 'Channel')

        NICK = config.get('Bot', 'Nick')
        IDENT = config.get('Bot', 'Ident')
        REALNAME = config.get('Bot', 'RealName')

        NoticeMsgOnChannelJoin = config.get('Messages', 'WelcomeMsg')
        NoticeMsgOnChannelJoinOn = config.get('Messages', 'WelcomeMsgActive')
        PING = config.get('Messages', 'OutputPing')
        HighLight = config.get('Messages', 'HighlightPhrases').split(',')

        TIMEOUTTIME = float(config.get('Settings', 'SocketDelay'))
        PLUGINFILE = config.get('Settings', 'PluginFile')
        TrueMaster = config.get('Settings', 'BotOwner')
        MASTERS = config.get('Settings', 'Masters').replace(' ', '').split(',')


    except:
            print "[!] Error have happened while fetching settings from configirc.ini!"
            sys.exit(1)

def maketextbox(h,w,y,x,value="",deco=None,textColorpair=0,decoColorpair=0):
    # thanks to http://stackoverflow.com/a/5326195/8482 for this
    global nw
    nw = curses.newwin(h,w,y,x)
    txtbox = curses.textpad.Textbox(nw,insert_mode=True)
    if deco=="frame":
        screen.attron(decoColorpair)
        curses.textpad.rectangle(screen,y-1,x-1,y+h,x+w)
        screen.attroff(decoColorpair)
    elif deco=="underline":
        screen.hline(y+1,x,underlineChr,w,decoColorpair)
 
    nw.addstr(0,0,value,textColorpair)
    nw.attron(textColorpair)
    screen.refresh()
    return nw,txtbox
textwin,textbox = maketextbox(1,79, 23,1,"")

def multi_detect(string, inputArray):
    for item in inputArray:
        if item in string:
            print '\a'
            return 1
    return 0

def print_date(msg):
    global counter2
    screen.refresh()
    pad.refresh(0,0, 0,0, 22,80)
    unix = msg.decode('utf-8', 'ignore')
    msg = unix.encode('utf-8', 'ignore')
    #pad.addstr(strftime("[*] [%H:%M:%S] "+msg+'\n', gmtime()))
    if(counter2 == 21):
        if(len(msg) >= 80):
            pad.scrollok(1)
            pad.scroll(1)
            pad.idlok(1)
        if(len(msg) >= 160):
            pad.scrollok(1)
            pad.scroll(1)
            pad.idlok(1)
            pad.scrollok(1)
            pad.scroll(1)
            pad.idlok(1)
        if(len(msg) >= 240):
            pad.scrollok(1)
            pad.scroll(1)
            pad.idlok(1)
            pad.scrollok(1)
            pad.scroll(1)
            pad.idlok(1)
            pad.scrollok(1)
            pad.scroll(1)
            pad.idlok(1)
        if(len(msg) >= 320):
            pad.scrollok(1)
            pad.scroll(1)
            pad.idlok(1)
            pad.scrollok(1)
            pad.scroll(1)
            pad.idlok(1)
            pad.scrollok(1)
            pad.scroll(1)
            pad.idlok(1)
            pad.scrollok(1)
            pad.scroll(1)
            pad.idlok(1)
        else:
            pad.scrollok(1)
            pad.idlok(1)
    elif(counter2 != 21):
        counter2 += 1
    else:
        pass
    screen.refresh()
    pad.refresh(0,0, 0,0, 22,80)
    pad.addstr(strftime("[*] [%H:%M:%S] "+msg+"\n", gmtime()))
    screen.refresh()
    pad.refresh(0,0, 0,0, 22,80)
    
class Irc:
    def __init__(self):
        self.onChannelMsg = 'Sup cunts.'
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lastHL = 'Null'
    def send(self, msg):
        self.socket.send(msg + "\r\n")
    def sendMsg(self, chan, msg):
        self.socket.send('PRIVMSG '+chan+' :'+msg+'\r\n')
        print_date('[%s] to <%s>: %s' % (NICK, chan, msg))

    def connect(self):
        #config_fetch()# just couldn't get it to work
        #logging section
        self.logger = logging.getLogger('myapp')
        self.hdlr = logging.FileHandler('socket.log')
        self.formatter = logging.Formatter('[*] [%(asctime)s] %(message)s', datefmt='%H:%M:%S')
        self.hdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.hdlr)
        self.logger.setLevel(logging.INFO)
        pad.scroll(3)
        self.socket.connect((HOST, PORT))
        self.send("NICK %s" % NICK)
        self.send("USER %s %s bla :%s" % (IDENT, HOST, REALNAME))
        time.sleep(5)
        self.send("JOIN %s" % (CHAN))
        self.socket.settimeout(TIMEOUTTIME)
        time.sleep(2)
        self.send("PRIVMSG #polish :Joined. Hi.")
    def whileSection(self):
        while True:
            screen.refresh()
            pad.refresh(0,0, 0,0, 22,80)
            try:
                readbuffer = self.socket.recv(1024)
            except:
                readbuffer = ""
            temp = string.split(readbuffer, "\n")
            for line in temp:
                try:
                    if not line:
                        break
                    line = string.rstrip(line)
                    self.logger.info(str(line))
                    line = string.split(line)
                    if line[0] == "PING":
                        self.send("PONG %s" % line[1])
                        if PING:
                            print_date("Pinged and ponged.")
                        else:
                            pass
                    if line[1] == "PRIVMSG":
                        channel = line[2]
                        message = (' '.join(line[3:]))[1:]
                        username = (line[0].split('!')[0])[1:]
                        hld = multi_detect(message, HighLight)
                        if hld:
                            self.lastHL = username
                        print_date("[%s] to <%s>: %s" % (username, channel, message))
                        execfile(PLUGINFILE)
                    elif line[1] == "JOIN":
                        username = (line[0].split('!')[0])[1:]
                        if NoticeMsgOnChannelJoinOn == 1:
                            self.send("NOTICE "+username+" :"+NoticeMsgOnChannelJoin)
                        print_date("[%s] joined the channel <%s>" % (username, ' '.join(line[2:])[1:]))
                    elif line[1] == "QUIT":
                        username = (line[0].split('!')[0])[1:]
                        print_date("[%s] has quit: %s" % (username, ' '.join(line[2:])[1:]))
                    elif line[1] == "PART":
                        username = (line[0].split('!')[0])[1:]
                        channel = line[2]
                        print_date("[%s] leaves from <%s>" % (username, channel))
                    else:
                        '''meineText = ' '.join(line)
                        pad.addstr(' '.join(line)+'\n')
                        if(len(meineText) > 80):
                            pad.scroll(2)
                        elif(len(meineText) > 160):
                            pad.scroll(3)
                        elif(len(meineText) > 160+80):
                            pad.scroll(4)
                        else:
                            pad.scroll(1)'''
                        pad.refresh(0,0, 0,0, 22,80)
                        pass
                except IndexError:
                    pass

IrcC = Irc()

class IrcThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        IrcC.connect()
        IrcC.whileSection()


class InputThreadIrc (threading.Thread):
    def __init__(self):
        global CHAN
        threading.Thread.__init__(self)
        #socket_x1.fetchSettings()
        self.lastMessage = [CHAN, '']
        self.messages = {}
        self.variables = {}

    def run(self):
        global CHAN
        while 1:
            try:
                curses.curs_set(1)
                self.line2 = textbox.edit()
                unix = self.line2.decode('utf-8', 'ignore')
                self.line2 = unix.encode('utf-8', 'ignore')
            except KeyboardInterrupt:
                break
            execute, specialChan = True, CHAN
            self.variables['hl'] = IrcC.lastHL
            self.variables['lm'] = self.lastMessage[1]
            if(self.line2[0] == ':'):
                inputArray = self.line2.replace('\n', '').split(' ')
                command = inputArray[0]
                command = command[1:]
                if command == 'q': # quit
                    curses.endwin()
                    os._exit(1)
                    break
                elif command == 'l': # last message, eventual append
                    self.line2 = self.lastMessage[1]
                    specialChan = self.lastMessage[0]
                    if len(inputArray) > 1:
                        self.line2 = self.line2 + ' ' + ' '.join(inputArray[1:])
                        self.line2 = self.line2.replace('\n', '')
                elif command == 'p': # private message to specified user/chan
                    specialChan = inputArray[1]
                    self.line2 = ' '.join(inputArray[2:])
                elif command == 'r': # raw input to server
                    execute = False
                    IrcC.send(' '.join(inputArray[1:]))
                elif command == 'j': # join to a channel
                    execute = False
                    IrcC.send('JOIN '+inputArray[1])
                elif command == 'ch': # changes channel
                    socket_x1.CHAN = inputArray[1]
                    CHAN = inputArray[1]
                    execute = False
                elif command == 'ms': # sets a message to reuse
                    self.messages[inputArray[1]] = ' '.join(inputArray[2:])
                    execute = False
                elif command == 'md': # displays a message
                    if inputArray[1] in self.messages:
                        self.line2 = self.messages[inputArray[1]]
                    else:
                        execute = False
                elif command == 'vs': # sets a variable
                    self.variables[inputArray[1]] = ' '.join(inputArray[2:])
                    execute = False
                elif command == 'v': # sends a message with variables
                    words = inputArray[1:]
                    new_msg = ''
                    for word in words:
                        if word[0] == '$':
                            wording = word[1:].replace(',', '')
                            wording = wording.replace(':', '')
                            if wording in self.variables:
                                new_msg += self.variables[wording]
                            if word[-1] == ',':
                                new_msg += ','
                            elif word[-1] == ':':
                                new_msg += ':'
                        else:
                            new_msg += word
                        new_msg += ' '
                    self.line2 = new_msg
            if execute:
                IrcC.logger.info(" ["+NICK+"] "+self.line2+" to "+specialChan+":")
                IrcC.sendMsg(specialChan, self.line2)
                self.lastMessage[1] = self.line2
                self.lastMessage[0] = specialChan
            nw.clear()
            screen.refresh()
            nw.refresh()
fetchSettings()

thread1 = IrcThread()
thread2 = InputThreadIrc()
thread2.daemon = 1

thread1.start()
thread2.start()


