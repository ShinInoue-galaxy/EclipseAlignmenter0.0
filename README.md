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

# License
Copyright (c) 2023 Shin Inoue
The source code is licensed under the BSD License, see LICENSE.
