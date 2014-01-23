from time import time

class _base64(object):
    t_en = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    t_de = (-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,	#15
	-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,	#31
	-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,62,-1,62,-1,63,	#47
	52,53,54,55,56,57,58,59,60,61,-1,-1,-1,-1,-1,-1,	#63
	-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,	#79
	15,16,17,18,19,20,21,22,23,24,25,-1,-1,-1,-1,63,	#95
	-1,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,	#111
	41,42,43,44,45,46,47,48,49,50,51,-1,-1,-1,-1,-1)

    def __init__(self):
        pass
    
    def encode(self, str):
        r = []
        pos = 0
        while(pos+3<=len(str)):
            ch1=ord(str[pos:pos+1])
            pos+=1
            ch2=ord(str[pos:pos+1])
            pos+=1
            ch3=ord(str[pos:pos+1])
            pos+=1
            r.append(self.t_en[ch1>>2])
            r.append(self.t_en[((ch1<<4)+(ch2>>4))&0x3f])
            r.append(self.t_en[((ch2<<2)+(ch3>>6))&0x3f])
            r.append(self.t_en[ch3&0x3f])
        

        if pos<len(str):
            ch1=ord(str[pos:pos+1])
            pos+=1
            r.append(self.t_en[ch1>>2])
            if pos<len(str):
                ch2=ord(str[pos:pos+1])
                r.append(self.t_en[((ch1<<4)+(ch2>>4))&0x3f])
                r.append(self.t_en[ch2<<2&0x3f])
        
            else:
                r.append(self.t_en[ch1<<4&0x3f])
            

        return ''.join(r)

base64 = _base64()

def get_wan_url(url):
    if not url.startswith('http://'):
        b64url = base64.encode('http://'+url)
    else:
        b64url = base64.encode(url)

    return '/proxy?url='+b64url+'&t='+str(int(time()*1000))


if __name__ == '__main__':
    print base64.encode('baidu.com')
    print get_wan_url('baidu.com')
