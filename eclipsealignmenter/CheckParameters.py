#入力パラメーターの、check 例外処理。
#last update: 2023/3/5
import os
import sys
from eclipsealignmenter import FileHundle
from eclipsealignmenter import RadiusCalculator

#file_listのチェックを行う。
def check_filelist(
    file_list      #ファイルリスト
    ):
    if not file_list:  #正しくpathを設定しているかどうか。
        print('error!!')
        print("'file_list' is not specified")
        print('set the path of the file list')
        sys.exit()
    elif type(file_list) != str:  #file_listが適切か (strか)
        print('error!!')
        print("'file_list' must be str")
        sys.exit()
    elif not os.path.exists(file_list):  #file listに入っている画像が、存在するかどうか。
        print('error!!')
        print('no such file as %s is exist.' % file_list)
        print('set the correct path of the file list')
        sys.exit()
    else:  #リストに含まれている画像が存在するかをcheck
        f = open(file_list,'r')
        for fline in f:
            filename, xcen, ycen = FileHundle.openfile_with_coord( fline, os.path.dirname(file_list)+'/', showtext = False)
            if not os.path.exists(filename):
                print('error!!')
                print("no such image as '%s' is exist." % filename)
                print('set the correct image and/or coordinates  in file_list')
                sys.exit()
        f.close()

def check_suffix(
    suffix     #suffix
):
    if suffix:  #suffixを与えている時
        if type(suffix) != str:  #strでないとき
            print('error!!')
            print("'suffix' must be str")
            sys.exit()
        else:
            if suffix[0] != '_':  #_をつける
                suffix = '_' + suffix
    else:
        suffix = '_aligned'  #デフォルト
    return suffix

def check_out_extension(
    out_image_type      #extensionのチェック
):
    if out_image_type:  #与えている時
        if type(out_image_type) != str:  #strでない時
            print('error!!')
            print("'out_image_type' must be str")
            sys.exit()
        elif out_image_type[0] != '.':  #. をつける
            out_image_type = '.' + out_image_type
    return out_image_type

#一枚目基準画像の、座標あるいは座標推定に必要なパラメータが与えられているかを確認。
def check_coordinate_of_the_firstimage(
    file_list,                   #入力file list
    radius,                      #半径
    circle_radius_image,         #半径探索画像
    outdir,                      #outputdir
    nsigma,                      #半径探索のパラメータ
    npixels,                     #半径探索のパラメータ
    log                          #ログ
    ):
    radius_calculated = False
    f = open(file_list,'r')
    for fline in f:  #一枚目の画像に座標が与えられているかどうかを確認
        filename, xcen, ycen = FileHundle.openfile_with_coord( fline, os.path.dirname(file_list)+'/', showtext = False)
        break
    if not xcen:   #座標が与えられていない場合。→Hough変換に渡す半径が必要。
        #画像が与えらてている場合は、強制的に上書き。
        if circle_radius_image:
            if type(circle_radius_image) != str:  #strでない時
                print('error!!')
                print("'circle_radius_image' must be str")
                sys.exit()
            elif not os.path.exists(circle_radius_image):  #ファイルが存在しないとき
                print("error!")
                print("no such file as '%s' is exists" % circle_radius_image)
                sys.exit()
            else:
                radius = RadiusCalculator.calculate_radius(circle_radius_image, outdir, nsigma, npixels)
                radius_calculated = True
                os.system("echo 'calculated radius is %.2f pix' > %s" % (radius,log))
                os.system("echo '' > %s" % (log))
        elif not radius:  #半径が与えられていない場合何か半径を求める方法が必要になる。
            print('error!!')
            print("center coordinate of the first image is needed")
            print("specify center coordinate of the first image")
            print("or")
            print("specify 'radius' to calculate the center coordinate of the first image")
            print("or")
            print("specify 'circle_radius_image' to calculate the radius to get the center coordinate")
            sys.exit()
        elif (type(radius)!=int) & (type(radius)!=float):  #与えられている場合におかしい場合。
            print('error!!')
            print("'radius must be int or float'")
            sys.exit()
    return radius, radius_calculated
