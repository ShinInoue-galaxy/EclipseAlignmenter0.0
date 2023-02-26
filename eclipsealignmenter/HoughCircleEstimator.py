#Hough 変換による円検出
# https://docs.opencv.org/3.4/d4/d70/tutorial_hough_circle.html
#last update: 2023/2/26

import cv2
import numpy as np
import sys
import matplotlib.pyplot as plt
import os
import matplotlib.patches as patches

#Hough 変換による円検出と例外処理
def estimate_hough_circle(
    gray, #入力画像、gray
    dp, #Hough 変換パラメータ
    radius, #円の半径
    param2, #Hogh 変換パラメータ
    outdir, #画像出力dir
    log, #log file
):
    delta_Radius = 2
    _max = np.max(gray) #最大値をとってHough変換に与える。
    #Hough 変換で円検出。ここが重要
    #求めた半径からパラメータを設定。
    minDist = 2 * int(radius)
    minRadius = int(radius) - delta_Radius
    maxRadius = int(radius) + delta_Radius
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=dp, minDist=minDist, param1=_max*1.5, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

    if circles is not None: #円が検出されれば、
        if len(circles[0]) == 1:
            xref = circles[0][0][0]
            yref = circles[0][0][1]
            radius = circles[0][0][2]
            print('matched a circle with (x,y) = (%.2f, %.2f), raidus = %.2f pix' % (circles[0][0][0], circles[0][0][1], circles[0][0][2]))
            print('set the reference coordinate as (x,y) = (%.2f, %.2f)' % (circles[0][0][0], circles[0][0][1]))
            os.system("echo '   center: matched: %.2f, %.2f' >> %s" % (xref,yref,log))
            os.system("echo '   radius: matched: %.2f pix' >> %s" % (radius,log))

            #画像書き出し。
            fig = plt.figure()
            ax = plt.axes()
            plt.imshow(gray,cmap = 'gray')
            c = patches.Circle(xy=(xref,yref), radius=radius, fill = False, ec='r')
            ax.add_patch(c)
            plt.xlim(int(xref)-radius*1.5, int(xref)+radius*1.5)
            plt.ylim(int(yref)-radius*1.5, int(yref)+radius*1.5)
            ax.axis("off")
            plt.savefig(outdir + 'log/detected_circle.png', dpi = 300)

        else: #誤検出の場合。
            print("error!!")
            print("Matched multiple circles!")
            print("Please adjust parameters!")
            sys.exit()
    else: #そもそも円が検出されない場合。
        print("error!!")
        print("no circle is detected")
        print("Please adjust parameters or set the reference coordinate!")
        sys.exit()

    return xref, yref
