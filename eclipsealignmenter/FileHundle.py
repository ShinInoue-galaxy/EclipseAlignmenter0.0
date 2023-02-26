#ファイルopen 書き出しなどに使用。
#last update: 2023/2/26
import re
import numpy as np
import cv2

#ファイルを開く。 中心座標を指定した場合は、それも読み込む。
def openfile_with_coord(
    fline, #ファイルline fname (+ coord)
    file_dir, #ファイルが存在するディレクトリ
):
    #座標が指定されているかどうかを確認
    r = re.match(r'(.+) (\d+\.*\d*) (\d+\.*\d*)',fline.rstrip('\n')) #座標が与えられているかどうかを確認

    #input fileの読み込み
    if r: #座標が与えられている場合。
        filename = file_dir + r.group(1)
        xcen = float(r.group(2)) #一致した場合、代入
        ycen = float(r.group(3))
        print('Reference coordinate is given.')
        print('Use coordinate (x,y) = (%.2f, %.2f)' % (xcen, ycen))
        print()
    else: #座標が与えられていない場合。
        filename = file_dir + fline.rstrip('\n')
        xcen = False
        ycen = False

    return filename, xcen, ycen


#保存
def save_image(
    R, #画像R
    G, #画像G
    B, #画像B
    savename, #保存名
    center, #画像中心
    displacement, #画像の位置ずれ
    boxsize, #clipする場合。
    resampling #位置をずらしてresampleするかどうか。
):
    if boxsize: #clipする場合
        if resampling: #画像の位置をずらして書き出す場合
            #resampling
            print('shifting and resampling...')
            R = image_shift(R, displacement[0], displacement[1])
            G = image_shift(G, displacement[0], displacement[1])
            B = image_shift(B, displacement[0], displacement[1])
            print('finished!')
            center = np.array(center) - np.array(displacement) #need reference center

        R = R[int(np.round(center[1]))-int(boxsize[1]/2):int(np.round(center[1]))+int(boxsize[1]/2), int(np.round(center[0]))-int(boxsize[0]/2):int(np.round(center[0]))+int(boxsize[0]/2)]
        G = G[int(np.round(center[1]))-int(boxsize[1]/2):int(np.round(center[1]))+int(boxsize[1]/2), int(np.round(center[0]))-int(boxsize[0]/2):int(np.round(center[0]))+int(boxsize[0]/2)]
        B = B[int(np.round(center[1]))-int(boxsize[1]/2):int(np.round(center[1]))+int(boxsize[1]/2), int(np.round(center[0]))-int(boxsize[0]/2):int(np.round(center[0]))+int(boxsize[0]/2)]
    else: #clipしない場合
        #resampleが必要
        print('shifting and resampling...')
        R = image_shift(R, displacement[0], displacement[1])
        G = image_shift(G, displacement[0], displacement[1])
        B = image_shift(B, displacement[0], displacement[1])
        print('finished!')

    img = np.stack([B,G,R])
    img = np.transpose(img,axes=[1,2,0])
    cv2.imwrite(savename, img, [cv2.IMWRITE_JPEG_QUALITY, 100])
    print('saved: %s' % savename)
    print()

def image_shift(image, dx, dy): #画像shift
    return np.roll(image, (-int(dy), -int(dx)), axis=(0, 1))
