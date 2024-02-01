# ShunCar 制御基板用ファームウェア

ShunCarに搭載されている制御基板には、 [Raspberry Pi Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/) が使われています。

## ファームウェアの書き換え

1. バイナリの用意: [GitHub Releases](https://github.com/shunkei-jp/shuncar/releases) からダウンロードするか、ソースコードからビルドして、`.uf2`ファイルを準備してください。
2. Rasperry Pi Picoの接続: Rasperry Pi Picoの "BOOT" ボタンを押しながら、USBケーブルでPCと接続を行います。
    PCからは、USBストレージデバイスとして認識されます。
3. バイナリのコピー: 認識されたUSBストレージデバイスに `.uf2` ファイルをコピーすると、ファームウェアが書き込まれます。
4. ファイルをコピーすると、自動でエクスプローラ、もしくはFinderが閉じます。自動で閉じた場合更新完了です。

## ビルド

ソースコードからビルドを行う場合のビルド手順です。Ubuntu 22.02 (Standalone or WSL) でビルドができる事を確認しています。

### 依存ライブラリのインストール

CMakeやCコンパイラなどをインストールします。

```sh
sudo apt install cmake gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib
```

### pico-sdk のインストール

このファームウェアは [pico-sdk](https://github.com/raspberrypi/pico-sdk) を利用して作成されています。


1. pico-sdkリポジトリをcloneする
   - ```sh
     git clone https://github.com/raspberrypi/pico-sdk.git
     ```
2. `PICO_SDK_PATH` 環境変数を設定する
   - 以下を `.zshrc` や `.bashrc` に追記してください。
     ```sh
     export PICO_SDK_PATH=/path/to/pico-sdk
     ```

必要に応じて、 [pico-sdk](https://github.com/raspberrypi/pico-sdk) のREADME.mdを参照してください

### ビルド

`pico` ディレクトリの下に `build` ディレクトリを作成し、ビルドを行います。

```sh
cd pico
mkdir -p build && cd build
cmake ..
make
```

`build` ディレクトリ内に `main.uf2` が生成されます。

