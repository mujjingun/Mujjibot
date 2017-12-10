#! /usr/bin/env python
#
# Example program using irc.bot.
#
# Joel Rosdahl <joel@rosdahl.net>

"""A simple example bot.

This is an example bot that uses the SingleServerIRCBot class from
irc.bot.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.
It also responds to DCC CHAT invitations and echos data sent in such
sessions.

The known commands are:

    stats -- Prints some channel information.

    disconnect -- Disconnect the bot.  The bot will try to reconnect
                  after 60 seconds.

    die -- Let the bot cease to exist.

    dcc -- Let the bot invite you to a DCC CHAT connection.
"""

import bot
import random
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

answers = ["Yes", "No", "Basically", "This is a korean channel.", "#"]

class TestBot(bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667, password=""):
        bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.reactor.add_global_handler("all_events", self.dispatcher, -10)
        self.channel = channel
        self.password = password

    def dispatcher(self, connection, event):
        #print(event)
        pass
    
    def on_nicknameinuse(self, c, e):
        print(e)
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print(e)
        c.join(self.channel)
        self.connection.privmsg("NickServ", "IDENTIFY " + self.password)

    def on_privmsg(self, c, e):
        print(e)
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        print(e)
        
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        return

    def on_dccmsg(self, c, e):
        # non-chat DCC messages are raw bytes; decode as text
        text = e.arguments[0].decode('utf-8')
        print(text)
        c.privmsg("You said: " + text)

    def on_dccchat(self, c, e):
        print(e)
        if len(e.arguments) != 2:
            return
        args = e.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def do_command(self, e, cmd):
        print(cmd)
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die" or cmd == "kill yourself":
            c.privmsg(e.target, "goodbye cruel world!")
            c.action(e.target, "shoots itself *bang!*")
            self.die()
        elif cmd.lower() == "hi":
            c.privmsg(e.target, "Hi")
        elif "bot" in cmd.lower():
            c.privmsg(e.target, "I'm not a bot!");
        elif cmd.split()[0] == "repeat":
            c.privmsg(e.target, " ".join(cmd.split()[1:]).lower().replace("mujji", "you"))
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp("DCC", nick, "CHAT chat %s %d" % (
                ip_quad_to_numstr(dcc.localaddress),
                dcc.localport))
        elif cmd.endswith('!'):
            c.privmsg(e.target, '!!!!!')
        elif "not" in cmd or "'t" in cmd:
            c.privmsg(e.target, "Why not")
        else:
            ans = random.sample(answers, 1)[0]
            if ans != "#":
              c.privmsg(e.target, ans)
            else:
              c.privmsg(e.target, ' '.join(cmd.lower().split() + ['huh?']))

server = "irc.snoonet.org"
port = 6667
channel = '#test'
nickname = 'mujjibot'
password = '42684pass'

def main():
    import sys
    print(sys.argv)
    if len(sys.argv) != 5:
        print("Usage: testbot <server[:port]> <channel> <nickname> <password>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]
    password = sys.argv[4]

    bot = TestBot(channel, nickname, server, port, password)
    print("start")
    bot.start()

if __name__ == "__main__":
    main()
