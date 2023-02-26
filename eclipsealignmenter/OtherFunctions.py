#その他関数
#last update: 2022/2/6

#1 clipしない
#2 指定した大きさでclip
#3 円の半径に対する相対値でclip
def set_boxsize(boxsize, radius):
    if not boxsize: #パターン1 when [], None, False, ''など
        boxsize = None
    else: #パターン2, 3
        if type(boxsize) == list: #listで与えている場合。
            if len(boxsize) == 1:
                box_x = boxsize[0]
                box_y = boxsize[0]
            elif len(boxsize) == 2:
                box_x = boxsize[0]
                box_y = boxsize[1]
            else:
                print('3 or more values are given')
                print('use the first two values')
                box_x = boxsize[0]
                box_y = boxsize[1]
        elif (type(boxsize) == int) | (type(boxsize) == float): #数値を与えている時
            box_x = boxsize
            box_y = boxsize
        else: #そもそも値が正しくない時。
            print('invalid value is specified as boxsize')
            sys.exit()
        #円の半径との相対値
        if radius: #円の半径がわかっている場合は、box sizeと比較
            if (radius*2 > box_x) | (radius*2 > box_y): #円半径が大きい場合、つまり比で与えている場合。
                box_x = int(2 * box_x * radius)
                box_y = int(2 * box_y * radius)
            else:
                 box_x = int(box_x)
                 box_y = int(box_y)
        else:
             box_x = int(box_x)
             box_y = int(box_y)
        boxsize = [box_x, box_y]
        print('images are clipped as %d * %d' % (boxsize[0], boxsize[1]))
    return boxsize
