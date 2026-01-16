from PiicoDev_SSD1306 import *
display = create_PiicoDev_SSD1306()

myString = "this is me"
myNumber = 123.4567

display.text("Hello, World!", 0,0, 1) # literal string
display.text(myString, 0,15, 1) # string variable
display.text(str(myNumber), 0,30, 1) # print a variable
display.text("{:.2f}".format(myNumber), 0,45, 1) # use formatted-print
display.show()

sleep_ms(1000)

counter = 1

while True:
    display.fill(0)
    display.text("PiicoDev",30,20, 1)
    display.text(str(counter),50,35, 1)
    display.show()
    counter = counter + 1
    sleep_ms(1000)
    