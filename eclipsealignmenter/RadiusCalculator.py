#円半径の推測に使用
#last update: 2023/2/26
import os
import numpy as np
import cv2

def calculate_radius(
    circle_radius_image, #半径を計算するための画像
    outdir, # 出力先dir
    nsigma, #マスク作成閾値
    npixels #マスク最小pix数
):
    from photutils.segmentation import make_source_mask
    ext = os.path.splitext(circle_radius_image)[-1] #画像のextension
    mask_name = outdir + 'log/' + os.path.basename(circle_radius_image).replace(ext, '_surface_mask' + ext) #output mask画像の出力名
    print('calculate the radius of the circle with %s ' % circle_radius_image)

    #画像の読み込み
    img = cv2.imread(circle_radius_image)[:, :, [2, 1, 0]]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #モノクロ画像に変換。
    mask = make_source_mask(gray, nsigma=nsigma, npixels=npixels, dilate_size=1) #マスクを作成。

    """===============マスクしきれなかった円の内部を塗りつぶし (参考: https://tpsxai.com/opencv_fill_hole/)============="""
    intmask = np.zeros(mask.shape)
    intmask[mask]=255
    ret, region = cv2.threshold(intmask, 1, 255,cv2.THRESH_BINARY)

    #輪郭データの取得
    contours,_ = cv2.findContours(np.array(region,dtype="uint8"), method = cv2.CHAIN_APPROX_NONE, mode = cv2.RETR_LIST)

    #塗りつぶし多角形を描写するためのゼロ埋め配列定義
    #point:opencvの関数で扱えるように型をuint8で指定！
    zero_img = np.zeros([region.shape[0], region.shape[1]], dtype="uint8")

    #全ての輪郭座標配列を使って塗りつぶし多角形を描写
    for p in contours:
        cv2.fillPoly(zero_img, [p], (255, 255, 255))
    mask = np.zeros(zero_img.shape)
    mask[zero_img>0] = 1
    """=========================================================================================================="""

    #面積計算
    surface = np.sum(mask)
    r = np.sqrt(surface/np.pi)
    print('radius of the circle is %.2f pix' %r )
    cv2.imwrite(mask_name, zero_img, [cv2.IMWRITE_JPEG_QUALITY, 100])
    print('saved mask image: %s ' % mask_name)
    print()

    return r
