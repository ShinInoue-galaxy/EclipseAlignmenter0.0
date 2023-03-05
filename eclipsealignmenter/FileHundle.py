#ファイルopen 書き出しなどに使用。
#last update: 2023/3/3
import re
import numpy as np
import cv2
import os
import sys

#出力dirの設定。例外処理
def outdir_setting(
    outdir,         #outputする
    file_list       #file list 指定しない場合はこの下に作るため。
    ):
    if outdir:  #指定する場合。
        if type(outdir) != str:  #正しく指定されていない場合。
            print('error!!')
            print("'outdir' must be str")
            sys.exit()
        else:
            if outdir[-1] != '/':
                outdir = outdir + '/'
            if outdir[0] =='/':  #絶対PATHなら。
                print("Output images are written in '%s'" % outdir)
            else:  #相対PATHなら
                print("Output images are written in './%s'" % outdir)
    else:  #特に指定しない場合。
        outdir = os.path.dirname(file_list) +'/aligned/'
        print("Output images are written in '%s'" % outdir)

    #ディレクトリの作成
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        print('mkdir %s' % outdir)
    #ログdirの作成
    if not os.path.exists(outdir+'log/'):
        os.makedirs(outdir+'log')
        print('mkdir %s' % outdir+'log/')
    print()
    return outdir

#ファイルを開く。 中心座標を指定した場合に、それも読み込む。
def openfile_with_coord(
    fline,           #ファイルline fname (+ coord)
    file_dir,        #ファイルが存在するディレクトリ
    showtext = True  #文字出力をするかどうか。
):
    #座標が指定されているかどうかを確認 必ず二つ与えられていることを確認。
    r = re.match(r'(.+) (\d+\.*\d*) (\d+\.*\d*)',fline.rstrip('\n'))
    #座標が一つの場合はエラー
    s = re.match(r'(.+) (\d+\.*\d*)',fline.rstrip('\n'))

    #input fileの読み込み
    if r:  #座標が与えられている場合。
        filename = file_dir + r.group(1)
        #中心座標を代入
        xcen = float(r.group(2))
        ycen = float(r.group(3))
        if showtext:
            print('Reference coordinate is given.')
            print('Use coordinate (x,y) = (%.2f, %.2f)' % (xcen, ycen))
            print()
    elif s:
        print("error!!")
        print("please specify two values as coordinate")
        sys.exit()
    else:  #座標が与えられていない場合。
        filename = file_dir + fline.rstrip('\n')
        xcen = False
        ycen = False

    return filename, xcen, ycen


#保存
def save_image(
    R,             #画像R
    G,             #画像G
    B,             #画像B
    savename,      #保存名
    center,        #天体中心座標
    displacement,  #画像の位置ずれ (基準画像に対する)
    boxsize,       #clipする場合。
    resampling     #小数点以下で位置をずらしてresampleするかどうか。
):
    if boxsize:  #clipする場合
        if resampling:  #画像の位置をずらして書き出す場合
            #shift and resampling
            print('shifting and resampling...')
            R = image_shift(R, displacement[0], displacement[1])
            G = image_shift(G, displacement[0], displacement[1])
            B = image_shift(B, displacement[0], displacement[1])
            print('finished!')
            #need reference center
            center = np.array(center) - np.array(displacement)
        #clip
        R = R[int(np.round(center[1]))-int(boxsize[1]/2):int(np.round(center[1]))+int(boxsize[1]/2), int(np.round(center[0]))-int(boxsize[0]/2):int(np.round(center[0]))+int(boxsize[0]/2)]
        G = G[int(np.round(center[1]))-int(boxsize[1]/2):int(np.round(center[1]))+int(boxsize[1]/2), int(np.round(center[0]))-int(boxsize[0]/2):int(np.round(center[0]))+int(boxsize[0]/2)]
        B = B[int(np.round(center[1]))-int(boxsize[1]/2):int(np.round(center[1]))+int(boxsize[1]/2), int(np.round(center[0]))-int(boxsize[0]/2):int(np.round(center[0]))+int(boxsize[0]/2)]
    else: #clipしない場合
        #resampleが必要
        print('shifting and resampling...')
        if resampling:
            R = image_shift(R, displacement[0], displacement[1])
            G = image_shift(G, displacement[0], displacement[1])
            B = image_shift(B, displacement[0], displacement[1])
        else:
            R = image_shift(R, np.round(displacement[0]), np.round(displacement[1]))
            G = image_shift(G, np.round(displacement[0]), np.round(displacement[1]))
            B = image_shift(B, np.round(displacement[0]), np.round(displacement[1]))
        print('finished!')

    img = np.stack([B,G,R])
    img = np.transpose(img,axes=[1,2,0])
    cv2.imwrite(savename, img, [cv2.IMWRITE_JPEG_QUALITY, 100])
    print('saved: %s' % savename)
    print()
#画像shift
def image_shift(
    image,        #画像　(単色)
    dx,           #x座標ずれ
    dy            #y座標ずれ
):
    return np.roll(image, (-int(dy), -int(dx)), axis=(0, 1))
