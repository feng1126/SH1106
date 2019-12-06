
import time
from smbus import SMBus

LCD_WIDTH   = 128 #LCD width
LCD_HEIGHT  = 64  #LCD height

class SH1106(object):
    def __init__(self):
        self.width = LCD_WIDTH
        self.height = LCD_HEIGHT
        self.bus = SMBus(1)
        self.address = 0x3C

    """    Write register address and data     """
    def command(self, cmd):
        self.bus.write_byte_data(self.address, 0x00, cmd)

    def Init(self):
        self.command(0xAE);#--turn off oled panel
        self.command(0x02);#---set low column address
        self.command(0x10);#---set high column address
        self.command(0x40);#--set start line address  Set Mapping RAM Display Start Line (0x00~0x3F)
        self.command(0x81);#--set contrast control register
        self.command(0xA0);#--Set SEG/Column Mapping     
        self.command(0xC0);#Set COM/Row Scan Direction   
        self.command(0xA6);#--set normal display
        self.command(0xA8);#--set multiplex ratio(1 to 64)
        self.command(0x3F);#--1/64 duty
        self.command(0xD3);#-set display offset    Shift Mapping RAM Counter (0x00~0x3F)
        self.command(0x00);#-not offset
        self.command(0xd5);#--set display clock divide ratio/oscillator frequency
        self.command(0x80);#--set divide ratio, Set Clock as 100 Frames/Sec
        self.command(0xD9);#--set pre-charge period
        self.command(0xF1);#Set Pre-Charge as 15 Clocks & Discharge as 1 Clock
        self.command(0xDA);#--set com pins hardware configuration
        self.command(0x12);
        self.command(0xDB);#--set vcomh
        self.command(0x40);#Set VCOM Deselect Level
        self.command(0x20);#-Set Page Addressing Mode (0x00/0x01/0x02)
        self.command(0x02);#
        self.command(0xA4);# Disable Entire Display On (0xa4/0xa5)
        self.command(0xA6);# Disable Inverse Display On (0xa6/a7) 
        time.sleep(0.1)
        self.command(0xAF);#--turn on oled panel
        
   
    def getbuffer(self, image):
        # print "bufsiz = ",(self.width/8) * self.height
        buf = [0xFF] * ((self.width//8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        # print "imwidth = %d, imheight = %d",imwidth,imheight
        if(imwidth == self.width and imheight == self.height):
            # print ("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[x + (y // 8) * self.width] &= ~(1 << (y % 8))
                        # print x,y,x + (y * self.width)/8,buf[(x + y * self.width) / 8]
                        
        elif(imwidth == self.height and imheight == self.width):
            # print ("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[(newx + (newy // 8 )*self.width) ] &= ~(1 << (y % 8))
        return buf
            
    def ShowImage(self, pBuf):
        for page in range(0,8):
            # set page address #
            self.command(0xB0 + page);
            # set low column address #
            self.command(0x02); 
            # set high column address #
            self.command(0x10); 
    
            for i in range(0,self.width):
                self.bus.write_byte_data(self.address, 0x40, ~pBuf[i+self.width*page])

    def clear(self):
        """Clear contents of image buffer"""
        _buffer = [0xff]*(self.width * self.height//8)
        self.ShowImage(_buffer) 
            #print "%d",_buffer[i:i+4096]

from PIL import Image,ImageDraw,ImageFont   
if __name__ == "__main__":
    disp = SH1106()
    disp.Init()
    disp.clear()
    while True:
        image1 = Image.new('1', (disp.width, disp.height), "WHITE")
        draw = ImageDraw.Draw(image1)
        font10 = ImageFont.truetype('Font.ttf',13)
        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        font = ImageFont.truetype('Font.ttf', 20)
        draw.text((0, 0), localtime, font=font10, fill=0)
        image1=image1.rotate(180)
        disp.ShowImage(disp.getbuffer(image1))
    #time.sleep(2)
