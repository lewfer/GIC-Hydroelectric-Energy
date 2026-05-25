from gpiozero import Button

b1 = Button(26)

print ("Please press the button")
b1.wait_for_press()
print("Thank you")
