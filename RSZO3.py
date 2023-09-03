import pygame
from math import *
from random import *
import time
from dataclasses import dataclass

@dataclass
class Databullet():

    name: str
    speed: float
    m: float
    m_topl: float
    l: float
    d: float
    KSA_n: float
    boost: float
    boost_t: float
    max_angle: float
    min_angle: float
    ZALP: float
    hight: float



pygame.init()
pygame.mixer.init()
# импорт всего и вся

pygame.display.set_caption("Grafics")

WIDHT = pygame.display.Info().current_w * 0.8 // 100 * 100
HIGHT = pygame.display.Info().current_h * 0.8 // 100 * 100

tick = 10    # Кол-во тиков в секунду

t = 1 / tick

TIME = 0

FPS = 9999

TOTAL_RANGE = 50000
biba = TOTAL_RANGE / WIDHT

SCALE_H = biba # Метров в пикселе
SCALE_W = biba # Метров в пикселе

num_tick = 0
chrift = pygame.font.Font(None, int(36))
big_chrift = pygame.font.Font(None, int(200))

screen = pygame.display.set_mode((WIDHT, HIGHT))
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PINK = (222, 100, 0)
PURPLE = (150, 222, 0)
DARK_GREEN = (0, 75, 0)
OLD_COLOR = (210, 210, 170)


COLOR_BASE = []

for g in range(5):
    for b in range(5):
        for r in range(5):
            COLOR_BASE.append((r*50,b*50,g*50))



air_data = []
file = open('data_base_of_air.txt', 'r').read().split()
for i in range(len(file) // 4 ):
    air_data.append([int(file[i*4]), float(file[i*4+1]), float(file[i*4+2]), float(file[i*4+3])])
# Высота - плотность воздуха - g - скорость звука
# print(air_data)

logs = open('logs.txt', 'w')

# Задаю все глобальные переменные


class Missle:

    def __init__(self, angle, speed, m, m_topl, color, l, d, KSA_n, boost, boost_t, hight):
        self.positions = []
        self.run = 1

        self.g = 9.81  # Ускорение свободного падения
        self.m = m  # Масса
        self.m_topl = m_topl # Масса топлива, которая постепенно будет уменьшаться

        self.KSA_n = KSA_n  # коофицент сопротивления воздуха объекта в профиль
        self.KSA_x = None  # КСВ по x
        self.KSA_y = None  # КСВ по y
        self.d = d    # Диаметр снаряда
        self.long = l    # длинна снаряда
        self.plot_air = 1.21  # Плотность воздуха

        self.start_angle = angle
        self.angle = angle
        self.color = color
        self.speed_x = cos(self.angle) * speed
        self.speed_y = sin(self.angle) * speed
        self.speed = hypot(self.speed_x, self.speed_y)

        self.Mah_speed_x = 0
        self.Mah_speed_y = 0
        self.Mah_speed = 0

        self.cdw = 0

        self.time = 0

        self.a_on_y = 0  # Ускорение по y
        self.a_on_x = 0  # Ускорение по x

        self.pos_y = hight  # Позиция по у
        self.pos_x = 0  # Позиция по х

        self.kost1 = 0 # для рассеивания

        self.boost = boost  # Ускорение за счёт двигла
        self.boost_time = boost_t

        self.M = 0 # Скорость звука


    def update(self):
        for i in range(len(air_data)):
            if self.pos_y <= air_data[i][0]:
                self.plot_air = air_data[i][1]
                self.g = air_data[i][2]
                self.M = air_data[i][3]
                break

        if self.Mah_speed >= 1:
            self.cdw = (4 * (self.d / self.long) ** 2) / sqrt(self.Mah_speed ** 2 - 1)
            # print(self.cdw)
        else:
            self.sdw = 0

        if self.pos_x < TOTAL_RANGE and self.pos_y >= 0:
            try:
                self.angle = atan(self.speed_y / self.speed_x )
            except ZeroDivisionError:
                print("Деление на 0 в апдейте поворота")

            self.KSA_x = (self.KSA_n + self.cdw) * (3.14 * self.d ** 2 /4) * cos( self.angle)
            self.KSA_y = (self.KSA_n + self.cdw) * (3.14 * self.d ** 2 /4) * sin(self.angle)

            self.a_on_y = self.g + self.plot_air * self.speed_y * self.speed_y / 2 * self.KSA_y / self.m * copysign(1, self.speed_y)
            if self.time < self.boost_time:
                self.speed_y -= (self.a_on_y - self.boost / self.m * sin(self.angle)) * t
            else:
                self.speed_y -= self.a_on_y * t

            self.pos_y += (self.speed_y * t + self.a_on_y * t * t / 2 )

            self.a_on_x = self.plot_air * self.speed_x * self.speed_x / 2 * self.KSA_x / self.m * copysign(1, self.speed_x)
            if self.time < self.boost_time:
                self.speed_x -= (self.a_on_x - self.boost / self.m * cos(self.angle)) * t
            else:
                self.speed_x -= self.a_on_x * t

            if self.time <= self.boost_time:
                self.m -= self.m_topl / self.boost_time / tick

            self.pos_x += (self.speed_x * t + self.a_on_x * t * t / 2)

            self.speed = hypot(self.speed_x, self.speed_y)
            self.time += t

            self.Mah_speed = self.speed / self.M

            # print(round(self.time / tick, 0), end=' ')
            # print(round(self.angle * 57.3, 2), end=' ')
            # print(round(self.pos_x, 0), end=' ')
            # print(round(self.pos_y, 0), end=' ')
            # print(round(self.speed_x, 0), end=' ')
            # print(round(self.speed_y, 0), end=' ')
            # print(round(self.a_on_x, 0), end=' ')
            # print(round(self.a_on_y, 0), end=' ')
            # print()
            self.positions.append([self.pos_x, self.pos_y])
        else:
            # print(self.pos_x, self.pos_y)
            self.run = 0
        for pos in self.positions:
            pygame.draw.circle(surface=screen, color=self.color, center=(pos[0] / SCALE_W, HIGHT - (pos[1]/ SCALE_H)), radius=2, width=2)

        self.logsupdate()


    def logsupdate(self):
        logs.write('---------------------------------------------------------\n')
        logs.write(f'Start angle: {self.start_angle}\n')
        logs.write(f'Now angle: {self.angle}\n')
        logs.write(f'Time: {TIME}\n')
        logs.write(f'Coordinats x, y: {self.pos_x}, {self.pos_y}\n')
        logs.write(f'Speeds x, y: {self.speed_x}, {self.speed_y}\n')
        logs.write(f'Mass: {self.m}\n')
        logs.write('---------------------------------------------------------\n')
        logs.write('                                                         \n')



class Interfase():

    def __init__(self):
        pygame.draw.line(screen, BLACK, (0,HIGHT), (0,0), 5) # ось у
        pygame.draw.line(screen, BLACK, (0,HIGHT), (WIDHT,HIGHT), 5) # ось х
        self.s_h = 1000 / SCALE_H
        self.s_w = 1000 / SCALE_W

        self.is_logs = 0

        for i in range(int(WIDHT// self.s_w)):
            pygame.draw.line(screen, BLACK, (self.s_w, HIGHT), (self.s_w, HIGHT - 15), 3) # ось у

        for i in range(int(HIGHT// self.s_h)):
            pygame.draw.line(screen, BLACK, (0, self.s_h), (15, self.s_h), 3) # ось у

    def update(self):
        pygame.draw.rect(screen,OLD_COLOR,(30, 30, WIDHT, 220))

        time_text = chrift.render(str(f'Время: {round(TIME, 2)} с'), True, BLACK)
        screen.blit(time_text, (30, 30))

        high_text = chrift.render(str(f'Средняя высота ракет: {round(SR_HIGH, 1)} м'), True, BLACK)
        screen.blit(high_text, (30, 50))

        range_text = chrift.render(str(f'Средняя дальность ракет: {round(SR_RANGE, 1)} м'), True, BLACK)
        screen.blit(range_text, (30, 70))

        speed_text = chrift.render(str(f'Средняя скорость ракет: {round(SR_SPEED, 1)} м\с'), True, BLACK)
        screen.blit(speed_text, (30, 90))

        angle_text = chrift.render(str(f'Средний угол ракет: {round(SR_ANGLE, 1)} °'), True, BLACK)
        screen.blit(angle_text, (30, 110))

        spd_x_text = chrift.render(str(f'Средняя гор. скорость  ракет: {round(SR_SPD_X, 1)} м/с'), True, BLACK)
        screen.blit(spd_x_text, (30, 130))

        spd_y_text = chrift.render(str(f'Средняя верт. скорость  ракет: {round(SR_SPD_Y, 1)} м/с'), True, BLACK)
        screen.blit(spd_y_text, (30, 150))

        max_speed_text = chrift.render(str(f'Максимальная скорость ракет: {round(MAX_SPEED, 1)} м\с'), True, BLACK)
        screen.blit(max_speed_text, (550, 30))

        max_hight_text = chrift.render(str(f'Максимальная высота ракет: {round(MAX_HIGHT, 1)} м'), True, BLACK)
        screen.blit(max_hight_text, (550, 50))

        max_range_text = chrift.render(str(f'Максимальная дальность ракет: {round(MAX_RANGE, 1)} м'), True, BLACK)
        screen.blit(max_range_text, (550, 70))

        min_range_text = chrift.render(str(f'Минимальная дальность ракет: {round(MIN_RANGE, 1)} м'), True, BLACK)
        screen.blit(min_range_text, (550, 90))

        opt_angle_text = chrift.render(str(f'угол для макс. дальности ракет: {round(degrees(OPTIMAL_ANGLE), 1)} °'), True, BLACK)
        screen.blit(opt_angle_text, (550, 110))


        logs.write('#########################################################\n')
        logs.write(f'Time: {TIME}\n')
        logs.write(f'Average hight missls: {SR_HIGH}\n')
        logs.write(f'Average distance missls: {SR_RANGE}\n')
        logs.write(f'Average speed missls: {SR_SPEED}\n')
        logs.write(f'Average angle missls: {SR_ANGLE}\n')
        logs.write(f'Average X speed missls: {SR_SPD_X}\n')
        logs.write(f'Average Y speed missls: {SR_SPD_Y}\n')
        logs.write(f'Max speed of missls: {MAX_SPEED}\n')
        logs.write(f'Max hight of missls: {MAX_HIGHT}\n')
        logs.write(f'Max distance of missls: {MAX_RANGE}\n')
        logs.write(f'Min distance of missls: {MIN_RANGE}\n')
        logs.write('#########################################################\n')
        logs.write('                                                         \n')

        if not RUN and not self.is_logs:
            self.is_logs = 1
            logs.write('---------------------------------------------------------\n')
            logs.write(f'Angle for max distance: {degrees(OPTIMAL_ANGLE)}\n')
            logs.write('---------------------------------------------------------\n')
            logs.write('                                                         \n')





class Button:
    def __init__(self, rect, text):
        self.on = False
        self.rect = rect
        self.text = text
        try:
            self.rendered_text = chrift.render(self.text, True, BLACK)
            #self.txt_rect.append(int(self.rendered_text.get_rect()[0] // 2 + self.rect[0]) + (68 - len(self.text) * 36 * GAME_S // 2) * GAME_S)
            self.txt_rect.append(int(self.rendered_text.get_rect()[0] // 2 + self.rect[0]) + 10)
            self.txt_rect.append(int(self.rendered_text.get_rect()[1] // 2 + self.rect[1]) + 40)
            self.txt_rect.append(int(self.rendered_text.get_rect()[2] // 2 + self.rect[2]) - 10)
            self.txt_rect.append(int(self.rendered_text.get_rect()[3] // 2 + self.rect[3]) - 10)
        except AttributeError:
            pass

    def update(self):
        screen.blit(self.rendered_text, (self.rect[0], self.rect[1]))

button_pause = Button((WIDHT - 80, 0, WIDHT, 80), 'PAUSE')
# button_selector = Button((WIDHT - 200, 81, WIDHT, 160), 'SELECT AMMO')

## INPUT_ZONE
print('Хотите ли вы создать новый тип снаряда? (yes or no)', end='\n')
pres = input()
if pres == 'no':
    pass
elif pres == 'yes':
    print('Введите название снаряда')
    name = input()
    print('Введите начальную скорость снаряда в м\с')
    speed = float(input())
    print('Введите начальную массу снаряда в кг')
    m = float(input())
    print('Введите начальную массу топлива в кг')
    m_topl = float(input())
    print('Введите длинну снаряда в м')
    l = float(input())
    print('Введите диаметр снаряда в м')
    d = float(input())
    print('Введите коофицент сопротивления в среде снаряда в лобовой проекции')
    KSA_n = float(input())
    print('Введите мощность двигателя в дж')
    boost = float(input())
    print('Введите время работы двигателя в с, если нет, то -1')
    boost_t = float(input())
    open('databullets.txt', 'a', encoding='utf8').write(f"{name.replace(' ', '_')} {speed} {m} {m_topl} {l} {d} {KSA_n} {boost} {boost_t}\n")
    print('Ваш снаряд успешно сохранён')

# РСЗО_ГРАД 50 121 60 2.870 0.122 0.15 28000 2
# Артилерия_1812_года 290 5.5 0 1.2 1.2 0.47 0 -1

else:
    raise Exception('тебе ясно сказали yes or no')

print('Введите максимальный угол залпа в градусах: ')
max_angle = float(input())
print('Введите минимальный угол залпа в градусах: ')
min_angle = float(input())
print('Введите количество снарядов в залпе: ')
ZALP = int(input())
print('Введите высоту с которой происходит залп')
hight = float(input())


databullets = {}
for data in list(open('databullets.txt', 'r', encoding='utf8').read().split('\n')):
    data = data.split()
    if len(data) < 9:
        continue
    databullets.update({data[0].replace('_', ' ') : Databullet(data[0].replace('_', ' '), float(data[1]), float(data[2]), float(data[3]), float(data[4]), float(data[5]), float(data[6]), float(data[7]), float(data[8]), max_angle, min_angle, ZALP, hight)})

keys = list(databullets.keys())
print('Введите название снаряда, которым хотите воспользоваться. Существующие классы:')
for cl in keys:
    print(cl)

boepripas = databullets.get(input())
# # Т-80 БОПС
# speed = 1780
# m = 3.9
# m_topl = 0
# l = 0.580
# d = 0.036
# KSA_n = 0.1
# KSA_s = 0.7
# boost = 0
# boost_t = -1
# max_angle = 2
# min_angle = 14
# ZALP = 50
# rasev = 0
# hight = 2.5


# #авиабимба ФАБ-5000
# speed = 320
# m = 5400
# m_topl = 0
# l = 5.200
# d = 1.000
# KSA_n = 0.4
# KSA_s = 0.7
# boost = 0
# boost_t = -1
# max_angle = 10.0001
# min_angle = 5.0000
# ZALP = 20
# rasev = 125
# hight = 4000

# fab5k = Databullet('ФАБ 5000', 320, 5400, 0, 5.2, 1.0, 0.4, 0.7, 0, -1, max_angle, min_angle, ZALP, hight)

# #авиабимба ФАБ-250
# speed = 700 / 3.6
# m = 227
# m_topl = 0
# l = 1.924
# d =	0.300
# KSA_n = 0.4
# KSA_s = 0.7
# boost = 0
# boost_t = -1
# max_angle = 0.0001
# min_angle = 0.0000
# ZALP = 20
# rasev = 125
# hight = 7000

# missle1 = Missle(radians(55), speed, m, m_topl, RED, l, d, KSA_n, KSA_s, boost, boost_t)
# Missels.append(missle1)


grad = Databullet('РСЗО_ГРАД', 50, 121, 60, 2.870, 0.122, 0.15, 28000, 2, max_angle, min_angle, ZALP, hight)

screen.fill(OLD_COLOR)

interfase = Interfase()

RUN = 1
run_sum = 1
SR_RANGE = 0
SR_HIGH = 0
TOTAL_TIC = 0
SR_SPEED = 0
SR_ANGLE = 0

SR_SPD_X = 0
SR_SPD_Y = 0

MAX_SPEED = 0
MAX_HIGHT = 0
MAX_RANGE = 0
MIN_RANGE = 9999999
OPTIMAL_ANGLE = 45

Missels =[]

for i in range(ZALP):
    Missels.append(Missle(radians((max_angle - min_angle) / ZALP * i + min_angle), boepripas.speed, boepripas.m, boepripas.m_topl, COLOR_BASE[i % len(COLOR_BASE)], boepripas.l, boepripas.d, boepripas.KSA_n, boepripas.boost, boepripas.boost_t, hight))

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.pos[0] > WIDHT - 80 and event.pos[1] < 80:
                button_pause.on = not button_pause.on



    if not button_pause.on:
        TOTAL_TIC += 1


        if RUN:
            TIME += t

        if TOTAL_TIC % (tick) == 0:
            run_sum = 0
            SR_RANGE = 0
            SR_HIGH = 0
            SR_SPEED = 0
            SR_ANGLE = 0
            SR_SPD_X = 0
            SR_SPD_Y = 0

            for missle in Missels:
                if missle.pos_y > MAX_HIGHT:
                    MAX_HIGHT = missle.pos_y

                if missle.speed > MAX_SPEED:
                    MAX_SPEED = missle.speed

                if missle.pos_x > MAX_RANGE:
                    MAX_RANGE = missle.pos_x
                    OPTIMAL_ANGLE = missle.start_angle

                if missle.pos_x < MIN_RANGE and missle.run == 0:
                    MIN_RANGE = missle.pos_x

                run_sum += missle.run
                SR_RANGE += missle.pos_x
                SR_HIGH += missle.pos_y
                SR_SPEED += missle.speed
                SR_ANGLE += degrees(missle.angle)
                SR_SPD_X += missle.speed_x
                SR_SPD_Y += missle.speed_y

            SR_SPEED /= ZALP
            SR_RANGE /= ZALP
            SR_HIGH /= ZALP
            SR_ANGLE /= ZALP
            SR_SPD_X /= ZALP
            SR_SPD_Y /= ZALP

        pygame.draw.rect(screen, OLD_COLOR, (0, 0, WIDHT, HIGHT))

        for missle in Missels:
                missle.update()

        if run_sum < 1:
            RUN = 0
            pygame.draw.line(screen, RED, (MAX_RANGE / SCALE_W, HIGHT), (MAX_RANGE / SCALE_W, HIGHT - 20), 5 )

    interfase.update()
    button_pause.update()
    # button_selector.update()

    clock.tick(FPS)
    pygame.display.flip()
