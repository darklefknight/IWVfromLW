import socket
import asyncio
from scipy.interpolate import griddata
import numpy as np


hostname = socket.gethostname()
print(f'Hello from {hostname}')

async def HelloWorld():
    print("Hello World!")

loop = asyncio.get_event_loop()
loop.run_until_complete(HelloWorld())
loop.close()


def func(x,y):
    return x * (1 - x) * np.cos(4 * np.pi * x) * np.sin(4 * np.pi * y ** 2) ** 2

grid_x, grid_y = np.mgrid[0:1:100j, 0:1:200j]

points = np.random.rand(1000, 2)
values = func(points[:,0], points[:,1])

grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')