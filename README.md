# EclipseAlignmenter
時間変化する月食・日食画像を自動で"大体"位置合わせするコードです。  

# REQUIREMENTS
python 3.9  
matplotlib 3.5.3  
numpy 1.23.2  
photutils 1.5.0  
image-registration 0.2.6  
opencv-contrib-python 4.6.0.66  

# Core Algorithm
位置合わせは、[astronomical image registration](https://image-registration.readthedocs.io/en/latest/index.html)の[cross_correlation_shifts](https://image-registration.readthedocs.io/en/latest/image_registration.html#module-image_registration.cross_correlation_shifts)を用いて行っています。  
これは画像の相互相関関数を計算することで、二枚の画像のずれ量を計算してくれるというものです。  
画像の位置合わせそのものは、このモジュールだけで完結します。   
それを組み込んで、時間変化して欠け方の変わる食画像の位置合わせを、できるだけ簡単に半自動的に行えるようにしました。

# Usage
使い方の詳細はwikiを参照。  
必要な画像ファイルを用意して、[EclipseAlignmenter.py](https://github.com/ShinInoue-galaxy/EclipseAlignmenter0.0/blob/main/EclipseAlignmenter.py)の`parameters`の`required`で設定します。必要に応じてoptionも編集します。  
一枚目の画像を基準に、位置合わせを行った画像が書き出されます。

- 画像ファイルの指定
```
file_list      = 'Sample/list.list'
```
のように、位置合わせをする画像を並べたリスト`list.list`を指定します。リストの書き方はこちら。

- 書き出しサイズの指定。
```
boxsize        = []
```
で書き出す画像のサイズを指定します。何も指定しない場合は、画像をシフトして、入力画像と同じサイズで書き出します。
```
boxsize        = [1.5,1.5]
```
のように、書き出す画像の縦横のサイズを指定することができます。2以下の値を与えた場合、天体の直径にその値をかけた大きさで、2以上の値を与えた場合、与えた大きさで天体の円中心を基準に画像をclipした画像を書き出します。(画像の解像度はそのままで、トリミングされる。）  
このために天体の中心座標が必要となります。
```
circle_radius_image = 'Sample/IMG_0123.jpg'
```
などと、`circle_radius_image`に欠けていない天体の画像を指定してください。この画像から円の半径を計算し、基準画像に対して、そのような半径を持つ円の中心を自動的に検出します。
(`circle_radius_image` で指定した画像の、中心座標が検出されるわけではない。)
画像を使わずに、直接天体の座標を指定することもできます。詳細はwikiを参照してください。

- 実行と書き出し
```
$ python3 EclipseAlignmenter.py
```
とコマンドラインからスクリプトを実行してください。入力画像が入っているディレクトリ下に`aligned/`というディレクトリが作成され、その中に位置合わせした画像が書き出されます。

他にもいくつかオプションを設定しています。詳細はwikiをご覧ください。

# License
Copyright (c) 2023 Shin Inoue
The source code is licensed under the BSD License, see LICENSE.
