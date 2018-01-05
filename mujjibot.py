#! /usr/bin/env python3
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
import conj

answers = ["Yes", "No", "Basically", "This is a korean channel.", "#"]

class BattleNick:
  def __init__(self, nick):
    self.nick = nick
    self.hp = 100
    n = random.randint(0, 3)
    if n == 0:
      n = random.randint(0, 3)
    if n == 0:
      n = random.randint(0, 3)
    self.items = random.sample(["stick", "gun", "scissors"], n)
    print(self.items)

  def ask(self, c, e):
    if len(self.items) == 0: itemstr = "nothing. Say cheese to skip your turn."
    else: itemstr = ", and ".join(["a " + s for s in self.items]) + ". What will you use?"
    c.privmsg(e.target, "{}: it's your turn! You have {}".format(
      self.nick, itemstr))

class TestBot(bot.SingleServerIRCBot):
  def __init__(self, channel, nickname, server, port=6667, password=""):
    bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
    self.reactor.add_global_handler("all_events", self.dispatcher, -10)
    self.channel = channel
    self.password = password
    self.on_battle = False
    self.battlenicks = [None, None]

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
    b = e.arguments[0].split(" ", 1)
    if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
      self.do_command(e, a[1].strip())
    elif len(b) > 1 and irc.strings.lower(b[0]) == irc.strings.lower(self.connection.get_nickname()):
      self.do_command(e, b[1].strip())
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

  def battle(self, e, cmd):
    nick = e.source.nick
    c = self.connection
    if self.on_battle:
      you = self.battlenicks[1]
      opp = self.battlenicks[0]
      if cmd == "end battle":
        self.on_battle = False
        c.privmsg(e.target, "Battle over. No one wins.")
        return True
      elif nick == you.nick or nick == "mujji":
        if cmd == "stick":
          if "stick" not in you.items:
            c.privmsg(e.target, "{}: You don't have any sticks. You should be ashamed of yourself.".format(you.nick))
          else:
            r = random.randint(0, 99)
            if r < 15:
              c.privmsg(e.target, "{}: You poke {} with the stick. {} pokes back.".format(you.nick, opp.nick, opp.nick))
            elif r < 20:
              c.privmsg(e.target, "{}: You pull out your \"stick\". {} stares at it in horror.".format(you.nick, opp.nick))
            elif r < 80:
              c.privmsg(e.target, "{}: Thwack! You hit {} with the stick. {} takes 30 damage.".format(you.nick, opp.nick, opp.nick))
              opp.hp -= 30
            else:
              c.privmsg(e.target, "{}: You accidentally stab yourself with the stick. You take 30 damage.".format(you.nick))
              you.hp -= 30
        elif cmd == "gun":
          if "gun" not in you.items:
            c.privmsg(e.target, "{}: You don't have a gun tho...".format(you.nick))
          else:
            r = random.randint(0, 99)
            if r < 10:
              c.privmsg(e.target, "{}: The gun's jammed! You'll have to wait another turn. Dangit!".format(you.nick))
            elif r < 20:
              c.privmsg(e.target, "{}: The gun is out of ammo! You'll have to wait another turn. Dangit!".format(you.nick))
            elif r < 60:
              c.privmsg(e.target, "{}: Headshot! {} dies.".format(you.nick, opp.nick))
              opp.hp -= 100
            elif r < 80:
              c.privmsg(e.target, "{}: Bang! You missed!".format(you.nick))
            else:
              c.privmsg(e.target, "{}: You somehow managed to shoot yourself! You die.".format(you.nick))
              you.hp -= 100
        elif cmd == "scissors":
          if "scissors" not in you.items:
            c.privmsg(e.target, "{}: You don't have any scissors. You just wasted your turn. Just like that.".format(you.nick))
          else:
            r = random.randint(0, 99)
            if r < 10:
              c.privmsg(e.target, "{}: You stab {} with the scissors. Unfortunately {}'s skin is too thick to penetrate.".format(you.nick, opp.nick, opp.nick))
            elif r < 30:
              c.privmsg(e.target, "{}: Scissors? Seriously?".format(you.nick))
            elif r < 50:
              c.privmsg(e.target, "{}: You throw the scissors at {}. It lands in front of {}'s feet. {} picks it up.".format(you.nick, opp.nick, opp.nick, opp.nick))
              you.items.remove("scissors")
              opp.items.append("scissors")
            else:
              c.privmsg(e.target, "{}: You stab {}. {} takes 50 damage.".format(you.nick, opp.nick, opp.nick))
              opp.hp -= 50
        elif cmd == "cheese":
          c.privmsg(e.target, "{}: Unable to do anything, you fall on the floor crying.".format(you.nick))
          pass
        else:
          c.privmsg(e.target, "{}: Focus on the battle!".format(you.nick))
        if opp.hp <= 0:
          c.privmsg(e.target, "Battle over! {} is dead! {} wins!".format(opp.nick, you.nick))
          self.on_battle = False
        elif you.hp <= 0:
          c.privmsg(e.target, "Battle over! {} is dead! {} wins!".format(you.nick, opp.nick))
          self.on_battle = False
        else:
          c.privmsg(e.target, "{}: {} HP, {}: {} HP".format(you.nick, you.hp, opp.nick, opp.hp))
          self.battlenicks = self.battlenicks[-1:] + self.battlenicks[:-1]
          self.battlenicks[1].ask(c, e)
        return True
    elif cmd.startswith("battle"):
      if len(cmd.split()) == 2:
        self.on_battle = True
        self.battlenicks = [BattleNick(nick), BattleNick(cmd.split()[1])]
        c.privmsg(e.target, "Ding ding ding! The battle between {} and {} has commenced!".format(nick, cmd.split()[1]))
        self.battlenicks[1].ask(c, e)
      elif len(cmd.split()) == 1:
        c.privmsg(e.target, "{}: You can't battle yourself.".format(nick))
      else:
        c.privmsg(e.target, "{}: You're not Chuck Norris, handle them one at a time.".format(nick))
      return True
    return False
    
  def do_command(self, e, cmd):
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
    elif self.battle(e, cmd):
      pass
    elif cmd.startswith("conj"):
      conj.conj(c, e, cmd)
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

def main():
  random.seed()
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
