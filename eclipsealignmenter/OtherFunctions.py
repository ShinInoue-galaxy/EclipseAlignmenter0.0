#その他関数
#last update: 2022/3/5
import sys
import os
from eclipsealignmenter import RadiusCalculator

#boxsizeを取得する関数
#1 clipしない
#2 指定した大きさでclip
#3 円の半径に対する相対値でclip
def set_boxsize(
    boxsize,              # 入力
    radius,               # 円の半径。(求めている場合)
    circle_radius_image,  #円半径を計算する画像
    outdir,               #出力dir
    nsigma,               #円半径の計算に使用
    npixels,              #円半径の計算に使用
    log,                  #log
    radius_calculated     #２回計算するのを防ぐ
    ):
    #パターン2, 3
    if type(boxsize) == list:   #listで与えている場合。
        if len(boxsize) == 1:
            box_x = boxsize[0]  #xyに変換
            box_y = boxsize[0]
        elif len(boxsize) == 2:
            box_x = boxsize[0]
            box_y = boxsize[1]
        else:  #３つ以上入力している場合は、最初の二つを取る。
            print('3 or more values are given')
            print('use the first two values')
            box_x = boxsize[0]
            box_y = boxsize[1]
    elif (type(boxsize) == int) | (type(boxsize) == float):  #配列ではなく、数値を与えている時
        box_x = boxsize
        box_y = boxsize
    else:  #そもそも値が正しくない時。
        print('invalid value is specified as boxsize')
        sys.exit()

    #円の半径の相対値で指定する場合。<2以下
    if (box_x < 2) | (box_y < 2):
        if circle_radius_image:  #円半径計算ようの画像を与えていて、
            if not radius_calculated:  #計算されていない場合、問答無用で計算。
                if type(circle_radius_image) != str:  #strでない
                    print('error!!')
                    print("'circle_radius_image' must be str")
                    sys.exit()
                elif not os.path.exists(circle_radius_image):  #ファイルが存在しない
                    print("error!")
                    print("no such file as '%s' is exists" % circle_radius_image)
                    sys.exit()
                else:
                    radius = RadiusCalculator.calculate_radius(circle_radius_image, outdir, nsigma, npixels)
                    os.system("echo 'calculated radius is %.2f pix' > %s" % (radius,log))
                    os.system("echo '' > %s" % (log))
        elif radius:  #半径が与えられていて、
            if (type(radius)!=int) & (type(radius)!=float):  #与えられている場合におかしい場合。
                print('error!!!')
                print("'radius must be int or float'")
                sys.exit()
        else:
            print('error!!')
            print("when boxsize < 2, 'radius' or 'circle_radius_image' must be specified ")
            sys.exit()
        box_x = int(2 * box_x * radius)
        box_y = int(2 * box_y * radius)
    else:  #絶対値の場合
         box_x = int(box_x)
         box_y = int(box_y)
    boxsize = [box_x, box_y]
    print('images are clipped as %d * %d' % (boxsize[0], boxsize[1]))

    return boxsize
