#!/usr/local/bin/python3

import imaplib
import time
from os.path import expanduser, abspath

DoMail2 = True
DoDebug = False
DoPort = True


#print mail.list()
# Out: list of "folders" aka labels in gmail.
#print ncount

def get_access(filename):
    accf = open(filename, 'r')
    servers = []
    for line in accf:
        servers.append(line.rstrip().split(','))
    return servers    

def get_stats(address, account, passw, port):
    if (DoDebug):
        print('doing:',address, account, passw, port)
    if (DoPort):
        mail = imaplib.IMAP4_SSL(address,str(port))    
    else:
        mail = imaplib.IMAP4_SSL(address)
    mail.login(account, passw)
    result, data = mail.select("inbox") # connect to inbox

    stats = {}
    stats['mai'] = account
    result, data = mail.search(None, "ALL")
    count = 0
    if (data[0]): count = len(data[0].split())
    stats['all'] = count
    
    result, data = mail.search(None,'UnSeen')
    #print('debug:',data,type(data[0]))
    #print(len(data),'<->',data[0])
    count = 0
    if (data[0]): count = len(data[0].split())
    #print('works:',myans)
    stats['new'] = count
    
    result, data = mail.search(None,'Deleted')
    count = 0
    if (data[0]): count = len(data[0].split()) 
    stats['del'] = count
    
    result, data = mail.search(None,'Flagged') 
    count = 0
    if (data[0]): count = len(data[0].split())    
    stats['flg'] = count

    return stats

def make_entry(file, time, s1, s2):

    timeString  = time.strftime("%d/%m/%Y,%H:%M,", localtime)
    file.write(timeString)
    file.write('{},{},{},{},'.format(s1['all'],s1['del'],s1['new'],s1['flg']))
    file.write('{},{},{},{}'.format(s2['all'],s2['del'],s2['new'],s2['flg']))
    file.write('\n')
    return



localtime   = time.localtime()
#print localtime
filedate = time.strftime("%Y%m%d", localtime)

filepath = abspath(expanduser("~/") + 'Mailmon/HuibMail'+filedate+'.csv')

access = get_access(expanduser("~/")+'.ssh/mailmon')

res = open(filepath, 'a')

# is DST in effect?
#timezone    = -(time.altzone if localtime.tm_isdst else time.timezone)
#timeString += "Z" if timezone == 0 else "+" if timezone > 0 else "-"
#timeString += time.strftime("%H'%M'", time.gmtime(abs(timezone)))
#print timeString

if (DoDebug):
    print('mail1: ',access[0][0], access[0][1],access[0][2], access[0][3])
    print('mail2: ',access[1][0], access[1][1],access[1][2], access[1][3])

stats1 = get_stats(access[0][0], access[0][1],access[0][2], access[0][3])
if (DoMail2):
    stats2 = get_stats(access[1][0], access[1][1],access[1][2], access[1][3])
else:
    stats2 = {'mai': 'huib.van.langevelde@me.com', 'new': 0, 'all': 0, 'del': 0, 'flg': 0}

if (DoDebug):
    print('stats1: ', stats1)
    print('stats2: ', stats2)

make_entry(res,time,stats1,stats2)
res.close()

 
#ids = data[0] # data is a list.
#id_list = ids.split() # ids is a space separated string

#print id_list

#latest_email_id = id_list[-1] # get the latest
 
#result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID
 
#raw_email = data[0][1] # here's the body, which is raw text of the whole email
# including headers and alternate payloads
#print raw_email

