import re
import io
import datetime as dt

class Subs():
    def __init__(self, subfile, delta=dt.timedelta(0)):
        self.__subfile = io.open(subfile, mode='r', encoding='utf-8')
        self.subs = []
        self.delta = delta
        self.getSubs()
        self.closeFile()

    def getSubs(self):
        line_buffer = []
        for line in self.__subfile:
            if line == '\n' and len(line_buffer) > 2:
                line_sub = Sub(line_buffer, self.delta)
                self.subs += [line_sub]
                line_buffer = []
            else:
                line_buffer += [line]

    def closeFile(self):
        self.__subfile.close()

    def __len__(self):
        return len(self.subs)

class Sub():
    def __init__(self, sublist, delta=dt.timedelta(0)):
        self.sublist = sublist
        self.delta = delta
        self.timestamp = sublist[1]
        self.content = sublist[2:]
        self.deltastamp = self.getTime()
        self.time = self.convertTime(self.deltastamp[0])
        self.correctTimestamp()

    def getTime(self):
        matchObj = re.match(r'(.*) --> (.*)', self.timestamp)
        return matchObj.group(1, 2)

    def convertTime(self, time):
        pattern = re.compile(r'(.*):(.*):(.*)')
        match = pattern.match(time)
        tvalues = match.groups()
        
        tvalues = tuple(float(tvalues[elm].replace(',', '.'))
                        for elm in range(len(tvalues)))

        mseconds = tvalues[2] - int(tvalues[2])
        tvalues = tvalues[:2] + (float(int(tvalues[2])),)
        tvalues += (int(mseconds*1000),)

        t = dt.timedelta(hours= tvalues[0], minutes= tvalues[1],
                         seconds= tvalues[2], milliseconds= tvalues[3])
        
        t += self.delta
        return t

    def correctTimestamp(self):
        endtime = self.convertTime(self.deltastamp[1])
        string_stime = self.timeToString(self.time)
        string_etime = self.timeToString(endtime)
        new_timestamp = '{} --> {}\n'.format(string_stime, string_etime)
        self.timestamp = new_timestamp

    def timeToString(self, timedelta):
        mseconds = self.toRstCompatible1000(timedelta.microseconds // 1000)
        secs = self.toRstCompatible(timedelta.seconds % 60)
        seconds = '{},{}'.format(secs, mseconds)
        minutes = self.toRstCompatible((timedelta.seconds // 60) % 60)
        hours = self.toRstCompatible(timedelta.seconds // 3600)
        time = '{}:{}:{}'.format(hours, minutes, seconds)
        return time

    def toRstCompatible(self, num):
        hundreds = num // 100
        tens = num // 10
        if tens == 0:
            return '0' + str(num)
        else:
            return str(num)

    def toRstCompatible1000(self, num):
        hundreds = num // 100
        tens = num // 10
        if hundreds == 0:
            if tens == 0:
                return '00' + str(num)
            else:
                return '0' +str(num)
        else:
            return str(num)
            

class Mixer:
    def __init__(self, sub1, sub2, delta):
        self.sub1 = Subs(sub1)
        self.sub2 = Subs(sub2, delta)
        self.sub3 = io.open('SubMix.srt', mode='w', encoding='utf-8')
        self.organize()
        self.closeFile()

    def biggestSize(self):
            len1 = len(self.sub1)
            len2 = len(self.sub2)
            print('len1: {}'.format(len1))
            print('len2: {}'.format(len2))
            
            if len1 > len2:
                return len1 + len2
            else:
                self.sub1, self.sub2 = self.sub2, self.sub1
                return len1 + len2

    def organize(self):
        subs1 = self.sub1.subs
        pointer1 = 0
        subs2 = self.sub2.subs
        pointer2 = 0
        size = self.biggestSize()
        print('size: {}'.format(size))
        
        for elm in range(size):
            self.sub3.write(str(elm + 1) + '\n')
            
            if pointer1 == len(subs1):
                time1 = dt.timedelta(days=1)
            else:
                time1 = subs1[pointer1].time
                
            if pointer2 == len(subs2):
                time2 = dt.timedelta(days=1)
            else:
                time2 = subs2[pointer2].time
                
            if time1 <= time2:
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

timedelta = dt.timedelta(seconds=31, milliseconds=933)
#timedelta = dt.timedelta(0)
Mixer('SubsEN.srt', 'SubsCN.srt', timedelta)
