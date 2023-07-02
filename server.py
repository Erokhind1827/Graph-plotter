import socket
import matplotlib.pyplot as plt
import numpy as np
import re
import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QApplication
from math import sin, cos, log as ln, tan as sincos,\
                 sinh as sh, cosh as ch, tanh as shch, asin, asinh as ash,\
                 acos, acosh as ach, atan as asincos, exp as ep, atanh as ashch, fabs as abs, pi 

# def my_eval(x):
#     # try:
#         eq=eval(x)
#         # print(eq)
#         if np.iscomplex(eq):
#             return None
#         else:
#             return eq
#     # except:
#     #     return False

def cossin(x):
    return 1/sincos(x)

def chsh(x):
    return 1/shch(x)

def sq(x):    
    return (x)**0.5
    
def findValues(equation,var,letter):
    func = []
    for i in var:
        newEq = equation.replace(letter,'(' + str(i) + ')')
        try:
            solution = eval(newEq) 
            if type(solution) == int or type(solution) == float:
                func.append(solution)
            else:
                func.append(None)
        except:
            func.append(None)           
    var_values = []
    func_values = []
    has_values = False
    for i in range(len(func)):
        if func[i] != None:
            if letter != 'f' or func[i] > 0:
                has_values = True
                var_values.append(var[i])
                func_values.append(func[i])
        else:
            var_values.append(var[i])
            func_values.append(np.nan)
    for i in range(1,len(func_values)):
        if func_values[i] != np.nan and func_values[i-1] != np.nan and abs(func_values[i] - func_values[i-1]) > 100:
            func_values[i] = np.nan
            func_values[i-1] = np.nan
    return func_values,var_values, has_values

def findMaxMin(x):
    minFunc = sys.maxsize 
    for i in x: 
        if i!= np.nan and i < minFunc: 
            minFunc = i 
    maxFunc = minFunc 
    for i in x: 
        if i!= np.nan and i > maxFunc: 
            maxFunc = i 
    # if minFunc != sys.maxsize:
    return maxFunc, minFunc
    # else:
    #     return 1,-1
    
def findBounds(func_values, var_values):
    maxFunc, minFunc = findMaxMin(func_values)
    delFunc = maxFunc-minFunc            
    if minFunc < 20 and maxFunc > -20: 
        funcLowerBound = max(minFunc-0.5,-20) 
        funcUpperBound = min(20,maxFunc+0.5) 
    elif maxFunc <= -20: 
        funcLowerBound = maxFunc + 0.5 
        funcUpperBound = funcUpperBound - min(20, delFunc) 
    else: 
        funcLowerBound = minFunc-0.5 
        funcUpperBound = funcLowerBound + min(20,delFunc)
    varUpperBound, varLowerBound = findMaxMin(var_values)
    if varUpperBound - varLowerBound == 0:
        varLowerBound -= 1
        varUpperBound = max(var_values) + 1
    return funcUpperBound, funcLowerBound, varUpperBound, varLowerBound

    



MSG_CONNECT = '!Connect'
MSG_DISCONNECT = '!Disconnect'

print('start')
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 5050)) # Привязываем серверный сокет к localhost и 5050 порту.
server.listen() # Начинаем прослушивать входящие соединения.

while True:
    # w.show()
    # sys.exit(app.exec_())
    # try:
    conn, addr = server.accept() # Метод который принимает входящее соединение.
    print(f'[{addr}] connected')
    connected = True
    # except:
    #     connected = False
    while connected:
        try:
            data = conn.recv(1024) # Получаем данные из сокета.
        except:
            data = MSG_DISCONNECT.encode()
            print('Connection Lost')
        properties = data.decode()
        if properties == MSG_DISCONNECT:
            connected = False
        elif properties != 'connect':
            props = properties.split('//')
            cord = props[0]
            rel = props[1]
            equation = props[2]
            start = int(props[3])
            end = int(props[4])
            colorValue = props[5]   
            widthValue = int(props[6])
            grid = props[7] in ("True")
            typeValue = props[8]
            time = props[9]
            fileName = 'requests\\\\' + addr[0] + '  ' + time + '.jpeg'
            
            yLowerBound = start
            yUpperBound = end
            xLowerBound = start
            xUpperBound = end

            equation = equation.replace('e^', '2.71828^')
            equation = equation.replace('^', '**')
            equation = equation.replace('sqrt', 'sq')
            equation = equation.replace('atg', 'asincos')
            equation = equation.replace('ath', 'ashch')
            equation = equation.replace('ctg', 'cossin')
            equation = equation.replace('tg', 'sincos')
            equation = equation.replace('cth', 'chsh')
            equation = equation.replace('th', 'shch')

            multiplies = re.findall(r'[0-9)xtrf][a-z(\|]',equation)
            for i in multiplies:
                equation = equation.replace(i, i[0] + '*' + i[1])
                
            # print(equation)

            if cord == 'rect':
                if rel == 'dir':      
                    x = np.linspace(start,end,10000)
                    y_values, x_values, has_values = findValues(equation,x,'x')
                    if has_values:
                        yUpperBound, yLowerBound, xUpperBound, xLowerBound = findBounds(y_values,x_values)

                elif rel == 'inv':
                    y = np.linspace(start,end,10000)
                    x_values, y_values, has_values = findValues(equation,y,'y')
                    if has_values:
                        xUpperBound, xLowerBound, yUpperBound, yLowerBound = findBounds(x_values,y_values)

                else:
                    yEq, xEq = equation.split('&')
                    t = np.linspace(start,end,10000)
                    y_temp_values, temp, has_values1= findValues(yEq,t,'t')
                    x_temp_values, temp, has_values2 = findValues(xEq,t,'t')
                    x_values = []
                    y_values = []
                    has_values = False
                    for i in range(min(len(x_temp_values),len(y_temp_values))):
                        # if x_temp_values[i] != None and y_temp_values[i]!= None:
                            x_values.append(x_temp_values[i])
                            y_values.append(y_temp_values[i])
                    if has_values1 and has_values2:
                        has_values = True
                        print('true')
                        # print(x_values)
                        yUpperBound, yLowerBound, xUpperBound, xLowerBound = findBounds(y_values,x_values)

                if has_values and (max(y_values) - min(y_values) > 0 or max(x_values) - min(x_values) > 0):
                    conn.sendall('Ok'.encode())
                    fig = plt.figure()
                    ax = plt.gca()
                    ax.axhline(y=0, color='k')
                    ax.axvline(x=0, color='k')
                    ax.set_xlim([xLowerBound,xUpperBound])
                    ax.set_ylim([yLowerBound,yUpperBound])
                    plt.grid(grid)
                    plt.plot(x_values,y_values, linestyle = typeValue, linewidth = widthValue, color = colorValue)
                    plt.savefig(fileName) 
                    plt.show()

                else:
                    conn.sendall('Something went wrong with your function... Check it?'.encode()) # Отправляем данные в сокет.

            else:
                if rel == 'dir':
                    f = np.linspace(float(start*np.pi/12),float(end*np.pi/12),1000)
                    r_values, f_values, has_values = findValues(equation,f,'f')

                elif rel == 'inv':
                    r = np.linspace(start,end,10000)
                    f_values, r_values, has_values = findValues(equation,r,'r')

                else:
                    rEq, fEq = equation.split('&')
                    t = np.linspace(start,end,10000)
                    r_temp_values, temp, has_values1 = findValues(rEq,t,'t')
                    f_temp_values, temp, has_values2 = findValues(fEq,t,'t')
                    r_values = []
                    f_values = []
                    has_values = False
                    for i in range(min(len(r_temp_values),len(f_temp_values))):
                        if f_temp_values[i] != np.nan and r_temp_values[i]!= np.nan and r_temp_values[i] > 0:
                            has_values = True
                            f_values.append(f_temp_values[i])
                            r_values.append(r_temp_values[i])

                if has_values and (max(r_values) - min(r_values) > 0 or max(f_values) - min(f_values) > 0):
                    conn.sendall('Ok'.encode())
                    ax = plt.subplot(111,projection='polar')
                    ax.plot(f_values, r_values, linestyle = typeValue, linewidth = widthValue, color = colorValue)
                    ax.grid(grid)
                    plt.savefig(fileName) 
                    plt.show()

                else:
                    conn.sendall('Something went wrong with your function... Check it?'.encode())

    print(f'[{addr}] disconnected')
    conn.close()
    