#入力パラメーターの、check 例外処理。
#last update: 2023/3/5
import os
import sys
from eclipsealignmenter import FileHundle

#file_listのチェックを行う。
def check_filelist(
    file_list      #ファイルリスト
    ):
    if not file_list: #正しくpathを設定しているかどうか。
        print('error!!')
        print("'file_list' is not specified")
        print('please set the path of the file list')
        sys.exit()
    elif type(file_list) != str: #file_listが適切か (strか)
        print('error!!')
        print("'file_list' must be str")
        sys.exit()
    elif not os.path.exists(file_list): #file listに入っている画像が、存在するかどうか。
        print('error!!')
        print('no such file as %s is exist.' % file_list)
        print('please set the correct path of the file list')
        sys.exit()
    else: #リストに含まれている画像が存在するかをcheck
        f = open(file_list,'r')
        for fline in f:
            filename, xcen, ycen = FileHundle.openfile_with_coord( fline, os.path.dirname(file_list)+'/')
            if not os.path.exists(filename):
                print('error!!')
                print("no such image as '%s' is exist." % filename)
                print('please set the correct image and/or coordinates  in file_list')
                sys.exit()
        f.close()

def check_suffix(
    suffix      #suffix
):
    if not suffix:
        suffix = '_aligned'
    elif type(suffix) != str:
        print('error!!')
        print("'suffix' must be str")
        sys.exit()
    else:
        if suffix[0] != '_':
            suffix = '_' + suffix
    return suffix

def check_out_extension(out_image_type):
    if out_image_type:
        if type(out_image_type) != str:
            print('error!!')
            print("'out_image_type' must be str")
            sys.exit()
        elif out_image_type[0] != '.':
            out_image_type = '.' + out_image_type
    return out_image_type
