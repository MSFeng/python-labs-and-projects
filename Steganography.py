#! /usr/bin/env python3.4

__author__= 'ee364f05'

#
#$Author: ee364f05 $ Username of the person committing
#$Date: 2016-04-17 16:43:53 -0400 (Sun, 17 Apr 2016) $   Date and time this file was committed
#$Revision: 90637 $ The revision number of this file
#$HeadURL: svn+ssh://ece364sv@ecegrid-thin1/home/ecegrid/a/ece364sv/svn/S16/students/ee364f05/Lab11/Steganography.py $  The URL where this file lives in the repository

#$Id: Steganography.py 90637 2016-04-17 20:43:53Z ee364f05 $ A combination of the above keywords

import scipy,base64
import numpy as np
from os.path import join
from scipy.misc import *
import zlib
import re
from numpy import uint8
from numpy import packbits
class Payload():
    def __init__(self,img=None,compressionLevel=-1,xml=None):
        self.img=img
        self.compressionLevel=compressionLevel
        self.xml=xml

        if img is not None and type(img) == np.ndarray and (compressionLevel<=9 and compressionLevel>=0 or compressionLevel==-1):


            self.generateXML(img,compressionLevel)
        elif xml is not None and isinstance(xml,str):


            self.recustruct()
        elif img is None and xml is None:
            raise ValueError(img,xml)
        elif compressionLevel<-1 or compressionLevel>9:
            raise ValueError(compressionLevel)
        elif not isinstance(img,np.ndarray):

            raise TypeError(img)
        elif not isinstance(xml,str):
            raise TypeError(xml)

    def generateXML(self,img,compressionLevel):
        mx=img.shape
        byte = bytearray()
        red=""
        green=""
        blue=""
        size = mx[0],mx[1]
        if(compressionLevel!=-1):

            compressed=True
            if(len(mx)==2):
                type="Gray"

                for i in range(0,mx[0]):

                    for j in range(0,mx[1]):

                        byte.extend(img[i][j])
                #print(byte)
            elif(len(mx)==3):
                for i in img:
                    for j in i:
                        byte.extend(j[0])

                for i in img:
                    for j in i:
                        byte.extend(j[1])
                for i in img:
                    for j in i:
                        byte.extend(j[2])
                type="Color"


            s=zlib.compress(byte,compressionLevel)
            z=base64.b64encode(s)




        else:
            compressed=False

            if(len(mx)==2):
                type="Gray"
                for i in range(0,mx[0]):
                    for j in range(0,mx[1]):

                        byte.extend(img[i][j])
            elif(len(mx)==3):
                for i in img:
                    for j in i:
                        byte.extend(j[0])

                for i in img:
                    for j in i:
                        byte.extend(j[1])
                for i in img:
                    for j in i:
                        byte.extend(j[2])
                type="Color"



            z=base64.b64encode(byte)

        z=str(z)
        z=z[2:-1]

        string="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<payload type=\"{}\" size=\"{},{}\" compressed=\"{}\">".format(type,mx[0],mx[1],compressed) + "\n" +z  +'\n' +"</payload>"

        self.xml=string

    def recustruct(self):
        type=re.search(r'type="\w{1,}',self.xml).group()
        type=type[6:]
        size=re.search(r'size="[0-9,]{1,}',self.xml).group()
        size=size.split(",")
        num1=size[0][6:]
        num2=size[1]
        size=(int(num1),int(num2))
        compressed=re.search(r'compressed="\w{1,}',self.xml).group()
        compressed=compressed[12:]
        content=re.search(r'>\n\S{1,}\n<',self.xml).group().split('\n')
        content=content[1]

        if(compressed=="True"):

            if type == "Color":
                array=np.ndarray(shape=(size[0],size[1],3),dtype=uint8)
                s=base64.b64decode(content)
                z=zlib.decompress(s)
                k=0
                for i in range(0,size[0]):
                    for j in range(0,size[1]):

                        array[i][j][0]=z[k]
                        k+=1
                for i in range(0,size[0]):
                    for j in range(0,size[1]):

                        array[i][j][1]=z[k]
                        k+=1
                for i in range(0,size[0]):
                    for j in range(0,size[1]):

                        array[i][j][2]=z[k]
                        k+=1

            elif type =="Gray":
                array=np.ndarray(shape=(size[0],size[1]),dtype=uint8)
                s=base64.b64decode(content)
                z=zlib.decompress(s)
                k=0
                for i in range(0,size[0]):
                    for j in range(0,size[1]):

                        array[i][j]=z[k]
                        k+=1


        else:
            if type == "Color":
                array=np.ndarray(shape=(size[0],size[1],3),dtype=uint8)
                z=base64.b64decode(content)

                k=0
                for i in range(0,size[0]):
                    for j in range(0,size[1]):

                        array[i][j][0]=z[k]
                        k+=1
                for i in range(0,size[0]):
                    for j in range(0,size[1]):

                        array[i][j][1]=z[k]
                        k+=1
                for i in range(0,size[0]):
                    for j in range(0,size[1]):

                        array[i][j][2]=z[k]
                        k+=1

            elif type =="Gray":
                array=np.ndarray(shape=(size[0],size[1]),dtype=uint8)
                z=base64.b64decode(content)

                k=0
                for i in range(0,size[0]):
                    for j in range(0,size[1]):

                        array[i][j]=z[k]
                        k+=1




        self.img=array



class Carrier():
    def __init__(self,img):
        if isinstance(img,np.ndarray):
            self.img=img
        else:
            raise TypeError(img)

    def payloadExists(self):
        array=self.img&1

        bits=[]
        cnt=0
        i=0
        j=0
        k=0

        if len(self.img.shape)==3:
            while cnt<38*8 and i<len(array):
                bits.append(array[i][j][k])
                j+=1
                if j>=self.img.shape[0]:
                    i+=1
                    j=0
                if i>=self.img.shape[1]:
                    k+=1
                    i=0
                    j=0
                cnt+=1

            info=packbits(bits)
            string=""
            for p in info:
                c=chr(p)
                string+=c
        elif len(self.img.shape)==2:

            while cnt<38*8 and i<len(array):

                bits.append(array[i][j])
                j+=1
                if j>=self.img.shape[1]:
                    i+=1
                    j=0

                cnt+=1

            info=packbits(bits)
            string=""

            for p in info:
                c=chr(p)
                string+=c


        if string == "<?xml version=\"1.0\" encoding=\"UTF-8\"?>":
            return True
        else:
            return False

    def clean(self):
        img2=254
        out=np.bitwise_and(self.img,img2)
        return out

    def embedPayload(self,payload,override=False):
        if override==False and self.payloadExists():
            raise Exception(self.img)
        if not isinstance(payload,Payload):
            raise TypeError(payload)
        if len(self.img.shape)==2:
            size1=self.img.shape[0]*self.img.shape[1]
        else:
            size1=self.img.shape[0]*self.img.shape[1]*self.img.shape[2]

        if len(payload.img.shape)==2:
            size2=payload.img.shape[0]*payload.img.shape[1]
        else:
            size2=payload.img.shape[0]*payload.img.shape[1]*payload.img.shape[2]

        if size1<size2*8:
            raise ValueError(payload)

        char=bytearray(map(ord,payload.xml))

        bits=np.unpackbits(char)


        if len(self.img.shape)==3:
            new=self.img.transpose(2,0,1)
            new=new.ravel()
            new1=new
            new=new&~1
            newarray=np.bitwise_or(new[:len(bits)],bits)
            newarray=np.append(newarray,new1[len(bits):])

            r,g,b=np.hsplit(newarray,3)
            newarray=np.dstack((r,g,b))
            newarray=np.hsplit(newarray,self.img.shape[0])
            newarray=np.vstack(newarray)
            #newarray=newarray.transpose(1,2,0)
        else:
            new=self.img.ravel()
            new1=new
            new=new&~1
            newarray=np.bitwise_or(new[0:len(bits)],bits)
            newarray=np.append(newarray,new1[len(bits):])
            newarray=np.hsplit(newarray,self.img.shape[0])
            newarray=np.vstack(newarray)


        # if len(self.img.shape)==3:
        #     for i in range(0,len(bits)):
        #
        #         newarray[j][k][l]=(self.img[j][k][l] & ~1) | bits[i]
        #
        #
        #         k+=1
        #         if k==self.img.shape[1]:
        #             k=0
        #             j+=1
        #         if j==self.img.shape[0]:
        #             j=0
        #             k=0
        #             l+=1
        #         if l==3:
        #             break
        #
        # else:
        #     for i in range(0,len(bits)):
        #
        #         newarray[j][k]=(self.img[j][k] & ~1) | bits[i]
        #
        #
        #
        #         k+=1
        #         if k==self.img.shape[1]:
        #             j+=1
        #             k=0

        #print(newarray)
        return newarray





    def extractPayload(self):
        if not self.payloadExists():
            raise Exception(self)



        if len(self.img.shape)==3:
            new=self.img.transpose(2,0,1)

            array=new&1
            a=np.packbits(array)
            string=""

            for p in a:
                c=chr(p)
                string+=c
            b=re.split(r'</payload>',string)[0]
            b=b+"</payload>"

        else:
            array=self.img&1
            a=np.packbits(array)
            string=""

            for p in a:
                c=chr(p)
                string+=c
            b=re.split(r'</payload>',string)[0]
            b=b+"</payload>"



        newins=Payload(xml=b)
        return newins





        #array=array.ravel()







def getXML(path):

    with open(path, "r") as xFile:
        content = xFile.read()
    return content
if __name__ == '__main__':
    folder = "test_images"
    p = Payload(imread(join(folder, "payload2.png")), 9)
    c = Carrier(imread(join(folder, "carrier1.png")))
    c.embedPayload(p)

    #print(imread(join(folder, "result2.png")))
    #print(imread(join(folder, "payload3.png")))