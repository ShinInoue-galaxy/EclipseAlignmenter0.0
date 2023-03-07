#時間変動する食画像の位置合わせ。
#last update 2023/3/5

"""============parameters=============="""
#================required=================
#str: 実行するファイルのリスト 中身の形式はwikiを参照
file_list      = 'Sample/list.list'

#================option=================== (適切な組み合わせで指定する必要がある。詳しくはwikiを参照)
# str, default:_aligned. outputにつけられるsuffix
suffix         = ''

# int/float or [int/float(x), int/float(y)], default:None, 書き出す画像の大きさ。(wikiを参照)
boxsize        = [1.5]

# str, default:dir of file_list/aligned/ 書き出す画像のディレクトリ。 画像は上書き
outdir         = ''

# str, default:original,  書き出す画像の拡張子。 ex: out_image_type = '.tiff' デフォルトは入力画像と同じ拡張子
out_image_type = ''

#円半径の推定パラメータ、photutilsが必要 (wikiを参照)、Hough 変換や画像のclipに使用
# str, default:None, 欠けていない画像を指定。画像から円の半径を推定。 上書きされる。
circle_radius_image = 'Sample/IMG_0123.jpg' 

# int/float, default: None, 円の半径。circle_radius_image によって円の半径を計算した場合は上書き。
radius     = None

# bool, default: False, 画像を小数点以下の精度でシフトするかどうか(wikiを参照)
resampling = False

## ================parameter tuning===============
# 基本的には触らない。うまくいかない時だけ変える
# 例外処理不十分 必ず正しいtypeの値を入れること。
# int/float, defalult: 10, 月検出の閾値。月以外のsourceも検出される場合は、大きい値を、月が円として検出されない場合は、小さい値(>3を推奨)を入れる。
nsigma = None
# int, default: 500, nsigma 以上の値をもち、npixels以上連続しているsourceを月と判定する。画面に対する月、星の大きさに合わせ、　星のpix < npixels <月のpixとなる値を設定。
npixels = None

#Hough parameters　(wiki参照)
#初期画像の基準座標を与えない場合、Hough変換により、基準画像の円を検出して、その中心座標を基準に画像をclipする。
#画像をclipしない場合は不要。
#うまく検出できない場合はパラメータ調整が必要。
# int, default: 5, 円検出のパラメータ。値が大きいほど検出基準が緩くなる。
dp            = None
# int, default: 60, 円中心検出の閾値。低い値にすると円の誤検出が多くなるとのこと。
param2        = None


"""===============*********** main do not edit *************==============="""
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
import eclipsealignmenter.CheckParameters

"""======デフォルト値の適用、パラメータチェック======"""
#時間計測
starttime = time.time()

#file_listが入力されているかどうか。妥当なファイルリストかどうかの確認。
eclipsealignmenter.CheckParameters.check_filelist(file_list)

#suffixの判定および、例外処理。
suffix = eclipsealignmenter.CheckParameters.check_suffix(suffix)

#出力画像の形式指定。例外処理。
out_image_type = eclipsealignmenter.CheckParameters.check_out_extension(out_image_type)

#resampling
if type(resampling) != bool:
    print("error!!")
    print("'esampling' must be 'True' or 'False'")
    sys.exit()

#出力ディレクトリ作成
outdir = eclipsealignmenter.FileHundle.outdir_setting(outdir, file_list)
log = outdir + 'log/center_coordinate.log'
print('center pixels (and radius) are written in %s' % log)
print()

"""==円半径計算パラメータデフォルト値=="""
if circle_radius_image:
    if not nsigma:
        nsigma = 10
    if not npixels:
        npixels = 500

"""==Hough変換パラメータ=="""
if not dp:
    dp = 5
if not param2:
    pram2 = 60

#coordinate clip radiusの処理
#boxsize がoffの場合は、半径も座標も必要ない。
if boxsize: #clipする場合、
    #中心座標が耐えられているか、あるいは必要なパラメータ(半径)が指定されているか
    radius, radius_calculated = eclipsealignmenter.CheckParameters.check_coordinate_of_the_firstimage(file_list, radius, circle_radius_image, outdir, nsigma, npixels, log)
    #boxsizeの取得
    boxsize = eclipsealignmenter.OtherFunctions.set_boxsize(boxsize, radius, circle_radius_image, outdir, nsigma, npixels, log, radius_calculated)

#全ファイル数の取得
f = open(file_list,'r')
length = 0
for fline in f:
    length+=1
f.close()

#位置合わせして書き出し。
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

     #log 出力
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
            if boxsize: #基準が必要でない場合は計算しない
                print('no corrdinate is given')
                print('matching a circle to input image with Hough transformation')
                xref,yref = eclipsealignmenter.HoughCircleEstimator.estimate_hough_circle(gray, dp, radius, param2, outdir, log)
            else:
                xref = False
                yref = False
        eclipsealignmenter.FileHundle.save_image(R, G, B, savename, [xref, yref], [0,0], boxsize, resampling) #位置をずらしてresampleするかどうか。)
        reference = True
        if not boxsize:
            xcent_ref, ycent_ref = eclipsealignmenter.OtherFunctions.image_mom1(gray)


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
                #中心座標を0<xcen<shape, 0<ycen<shapeに納める
                if (xcen < 0) | (gray.shape[1] <= xcen):
                    dispx_tmp = -1. * (gray.shape[1] - abs(displacement[0])) * displacement[0]/abs(displacement[0])
                    dispx     = dispx - displacement[0] + dispx_tmp
                    xcen      = xref + dispx

                if (ycen < 0) | (gray.shape[0] <= ycen):
                    dispy_tmp = -1 * (gray.shape[0] - abs(displacement[1])) * displacement[1]/abs(displacement[1])
                    dispy     = dispy - displacement[1] + dispy_tmp
                    ycen      = yref + dispy

                print('matched center is (x,y) = (%.2f, %.2f)' % (xcen, ycen))
                os.system("echo '   center: calculated: %.2f, %.2f' >> %s" % (xcen,ycen,log))
            else:
                #画像の重心から判定する。
                xcent, ycent = eclipsealignmenter.OtherFunctions.image_mom1(gray)
                #ズレを素直な方向に修正する
                if (xcent - xcent_ref) * displacement[0] < 0:
                    dispx_tmp = -1. * (gray.shape[1] - abs(displacement[0])) * displacement[0]/abs(displacement[0])
                    dispx     = dispx - displacement[0] + dispx_tmp
                if (ycent - ycent_ref) * displacement[1] < 0:
                    dispy_tmp = -1 * (gray.shape[0] - abs(displacement[1])) * displacement[1]/abs(displacement[1])
                    dispy     = dispy - displacement[1] + dispy_tmp
                xcent_ref = xcent
                ycent_ref = ycent
                os.system("echo '   displacement: %.2f, %.2f' >> %s" % (dispx,dispy,log))
        eclipsealignmenter.FileHundle.save_image(R, G, B, savename, [xcen, ycen], [dispx,dispy], boxsize, resampling) #位置をずらしてresampleするかどうか。)

    i += 1
    ref_image = gray

endtime = time.time()
print ('all process has been finished. (%.2f min)' % ((endtime - starttime)/60.))
