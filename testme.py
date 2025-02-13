import math


gym_temperature = 11.9

new = 75

a = 17.27
b = 237.7
alpha = ((a * gym_temperature) / (b + gym_temperature)) + math.log(new / 100)
Td = (b * alpha)/(a - alpha)

print(round(Td, 2))
