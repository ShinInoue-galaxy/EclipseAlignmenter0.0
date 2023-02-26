#時間変動する食画像を位置合わせする。
#last update 2023/2/26

"""============parameters=============="""
#required
file_list      = '/Volumes/2TB_HDD/音楽以外/天体処理済み/完全処理済み/2022/月食1108/月食60c/full_images_jpg/list.list' #str, required: 実行するファイルのリスト
#optional
suffix         = '' #str, option: outputにつけられるsuffix 指定しない場合は input_aligned.jpg などと '_aliged' がつく
# 円の半径より小さい場合は、factorとみなし、円の半径*factorとする
boxsize        = [1.2] #int or [int(x), int(y)], option: 書き出す画像のサイズ。 指定しない場合は、一枚目の画像に対して位置合わせ。clipせず書き出し。
outdir         = 'aligned_clipped_test' #str, option: 書き出す画像のディレクトリ。 絶対パスまたは、スクリプト実行dirからの相対パス。指定しない場合は、file_listが存在するディレクトリ下にaligned/を作成 #画像は上書き。。
out_image_type = '' #str, option: 出力する画像のタイプ。拡張子で指定。 ex: out_image_type = '.tiff'。指定しない場合は、入力画像と同じ拡張子
resampling = False #bool,
#円半径の推定。
#これを使用する場合、photutilsが必要になります。
circle_radius_image = '/Volumes/2TB_HDD/音楽以外/天体処理済み/完全処理済み/2022/月食1108/月食60c/full_images_jpg/IMG_0369.jpg'  #str, default: '', 円半径を推定するのに使う画像。 欠けていない画像を入力。指定した場合、面積から円の半径を求め、基準画像での円半径の制限に使用。
nsigma = None #int/float, defalult: 10, 標準偏差の何倍以上をsourceとするか。
npixels = None #int, redault: 500, これ以下のnpixelsであるsourceはノイズあるいは星としてmaskから除去。 星よりも大きく、月よりも小さい値を指定。

#Hough parameters
#初期画像の基準座標を与えない場合、Hough変換により、基準画像の円を検出する。
#パラメータ調整が必要。
dp            = 5                   #円検出のパラメータ。値が大きいほど検出基準が緩くなる。
minDist       = 500            #隣接する円の最短距離。月画像について適用する場合、月の半径より十分大きく取る。
param2        = 60              #円中心検出の閾値。低い値にすると円の誤検出が多くなるとのこと。
radius     = None  #int/float, defalult: None, 円検出の際の半径 circle_radius_imageが与えられている場合、そちらの値で上書き。


"""========================main======================="""
"""========================dont edit======================="""
#module import
import cv2
import numpy as np
import os
import re
import sys
import time
import image_registration as im_regi
import eclipsealignmenter.RadiusCalculator
import eclipsealignmenter.FileHundle
import eclipsealignmenter.HoughCircleEstimator
import eclipsealignmenter.OtherFunctions



"""======デフォルト値の適用======"""
#file_listが入力されているかどうか。
if not file_list:
    print('please set the path of the file list')
    sys.exit()
#file_listが適切か
elif type(file_list) != str:
    print('"file_list must be str"')
    sys.exit()
#suffixの判定および、例外処理。
if not suffix:
    suffix = '_aligned'
else:
    if suffix[0] != '_':
        suffix = '_' + suffix
#出力画像の形式指定。例外処理。
if out_image_type:
    if out_image_type[0] != '.':
        out_image_type = '.' + out_image_type

"""==円半径計算パラメータデフォルト値=="""
if circle_radius_image:
    if not nsigma:
        nsigma = 10
    if not npixels:
        npixels = 500

#時間計測
starttime = time.time()


"""出力ディレクトリ作成。"""
if outdir == '':#デフォルト
    outdir = os.path.dirname(file_list) +'/aligned/'
    print("Output images are written in '%s'" % outdir)
else:
    #/がついていなければつける。
    r = re.match(r'.+/',outdir)
    if not r:
        outdir = outdir + '/'
    if outdir =='/':#絶対PATHなら。
        print("Output images are written in '%s'" % outdir)
    else: #相対PATHなら
        print("Output images are written in './%s'" % outdir)
if not os.path.exists(outdir):
    os.makedirs(outdir)
    print('mkdir %s' % outdir)
if not os.path.exists(outdir+'log/'):
    os.makedirs(outdir+'log')
    print('mkdir %s' % outdir+'log/')
print()

log = outdir + 'log/center_coordinate.log'
print('center pixels (and radius) are written in %s' % log)
print()

"""円半径の計算"""
if boxsize: #clipする場合
    if circle_radius_image:
        #計算して半径を取得。
        #上書き。
        radius = eclipsealignmenter.RadiusCalculator.calculate_radius(circle_radius_image, outdir, nsigma, npixels)
        os.system("echo 'calculated radius is %.2f pix' > %s" % (radius,log))
        os.system("echo '' > %s" % (log))

"""===boxsize決定==="""
boxsize = eclipsealignmenter.OtherFunctions.set_boxsize(boxsize, radius)

#位置合わせして書き出し。

#全ファイル数の取得
f = open(file_list,'r')
length = 0
for fline in f:
    length+=1
f.close()

dispx     = 0 #ずれ初期値
dispy     = 0 #ずれ初期値
reference = False #reference 画像を計算したかどうかのflag

#一枚ずつ実行
f = open(file_list,'r')
i = 0
for fline in f:
    print('processing %d/%d ...' % (i+1, length)) #何枚目の処理かを出力
    #ファイル名、天体中心 (x,y) を取得 (座標を与えていない場合は、xcen, ycen = False)
    filename, xcen, ycen = eclipsealignmenter.FileHundle.openfile_with_coord( fline, os.path.dirname(file_list)+'/')

    #output画像の準備
    ext = os.path.splitext(filename)[-1] #画像のextension
    if out_image_type:
        savename = outdir+os.path.basename(filename).replace(ext,suffix+out_image_type)
    else:
        savename = outdir+os.path.basename(filename).replace(ext,suffix+ext)
    print('input image: %s' % filename)
    if circle_radius_image:
        if boxsize:
            os.system("echo '%s' >> %s" % (os.path.basename(filename),log))
        elif not reference:
            os.system("echo '%s' > %s" % (os.path.basename(filename),log)) #初期化
        else:
            os.system("echo '%s' >> %s" % (os.path.basename(filename),log))
    elif not reference:
        os.system("echo '%s' > %s" % (os.path.basename(filename),log)) #初期化
    else:
        os.system("echo '%s' >> %s" % (os.path.basename(filename),log))
    #画像open
    img = cv2.imread(filename)[:, :, [2, 1, 0]]
    R = img[:,:,0]
    G = img[:,:,1]
    B = img[:,:,2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #モノクロ画像に変換。
    #一枚目、基準画像の中心を求める。
    if not reference:
        if bool(xcen) & bool(ycen): #基準座標を与えている場合 その値を使用
            xref = xcen
            yref = ycen
            os.system("echo '   center: input: %.2f, %.2f' >> %s" % (xcen,ycen,log))
        else: #基準座標がない場合はHough変換で求める。
            #円検出で月を同定。
            if boxsize: #基準が必要でない場合は計算したくないので、
                print('no corrdinate is given')
                print('matching a circle to input image with Hough transformation')
                xref,yref = eclipsealignmenter.HoughCircleEstimator.estimate_hough_circle(gray, dp, radius, param2, outdir, log)
            else:
                xref = False
                yref = False
        eclipsealignmenter.FileHundle.save_image(R, G, B, savename, [xref, yref], [0,0], boxsize, resampling) #位置をずらしてresampleするかどうか。)
        reference = True

    else: #二枚目以降

        if bool(xcen) & bool(ycen): #基準座標を与えている場合
            dispx = xcen - xref
            dispy = ycen - yref
            os.system("echo '   center: input: %.2f, %.2f' >> %s" % (xcen,ycen,log))
        else: #基準座標がない場合、 相互相関関数を使って位置合わせ
            print('no coordinate is given')
            print('matching image ...')
            displacement = im_regi.cross_correlation_shifts(ref_image, gray) #displacementを計算
            dispx  += displacement[0]
            dispy  += displacement[1]
            if boxsize:
                xcen = xref + dispx
                ycen = yref + dispy
                print('matched center is (x,y) = (%.2f, %.2f)' % (xcen, ycen))
                os.system("echo '   center: calculated: %.2f, %.2f' >> %s" % (xcen,ycen,log))
            else:
                os.system("echo '   displacement: %.2f, %.2f' >> %s" % (dispx,dispy,log))
        eclipsealignmenter.FileHundle.save_image(R, G, B, savename, [xcen, ycen], [dispx,dispy], boxsize, resampling) #位置をずらしてresampleするかどうか。)

    i += 1
    ref_image = gray

endtime = time.time()
print ('all process has been finished. (%.2f min)' % ((endtime - starttime)/60.))
