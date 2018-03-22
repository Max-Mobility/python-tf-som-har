from __future__ import print_function
import enum
import re
import struct
import sys
import threading
import time
import csv

from myo import myo_raw as myo

myo_data = [];

if __name__ == '__main__':
    try:
        import pygame
        from pygame.locals import *
        HAVE_PYGAME = True
    except ImportError:
        HAVE_PYGAME = False

    if HAVE_PYGAME:
        w, h = 1200, 400
        scr = pygame.display.set_mode((w, h))

    last_vals = None
    def plot(scr, vals):
        DRAW_LINES = False

        global last_vals
        if last_vals is None:
            last_vals = vals
            return

        D = 5
        scr.scroll(-D)
        scr.fill((0,0,0), (w - D, 0, w, h))
        for i, (u, v) in enumerate(zip(last_vals, vals)):
            if DRAW_LINES:
                pygame.draw.line(scr, (0,255,0),
                                 (w - D, int(h/8 * (i+1 - u))),
                                 (w, int(h/8 * (i+1 - v))))
                pygame.draw.line(scr, (255,255,255),
                                 (w - D, int(h/8 * (i+1))),
                                 (w, int(h/8 * (i+1))))
            else:
                c = int(255 * max(0, min(1, v)))
                scr.fill((c, c, c), (w - D, i * h / 8, D, (i + 1) * h / 8 - i * h / 8));

        pygame.display.flip()
        last_vals = vals

    m = myo.MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None)

    def proc_emg(emg, moving, times=[]):
        if HAVE_PYGAME:
            ## update pygame display
            plot(scr, [e / 2000. for e in emg])
        else:
            print(emg)

        ## print framerate of received data
        times.append(time.time())
        if len(times) > 20:
            #print((len(times) - 1) / (times[-1] - times[0]))
            times.pop(0)

    def proc_imu(quat, accel, gyro):
        data = quat + accel + gyro
        print(data)
        myo_data.append(data)
        if HAVE_PYGAME:
            ## update pygame display
            plot(scr, [(e+2048) / 4096.0 for e in gyro])
        else:
            print(accel)

    m.add_emg_handler(proc_emg)
    m.add_imu_handler(proc_imu)
    m.connect()

    m.add_arm_handler(lambda arm, xdir: print('arm', arm, 'xdir', xdir))
    m.add_pose_handler(lambda p: print('pose', p))

    try:
        while True:
            m.run(1)

            if HAVE_PYGAME:
                for ev in pygame.event.get():
                    if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
                        raise KeyboardInterrupt()
                    elif ev.type == KEYDOWN:
                        if K_1 <= ev.key <= K_3:
                            m.vibrate(ev.key - K_0)
                        if K_KP1 <= ev.key <= K_KP3:
                            m.vibrate(ev.key - K_KP0)

    except KeyboardInterrupt:
        pass
    finally:
        m.disconnect()
        print()

    outputFilename = 'myo_raw_data.csv'
    header = '% qx, qy, qz, qw, ax, ay, az, gx, gy, gz\n'

    try:
        f = open(outputFilename, 'wb')
    except Exception as error:
        print("ERROR: Couldn't write to {}".format(outputFilename))
    else:
        with f:
            f.write(header)
            writer = csv.writer(f)
            writer.writerows(myo_data)
