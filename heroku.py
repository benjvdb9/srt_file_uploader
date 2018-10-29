import os
import re
import io
import datetime as dt
from bottle import route, static_file, run

class Subs():
    def __init__(self, subfile):
        self.__subfile = io.open(subfile, mode='r', encoding='utf-8')
        self.subs = []
        self.getSubs()
        self.closeFile()

    def getSubs(self):
        line_buffer = []
        for line in self.__subfile:
            if line == '\n' and len(line_buffer) > 2:
                line_sub = Sub(line_buffer)
                self.subs += [line_sub]
                line_buffer = []
            else:
                line_buffer += [line]

    def closeFile(self):
        self.__subfile.close()

    def __len__(self):
        return len(self.subs)

class Sub():
    def __init__(self, sublist):
        self.sublist = sublist
        self.timestamp = sublist[1]
        self.content = sublist[2:]
        self.time = self.getTime()

    def getTime(self):
        matchObj = re.match(r'(.*) --> (.*)', self.timestamp)
        return self.convertTime(matchObj.group(1))

    def convertTime(self, time):
        pattern = re.compile(r'(.*):(.*):(.*)')
        match = pattern.match(time)
        tvalues = match.groups()
        
        tvalues = tuple(float(tvalues[elm].replace(',', '.'))
                        for elm in range(len(tvalues)))

        t = dt.timedelta(hours= tvalues[0], minutes= tvalues[1], seconds= tvalues[2])
        x = t.total_seconds()

        return dt.timedelta(hours= tvalues[0],
                            minutes= tvalues[1], seconds= tvalues[2])

class Mixer:
    def __init__(self, sub1, sub2):
        self.sub1 = Subs(sub1)
        self.sub2 = Subs(sub2)
        self.sub3 = io.open('SubMix.srt', mode='w', encoding='utf-8')
        self.organize()
        self.closeFile()

    def biggestSize(self):
            len1 = len(self.sub1)
            len2 = len(self.sub2)
            
            if len1 > len2:
                return len1
            else:
                self.sub1, self.sub2 = self.sub2, self.sub1
                return len1 + len2

    def organize(self):
        subs1 = self.sub1.subs
        pointer1 = 0
        subs2 = self.sub2.subs
        pointer2 = 0
        size = self.biggestSize()
        
        for elm in range(size):
            self.sub3.write(str(elm + 1) + '\n')
            try:
                time2 = subs2[pointer2].time
            except:
                time2 = dt.timedelta(days=1)

            #t = subs1[pointer1].time.total_seconds()
            #f = time2.total_seconds()
            #import pdb; pdb.set_trace()
                
            if subs1[pointer1].time < time2:
                current_sub = subs1[pointer1]
                pointer1 += 1
            else:
                current_sub = subs2[pointer2]
                pointer2 += 1
            
            self.sub3.write(current_sub.timestamp)
            for line in current_sub.content:
                self.sub3.write(line)

            self.sub3.write('\n')

    def closeFile(self):
        self.sub3.close()

Mixer('SubsEN.srt', 'SubsCN.srt')

@route('/')
def show_def():
    return static_file('SubsMix.srt', root=('.'))

if os.environ.get('APP_LOCATION') == 'heroku':
    run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    
else:
    run(host='localhost', port=8080)
